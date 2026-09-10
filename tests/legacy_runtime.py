"""이전 V3 계약의 회귀 fixture. 새 V4 기본 동작은 test_shared_git_access에서 검사한다.

사용자가 폐기한 V3 차단의 기대값을 V4에 강요하지 않으면서, 중앙의 이전
완료/복구 코드에 대한 기존 테스트를 계속 실행한다. production 환경 변수로
구버전 권한을 선택하는 경로를 만들지 않고 테스트 렌더에만 계약을 고정한다.
"""
import atexit
import json
from pathlib import Path
import tempfile

from agent_policy.core import CENTRAL_ROOT, render_project as render_current_project


def render_project(project):
    rendered = render_current_project(project)
    key = ".agent-policy/common/contracts/runtime-policy.json"
    contract = json.loads(rendered[key])
    contract["version"] = 3
    contract["artifacts"]["required"] = ["plan.md", "exploration.md", "implementation-log.md",
        "grill-me-review.md", "review-log.md", "evaluation-log.md", "final-summary.md", "portfolio-log.md"]
    contract["artifacts"].pop("optional", None)
    contract["git"]["never_agent_commands"] = ["push", "reset --hard", "clean", "update-ref"]
    contract["git"].pop("access", None)
    contract["capabilities"]["git_write"] = "approved-integrator-assignment"
    rendered[key] = (json.dumps(contract, ensure_ascii=False, indent=2) + "\n").encode()
    guard = ".agent-policy/runtime/branch_guard.py"
    # 몇몇 기존 단위 테스트는 __file__ 없는 가상 module로 실행하므로 같은
    # fixture 계약을 module에도 고정한다. production renderer는 변경하지 않는다.
    rendered[guard] = rendered[guard].replace(b"RUNTIME_CONTRACT = _runtime_contract()",
        ("RUNTIME_CONTRACT = " + repr(contract)).encode())
    return rendered


_temporary = tempfile.TemporaryDirectory(prefix="asan-legacy-test-")
atexit.register(_temporary.cleanup)


def source_guard():
    from agent_policy.core import load_project
    rendered = render_project(load_project("user-ui"))
    root = Path(_temporary.name)
    for name, content in rendered.items():
        if name.startswith((".agent-policy/runtime/", ".agent-policy/common/contracts/")):
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            if name.endswith("branch_guard.py"):
                # 원본 직접 실행 tests와 동일한 미렌더 BASE_BRANCH 조건을 유지한다.
                content = content.replace(b'BASE_BRANCH = "sy-main"', b'BASE_BRANCH = "{{BASE_BRANCH}}"')
            target.write_bytes(content)
    return root / ".agent-policy/runtime/managed_policy_guard.py"
