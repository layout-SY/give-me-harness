"""Reproducible Git evidence for an agent's semantic integration review.

Evidence is not a declaration of semantic compatibility. Text conflicts,
contract risks, executed validations and unknowns remain separate report fields.
"""
from __future__ import annotations

import re
import os
import subprocess
import tempfile
import time
import uuid
from pathlib import Path
from types import ModuleType

_path = Path(__file__).with_name("runtime_loader.py")
_loader = ModuleType("review_loader")
_loader.__file__ = str(_path)
exec(compile(_path.read_bytes(), str(_path), "exec"), _loader.__dict__)
relations = _loader.load("branch_relations")
git, state = relations.git, relations.state
REPORT_FIELDS = ("comparisons", "text_conflicts", "contract_risks", "validation", "unknowns", "recommendation")


def current_participants(graph: dict, source: str, target: str) -> list[dict]:
    child, parent = relations.named(graph, source), relations.named(graph, target)
    if not child or not parent:
        raise RuntimeError("완료 검토 전에 source·target의 직접 부모 관계를 등록하세요.")
    # All siblings under exactly the same parent, recursively including their
    # ongoing children, and tombstones of previously completed siblings.
    selected = {parent["id"]: parent}
    for node in graph["nodes"].values():
        if node.get("parent") == parent["id"]:
            selected[node["id"]] = node
            selected.update({item["id"]: item for item in relations.descendants(graph, node["id"])})
    selected[child["id"]] = child
    return sorted(selected.values(), key=lambda node: node["id"])


def participants(graph: dict, source: str, target: str) -> list[dict]:
    selected = {node["id"]: node for node in current_participants(graph, source, target)}
    parent = relations.named(graph, target)
    for node in graph["nodes"].values():
        if any(item.get("target_id") == parent["id"] for item in node.get("integrations", [])):
            selected[node["id"]] = node
    return sorted(selected.values(), key=lambda node: node["id"])


def snapshot(root: Path, source: str, target: str) -> dict:
    graph = relations.read(root)
    current_ids = {node["id"] for node in current_participants(graph, source, target)}
    parent = relations.named(graph, target)
    result = {}
    for node in participants(graph, source, target):
        if node["id"] not in current_ids:
            result[node["id"]] = {"past_integrations": [item for item in node.get("integrations", []) if item.get("target_id") == parent["id"]]}
            continue
        result[node["id"]] = {"relation": node,
            "git": relations.node_snapshot(root, node) if not node.get("deleted") else None}
    return result


def diff(root: Path, base: str, tip: str) -> dict:
    result = git._git(root, "diff", "--find-renames", "--function-context", base, tip, "--", ".",
                      *(f":(exclude){prefix}**" for prefix in relations.config.ARTIFACT_SESSIONS_PREFIXES))
    if result.returncode:
        raise RuntimeError("비교 commit을 읽을 수 없습니다. 보존 ref와 Git 객체를 확인하세요.")
    return {"base": base, "tip": tip, "patch": result.stdout,
            "commits": git._output(root, "log", "--format=%H %s", base + ".." + tip)}


def text_preview(root: Path, source: str, target: str) -> dict:
    fast_forward = git.is_ancestor(root, target, source)
    if fast_forward:
        return {"ff_only_possible": True, "text_conflicts": False, "method": "ancestry"}
    # Keep merge-tree's preview objects outside the real repository. Evidence
    # collection precedes approval and must not modify its index, refs or objects.
    with tempfile.TemporaryDirectory(prefix="asan-merge-preview-") as objects:
        environment = dict(os.environ)
        environment["GIT_OBJECT_DIRECTORY"] = objects
        environment["GIT_ALTERNATE_OBJECT_DIRECTORIES"] = str(git.git_common_directory(root) / "objects")
        result = subprocess.run(["git", "merge-tree", "--write-tree", "--messages", target, source],
            cwd=root, env=environment, text=True, capture_output=True, timeout=30)
    if result.returncode in {0, 1}:
        return {"ff_only_possible": False, "text_conflicts": result.returncode == 1,
                "method": "merge-tree", "details": result.stdout}
    return {"ff_only_possible": False, "text_conflicts": None,
            "method": "unavailable", "details": result.stderr}


def references(root: Path, patches: list[str], worktrees: list[Path]) -> dict:
    tokens = sorted(set(re.findall(r"\b[A-Za-z_$][A-Za-z0-9_$]{3,}\b", "\n".join(patches))))
    tokens = [token for token in tokens if token not in {"const", "return", "function", "export", "import", "from", "diff", "index"}]
    selected = tokens[:160]
    result = {"symbols": selected, "symbol_limit_reached": len(tokens) > len(selected), "worktrees": {},
              "limits": "문자열 참조 후보입니다. 타입·props·상태·API 의미 분석은 에이전트가 별도로 수행합니다."}
    if not selected:
        return result
    pattern = "\\b(?:" + "|".join(re.escape(token) for token in selected) + ")\\b"
    for worktree in sorted(set(worktrees)):
        try:
            found = subprocess.run(["rg", "-n", "--no-heading", "--max-count", "20", "--glob", "!.git/**",
                "--glob", "!.*/*logs/**", "--glob", "!package-lock.json", "--glob", "!yarn.lock", pattern, "."],
                cwd=worktree, text=True, capture_output=True, timeout=15)
            result["worktrees"][str(worktree)] = {"matches": found.stdout[:120000],
                "truncated": len(found.stdout) > 120000, "status": found.returncode, "error": found.stderr}
        except (OSError, subprocess.TimeoutExpired) as error:
            result["worktrees"][str(worktree)] = {"unknown": str(error)}
    return result


def collect(root: Path, source: str, target: str, strategy: str, verification: list[str], cleanup: bool) -> dict:
    graph = relations.read(root)
    child, parent = relations.completion_check(root, graph, source, target)
    if strategy not in {"ff-only", "merge"} or not verification:
        raise RuntimeError("완료 전략(ff-only/merge)과 실행할 검증 명령을 명시하세요.")
    before = snapshot(root, source, target)
    evidence, patches, locations = {}, [], []
    current_ids = {node["id"] for node in current_participants(graph, source, target)}
    for node in participants(graph, source, target):
        active = node["id"] in current_ids
        resolution = node.get("resolution") or {}
        tip = (resolution.get("source_head") if node.get("deleted") else relations.require_live(root, node)) if active else None
        item = {"id": node["id"], "deleted": node.get("deleted", False), "resolution": resolution}
        item["past_integrations"] = []
        for integration in node.get("integrations", []):
            if integration.get("target_id") == parent["id"]:
                past = {"result": integration, "committed": diff(root, integration["fork_commit"], integration["source_head"])}
                item["past_integrations"].append(past)
                patches.append(past["committed"]["patch"])
        if tip:
            # For the parent, compare since this source's fork. This deliberately
            # includes direct parent commits and previously integrated siblings.
            item["committed"] = diff(root, child["fork_commit"] if node["id"] == parent["id"] else node["fork_commit"], tip)
            patches.append(item["committed"]["patch"])
        item["worktrees"] = {}
        for worktree in relations.branch_worktrees(root, node["name"]) if active and not node.get("deleted") else []:
            changes = relations.content_snapshot(worktree)
            changes["file_previews"] = {}
            for relative in changes["files"]:
                file = worktree / relative
                if file.is_file() and not file.is_symlink():
                    data = file.read_bytes()
                    changes["file_previews"][relative] = {"text": data[:80000].decode("utf-8", errors="replace"), "truncated": len(data) > 80000}
            item["worktrees"][str(worktree)] = changes
            patches.extend([changes["index"], changes["unstaged"]])
            locations.append(worktree)
        # Names may be reused; evidence keys include UUID in that case.
        key = node["name"] if node["name"] not in evidence else node["name"] + "@" + node["id"]
        evidence[key] = item
    result = {"version": 1, "id": uuid.uuid4().hex, "created_at": time.time(), "repository": str(git.git_common_directory(root)),
        "source": source, "target": target, "source_id": child["id"], "target_id": parent["id"],
        "source_head": relations.require_live(root, child), "target_head": relations.require_live(root, parent),
        "strategy": strategy, "verification": verification, "cleanup": cleanup, "snapshot": before,
        "generated_cleanup_roots": git.RUNTIME_CONTRACT["git"].get("integration", {}).get("generated_cleanup_roots", []),
        "participants": evidence, "text_preview": text_preview(root, relations.require_live(root, child), relations.require_live(root, parent)),
        "references": references(root, patches, locations), "semantic_status": "requires-agent-review"}
    if snapshot(root, source, target) != before:
        raise RuntimeError("비교 중 관련 변경이 바뀌었습니다. 현재 변경으로 검토를 다시 수집하세요.")
    result["evidence_digest"] = relations.digest(result)
    return result


def require_report(evidence: dict, report: dict) -> None:
    if not isinstance(report, dict):
        raise RuntimeError("검토 보고는 JSON 객체여야 합니다.")
    if report.get("evidence_digest") != evidence["evidence_digest"]:
        raise RuntimeError("에이전트 검토가 현재 비교 자료와 일치하지 않습니다.")
    if any(not isinstance(report.get(key), str) or not report[key].strip() for key in REPORT_FIELDS):
        raise RuntimeError("검토 보고에 비교 대상·텍스트 충돌·계약 위험·검증·미확인 사항·권장 순서를 모두 작성하세요.")
    # Acknowledged risks are reported for the user's decision, never an automatic
    # denial. The runner verifies real unmerged Git entries after execution.


def current(root: Path, evidence: dict) -> bool:
    return evidence["snapshot"] == snapshot(root, evidence["source"], evidence["target"])
