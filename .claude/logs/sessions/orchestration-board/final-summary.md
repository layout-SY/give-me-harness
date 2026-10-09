# 최종 요약: 오케스트레이션 1차 보강

## 상태

- 계획 범위 1~7: 구현·검증 완료. `task/orchestration-board`의 `c520a31`에 커밋
- 이전 Codex 세션의 미커밋 작업: 같은 브랜치의 `5a35420`으로 분리해 커밋
- 추가 범위 8~10(역할 본문 단일화, Publisher의 UI 방식과 Claude Figma MCP, Generator·Refactorer의 Logic 방식): 구현·검증 완료
- 추가 범위 11(Figma MCP의 3개 호스트 공용화): 사용자 결정으로 하지 않음. Claude에만 둔다
- 추가 범위 8~10과 `ui` 프로필의 `publishing` 추가: `f2541b3`에 커밋
- 2차 범위 12~14(작업별 산출물, 작업 ID별 계획 승인, 재개): 구현·검증 완료
- Figma MCP: 설정만 둔 상태. 사용자가 서버를 켠 뒤 실제 연결을 확인한다

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

### 추가 범위의 변경

| 구분 | 파일 | 내용 |
| --- | --- | --- |
| 신규 | `policy/common/agents/{planner,publisher,generator,refactorer,watcher,evaluator}.md`, `README.md` | 역할 본문 단일 원본 |
| 수정 | 자식 정의 18개 | 본문을 `{{AGENT_CONTRACT:<역할>}}` 표식으로 대체. Claude Publisher에 `Skill`, `mcp__TalkToFigma`와 Figma 연결 절 |
| 수정 | `lib/agent_policy/core.py` | 역할 본문과 공통 계약을 합쳐 표식에 삽입 |
| 수정 | `lib/agent_policy/role_profiles.py` | `generate` 세션의 자식별 역할 방식 매핑, `ui` 프로필에 `publishing` 추가 |
| 수정 | `lib/agent_policy/injection.py` | 설치 사본에 세션 바인딩(적용 역할 계약 문서와 스킬 경로) 삽입 |
| 수정 | `adapters/claude/mcp.defaults.json`, `project-ui` 스킬 | TalkToFigma를 `generate` 세션에도 주입 |
| 수정 | `references/{pipeline-roles,orchestration}.md`, `README.md`, `docs/` | 역할별 작업 방식 |

### 2차 범위의 변경

| 구분 | 파일 | 내용 |
| --- | --- | --- |
| 수정 | `policy/guards/approval_policy.py` | 현황판 작업의 계획으로 source 변경 판정, `<작업 ID> 진행` 승인과 취소 |
| 수정 | `policy/guards/work_board.py`, `git_operations.py` | 계획 경로 검증, worktree로 작업 찾기, `resumable` 목록과 세션 시작 안내 |
| 수정 | `policy/guards/artifact_policy.py`, `lib/agent_policy/log_mirror.py` | `tasks/<작업 ID>/` 산출물 허용과 수집 |
| 수정 | `policy/common/contracts/runtime-policy.json` | `artifacts.task_directory`, `work_board.plan_approval` |
| 수정 | `AGENT_POLICY.template.md`, `references/orchestration.md`, `CHILD_AGENT_CORE.template.md`, `templates/README.md`, `lib/agent_policy/injection.py` | 여러 작업 진행, 승인 입력, 재개 절차 |
| 수정 | `tests/test_orchestration.py` | 작업별 승인, 계획 검증, 세션 계획 유지, 산출물 배치·미러, 재개 테스트 5개 추가 |

## 결정과 근거

- 작업 계획은 작업 ID를 지정한 승인만 인정한다(사용자 결정). 일반 `진행`이 아직 보지 않은 작업 계획을 승인하지 않게 한다.
- 새 세션은 이전 세션의 승인을 승계하지 않는다. 기존 정책의 "다른 세션의 준비·승인은 자동 승계하지 않는다"를 따른다.
- 현황판에 작업이 없는 worktree는 세션 계획으로 판정해 기존 `ui`·`logic` 세션의 동작을 바꾸지 않는다.

- `generate` 세션에서 Publisher는 UI 방식, Generator·Refactorer는 Logic 방식을 적용한다. 스킬 목록은 기존 역할 프로필에서 가져온다. 그 밖의 세션에서는 자식도 세션 role의 방식을 따른다.
- 화면 구조·스타일 리팩터링은 Publisher가 맡는다.
- 세션 바인딩은 호스트가 읽는 설치 사본에만 넣는다. 번들의 정책 스냅샷은 렌더 결과와 같아야 한다는 기존 불변식을 유지하기 위해서다.

- 현황판은 관계 그래프와 별도 파일(`work-board/v1/board.json`)에 둔다. 그래프는 소유권 필드를 거부하고, 준비된 Git 작업이 그래프 전체를 승인 대상과 비교하기 때문이다.
- 쓰기 잠금과 소유권은 만들지 않는다. 범위가 겹치면 알리기만 한다.
- 대기는 선행 작업의 `committed`에서 풀린다. 재조사 범위는 접점 경로의 변경 파일이다.
- 하위 에이전트의 Git 거부는 `agent_id`를 주는 호스트에서만 동작한다. 근거는 각 호스트의 공식 hooks·plugins 문서다.

## 검증

- 1차 범위: `python3 -m unittest discover -s tests -p <모듈>`을 28개 모듈에 대해 병렬 실행, 429개 테스트, 모두 종료 코드 0
- 추가 범위 반영 후 같은 방식으로 재실행: 433개 테스트, 28개 모듈 모두 종료 코드 0
- 추가 범위 작업 중 두 번 실패를 확인하고 고쳤다. `tests/test_injection.py`에 넣은 들여쓰기 오류로 3개 모듈이 import에 실패했고, 세션 바인딩을 정책 스냅샷에 넣어 스냅샷·렌더 일치 테스트가 실패했다.
- 2차 범위 반영 후 같은 방식으로 재실행: 438개 테스트, 28개 모듈 모두 종료 코드 0
- `bin/agent-policy audit`: `central-contract`, `admin-ui`, `user-ui` 모두 PASS
- 수정 전 상태: `HEAD`의 `generator` 자식 정의 3종에 "부모에게 반환" 문구 0건

## 실행하지 않은 검증

- 실제 호스트(Claude Code, Codex, OpenCode)를 띄운 종단 확인
- `python3 -m unittest discover -s tests -v`를 단일 프로세스로 끝까지 실행한 결과. 작업 초반에 시작한 실행은 편집 도중의 원본을 읽었으므로 근거로 쓰지 않았다.

## 미완료와 인계

- Codex·OpenCode의 하위 에이전트 식별 방법 검증
- 하위 에이전트가 자기 작업의 worktree 밖을 수정하지 못하게 하는 강제는 없다. 프롬프트 계약으로 운영한다.
- Claude에서 Publisher가 `mcp__TalkToFigma` 도구를 실제로 받는지, 자식이 번들 경로의 문서를 읽는지는 새 inject 세션에서 확인이 필요하다.
- 커밋은 `task/orchestration-board` 브랜치에 있다. `main` 병합은 하지 않았다.
- 실행 중인 소비자 세션은 원래 번들을 쓴다. 적용하려면 handoff 후 중앙 launcher로 새 inject 세션을 시작한다.
