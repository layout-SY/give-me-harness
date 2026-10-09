# 최종 요약: 오케스트레이션 1차 보강

## 상태

- 계획 범위 1~7: 구현과 검증 완료, 미커밋
- 추가 범위 8~11(역할 본문 단일화, Publisher의 UI 계약·Figma MCP, Generator·Refactorer의 Logic 계약, Figma MCP 공용화): 사용자 결정 대기, 미착수

## 실제 변경

| 구분 | 파일 | 내용 |
| --- | --- | --- |
| 신규 | `policy/common/CHILD_AGENT_CORE.template.md` | 하위 에이전트 공통 계약 단일 원본 |
| 신규 | `policy/guards/work_board.py` | 작업 현황판, 공용 항목 영향 확인, 검토 지문, 대기 안내 |
| 신규 | `tests/test_orchestration.py` | 회귀 테스트 13개 |
| 신규 | `docs/orchestration-board-2026-10-09.md` | 운영 문서 |
| 수정 | `adapters/{claude,codex,opencode}`의 자식 정의 18개 | 공통 계약 삽입 표식. Claude Watcher에 `Write` 추가 |
| 수정 | `lib/agent_policy/core.py` | 표식 치환과 미치환 audit |
| 수정 | `lib/agent_policy/injection.py` | 자식 경로 바인딩, 부모 서문의 현황판 안내, Codex 실행 규칙의 허용 동작 |
| 수정 | `lib/agent_policy/role_profiles.py` | `generate`에 `planner`, `orchestration.md` |
| 수정 | `policy/common/contracts/runtime-policy.json` | `work_board` 계약(단계, 해제 기준) |
| 수정 | `policy/guards/git_operations.py` | `board`, `board-set`, `board-wait`, `fingerprint` |
| 수정 | `policy/guards/shared_git.py` | 새 동작 허용, `agent_id`가 있는 호출의 Git 변경·현황판 갱신 거부 |
| 수정 | `policy/guards/managed_policy_guard.py` | 세션 시작·compact·사용자 입력 훅의 대기 안내 |
| 수정 | `AGENT_POLICY.template.md`, `references/{orchestration,pipeline-roles,workflows,handoff-and-ownership}.md` | 부모·자식 계약, 현황판, 공용 항목, 대기와 재계획 |
| 수정 | `templates/{plan.template,review-log.template,review-log}.md` | 현황판·병합 순서 항목, 검토 지문 항목 |
| 수정 | `tests/test_injection.py`, `README.md` | 허용 동작 목록 기대값, 오케스트레이션 절 |

## 결정과 근거

- 현황판은 관계 그래프와 별도 파일(`work-board/v1/board.json`)에 둔다. 그래프는 소유권 필드를 거부하고, 준비된 Git 작업이 그래프 전체를 승인 대상과 비교하기 때문이다.
- 쓰기 잠금과 소유권은 만들지 않는다. 범위가 겹치면 알리기만 한다.
- 대기는 선행 작업의 `committed`에서 풀린다. 재조사 범위는 접점 경로의 변경 파일이다.
- 하위 에이전트의 Git 거부는 `agent_id`를 주는 호스트에서만 동작한다. 근거는 각 호스트의 공식 hooks·plugins 문서다.

## 검증

- `python3 -m unittest discover -s tests -p <모듈>`을 28개 모듈에 대해 병렬 실행: 429개 테스트, 28개 모듈 모두 종료 코드 0
- `bin/agent-policy audit`: `central-contract`, `admin-ui`, `user-ui` 모두 PASS
- 수정 전 상태: `HEAD`의 `generator` 자식 정의 3종에 "부모에게 반환" 문구 0건

## 실행하지 않은 검증

- 실제 호스트(Claude Code, Codex, OpenCode)를 띄운 종단 확인
- `python3 -m unittest discover -s tests -v`를 단일 프로세스로 끝까지 실행한 결과. 작업 초반에 시작한 실행은 편집 도중의 원본을 읽었으므로 근거로 쓰지 않았다.

## 미완료와 인계

- 추가 범위 8~11의 세 가지 결정: Figma MCP 대상 호스트, 역할 매핑의 적용 범위(`generate`만인지), UI 리팩터링 담당
- 2차: 한 세션의 다중 작업, Codex·OpenCode의 하위 에이전트 식별
- 작업 전부터 미커밋이던 Codex Git 실행기 변경(`injection.py`, `test_injection.py`, `README.md`)은 그대로 두었고 같은 파일에 이번 변경이 덧붙어 있다. 커밋 단위를 나눌 때 구분이 필요하다.
- 실행 중인 소비자 세션은 원래 번들을 쓴다. 적용하려면 handoff 후 중앙 launcher로 새 inject 세션을 시작한다.
