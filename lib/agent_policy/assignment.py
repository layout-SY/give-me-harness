"""명시적 handoff 계약으로 동일 host·role의 Git 소유권을 이전한다."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

from .core import CENTRAL_ROOT, PolicyError, ProjectConfig, atomic_write
from .runtime import load_runtime


def handoff(project: ProjectConfig, source_id: str, target_id: str, handoff_file: Path,
            approved_sha256: str | None = None, state_root: Path | None = None) -> tuple[Path, str]:
    if source_id == target_id or any(re.fullmatch(r"[a-f0-9]{32}", value) is None for value in (source_id, target_id)):
        raise PolicyError("서로 다른 두 launcher assignment ID가 필요합니다.")
    raw = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=project.path,
                         text=True, capture_output=True, check=True).stdout.strip()
    common = (Path(raw) if Path(raw).is_absolute() else project.path / raw).resolve()
    repository = (state_root or CENTRAL_ROOT / "state").resolve() / "repositories" / hashlib.sha256(str(common).encode()).hexdigest()
    state = load_runtime("runtime_state")
    with state.locked(repository / "events.lock"):
        source_root = repository / "assignments" / source_id
        target_root = repository / "assignments" / target_id
        source = state.read(source_root / "assignment.json")
        target = state.read(target_root / "assignment.json")
        if not source or not target or any(record.get("repository") != str(common) or record.get("project") != project.id for record in (source, target)):
            raise PolicyError("handoff assignment의 저장소·프로젝트가 다릅니다.")
        if source.get("host") != target.get("host") or source.get("role") != target.get("role"):
            raise PolicyError("이 명령은 동일 host·role의 담당 세션만 교체합니다. host·role 변경에는 새 branch 계약이 필요합니다.")
        if state.read(source_root / "pending-binding.json") or any((source_root / "pending-bindings").glob("*.json")):
            raise PolicyError("source에 결과 미확인 도구 예약이 있습니다. 먼저 실행 결과를 복구하세요.")
        binding = state.read(source_root / "session-binding.json")
        task = binding.get("task") or source.get("task")
        if target.get("task") not in {None, "", task}:
            raise PolicyError("다른 독립 task의 assignment로 소유권을 이전할 수 없습니다.")
        expected = Path(binding.get("worktree") or source["worktree"]) / (binding.get("directory") or source["environment"]["ASAN_SESSION_DIR"]) / "handoff.md"
        if handoff_file.is_symlink() or handoff_file.resolve() != expected.resolve() or not handoff_file.is_file():
            raise PolicyError(f"source assignment의 handoff.md가 필요합니다: {expected}")
        content = handoff_file.read_bytes()
        if len(content.strip()) < 20:
            raise PolicyError("handoff에 현재 작업 상태와 다음 조치를 기록하세요.")
        claims = []
        for path in sorted((repository / "claims").glob("*.json")):
            claim = state.read(path)
            if claim.get("owner") == source_id and str(claim.get("resource", "")).startswith("git:"):
                claims.append({"file": path.name, "resource": claim["resource"]})
        integrations = []
        for path in sorted((common / "asan-agent-policy/integration-targets").glob("*.json")):
            value = state.read(path)
            if value.get("owner") == source_id:
                if target.get("responsibility") != "owner":
                    raise PolicyError("진행 중인 통합은 owner assignment에만 인계할 수 있습니다.")
                finish_digest = str(value.get("finish_sha256") or "")
                if re.fullmatch(r"[a-f0-9]{64}", finish_digest):
                    contract = state.read(common / "asan-agent-policy/finish-proposals" / f"{finish_digest}.json")
                    if "completion_authority" in contract:
                        raise PolicyError(
                            "진행 중인 부모 완료 계약은 실행 assignment가 고정되어 있습니다. "
                            "같은 assignment를 재개해 verify·close 또는 통합 복구를 완료한 뒤 인계하세요."
                        )
                integrations.append({"file": path.name, "record": value})
        plan = {"version": 1, "kind": "assignment-handoff", "source": source_id, "target": target_id,
                "repository": str(common), "task": task or "", "claims": claims, "integrations": integrations,
                "handoff_sha256": hashlib.sha256(content).hexdigest(), "binding": binding}
        payload = (json.dumps(plan, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
        digest = hashlib.sha256(payload).hexdigest()
        destination = repository / "handoffs" / f"{digest}.json"
        if approved_sha256 and re.fullmatch(r"[a-f0-9]{64}", approved_sha256):
            original = repository / "handoffs" / f"{approved_sha256}.json"
            transaction = state.read(original.with_suffix(".transaction.json"))
            if transaction and transaction.get("source") == source_id and transaction.get("target") == target_id:
                previous = original.read_bytes()
                if hashlib.sha256(previous).hexdigest() != approved_sha256:
                    raise PolicyError("handoff 복구 계약 파일이 손상되었습니다.")
                plan = json.loads(previous)
                if plan.get("handoff_sha256") != hashlib.sha256(content).hexdigest():
                    raise PolicyError("인계 중 handoff 내용이 변경되었습니다. 원래 내용을 확인하세요.")
                if transaction.get("state") == "complete":
                    return original, approved_sha256
                destination, digest = original, approved_sha256
                claims, integrations = plan["claims"], plan["integrations"]
        if source.get("handed_off_to") not in {None, target_id} or target.get("native_session"):
            raise PolicyError("source는 인계 전 상태, target은 아직 시작하지 않은 준비 assignment여야 합니다.")
        if approved_sha256 is None:
            atomic_write(destination, payload)
            return destination, digest
        if approved_sha256 != digest:
            raise PolicyError("승인 후 handoff·소유권 상태가 변경되었습니다. 새 계약을 확인하세요.")
        if not destination.exists():
            atomic_write(destination, payload)
        # 모든 대상의 현재 소유권을 다시 검증한 뒤 journal을 먼저 기록한다.
        for claim in claims:
            value = state.read(repository / "claims" / claim["file"])
            if value.get("owner") not in {source_id, target_id} or value.get("resource") != claim["resource"]:
                raise PolicyError("인계할 Git 소유권이 승인 계약과 다릅니다.")
        for integration in integrations:
            value = state.read(common / "asan-agent-policy/integration-targets" / integration["file"])
            if value.get("owner") not in {source_id, target_id} or value.get("finish_sha256") != integration["record"]["finish_sha256"]:
                raise PolicyError("인계할 통합 예약이 승인 계약과 다릅니다.")
        transaction_path = destination.with_suffix(".transaction.json")
        journal = {"state": "applying", "source": source_id, "target": target_id}
        state.write(transaction_path, journal)
        for claim in claims:
            state.write(repository / "claims" / claim["file"], {"resource": claim["resource"], "owner": target_id})
        for integration in integrations:
            value = dict(integration["record"])
            value["owner"] = target_id
            state.write(common / "asan-agent-policy/integration-targets" / integration["file"], value)
        target["task"] = task or ""
        if task:
            target["environment"]["ASAN_AGENT_POLICY_TASK"] = task
        source["handed_off_to"] = target_id
        state.write(source_root / "assignment.json", source)
        state.write(target_root / "assignment.json", target)
        journal["state"] = "complete"
        state.write(transaction_path, journal)
        return destination, digest
