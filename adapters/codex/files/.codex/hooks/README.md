# Codex 훅

| 이벤트 | 스크립트 | 강제 규칙 |
| --- | --- | --- |
| `UserPromptSubmit` | `track-user-prompt.py` | 명시적 승인을 기록하거나 해제한다. |
| `PostToolUse` | `track-posttooluse.py` | skill 및 `src/shared/ui/`/reference 탐색을 기록한다. |
| `PreToolUse` | `enforce-pretooluse.py` | 필수 마커가 없으면 애플리케이션 변경을 차단한다. |
| `Stop` | `require-documentation-stop.py` | 보호 대상 변경이 감지되면 기존 7종 문서와 구조화된 `portfolio-log.md`를 요구한다. |

훅 명령은 현재 세션 작업 디렉터리에서 `git rev-parse --show-toplevel`로 프로젝트 루트를 결정한다. 등록 명령에 고정된 SHA-256으로 진입 스크립트와 `hook_common.py`를 함께 검증한 뒤 Python 격리 모드에서 검증된 바이트만 실행한다. 루트 결정·bootstrap·무결성 실패는 stderr 사유와 종료 코드 2를 반환하여 호스트가 차단하도록 한다. `PreToolUse`는 명시적인 읽기 전용 도구만 승인 전에 허용하고, 미분류 local/MCP 도구는 필수 조건이 충족될 때까지 기본 거부한다. 런타임 마커는 `$TMPDIR/codex-harness-state-v2/<root-hash>/` 아래에 있으며 프로젝트 파일이 아니다. 허용된 애플리케이션/패키지/설정 변경은 `source-mutated`를 기록하지만, 차단된 시도는 기록하지 않는다. `Stop`은 이 마커를 Git 변경 감지의 보조 근거로 사용하고, 각 포트폴리오 사례의 메타데이터와 문제 상황·고민과 선택·적용·기술 목적·결과·이력서 문구 구조를 검사한다.
