# 계획: 오케스트레이션 1차 보강 (하위 에이전트 계약·현황판·리뷰 지문)

<!-- asan-plan:approval:start:v1 -->

## 목표

한 세션에서 부모가 하위 에이전트(Planner·Publisher·Generator·Refactorer·Watcher)를 파이프라인으로 실행할 때 필요한 계약과 도구를 중앙 정책에 추가한다.

## 작업 유형

- feature (중앙 정책·runtime·호스트 adapter·테스트)

## 범위

- 대상 repository: `asan-agent-policy` (branch `main`, 기본 checkout)
- 포함:
  1. 하위 에이전트 공통 계약을 단일 원본으로 두고 렌더러가 3개 호스트의 모든 자식 정의에 삽입한다. 자식 정의의 정책·runtime 경로를 inject 번들의 절대 경로로 바인딩한다.
  2. `generate` 프로필에 `planner`와 오케스트레이션 문서를 추가한다.
  3. 호스트가 자식 실행을 식별해 주는 경우(`agent_id`) 자식의 Git 변경 준비·실행을 guard가 거부한다.
  4. 검토 지문 명령(`fingerprint`)과 Watcher 리뷰 문서 계약을 추가한다.
  5. 작업 현황판(`board`, `board-set`, `board-wait`)을 기존 브랜치 관계 그래프 옆에 추가한다. 쓰기 잠금은 두지 않는다.
  6. 선행 작업이 `커밋됨`이 되면 대기 작업에 변경 파일 목록을 안내한다(대기 명령, SessionStart·UserPromptSubmit 훅, 프롬프트).
  7. 공통 정책·역할 문서·템플릿·README·운영 문서와 회귀 테스트.

### 추가 범위 (2026-10-09 사용자 요청, 구현 전 결정 대기)

8. 하위 에이전트의 역할 본문을 `policy/common/`의 역할별 단일 원본으로 옮기고, 호스트 adapter에는 형식(frontmatter·TOML 키·도구 목록)만 남긴다. 현재는 같은 역할의 본문이 호스트마다 다르게 손으로 적혀 있다.
9. Publisher는 `references/ui.md`의 UI 역할 계약을 적용하고 Figma MCP를 사용한다. Figma 연결 절차는 Claude 전용 스킬(`project-ui`)에서 공통 문서로 옮긴다.
10. Generator와 Refactorer는 `references/logic.md`의 Logic 역할 계약을 적용한다.
11. Figma MCP 정의를 공통 원본으로 두고 호스트별 형식으로 렌더한다. 현재는 Claude의 `role=ui` 세션에만 주입된다.

결정이 필요한 항목은 `final-summary.md`가 아니라 사용자 답변을 받은 뒤 이 절에 기록한다.

## 제외 사항

- 한 세션에서 여러 작업을 동시에 진행하는 구조(작업별 `plan.md` 승인 바인딩). 2차 작업으로 둔다.
- 파일 쓰기 차단 훅, 역할별 스킬 읽기 강제 훅, 별도 스케줄러.
- 소비자 저장소 변경, 중앙 로그 삭제, Git commit.
- 작업 시작 전부터 미커밋 상태였던 Codex Git 실행기 권한 변경(`injection.py`, `test_injection.py`, `README.md`)의 내용 변경. 같은 파일에 이번 변경을 덧붙이기만 한다.

## 사용자 결정 (2026-10-09)

- 후속 작업이 풀리는 시점은 `커밋됨`이다.
- 자동으로 이어가는 범위는 재계획까지이며, 변경된 파일만 다시 조사한다. 훅과 프롬프트 양쪽에 반영한다.
- 다중 작업은 단일 작업 파이프라인과 현황판을 완성한 뒤 진행한다.
- 현황판은 쓰기 제한 없이 브랜치·워크트리 관계, 병합 순서, 작업 현황을 보여 주고 공용 항목 변경 시 영향받는 워크트리를 경고한다.
- 외부 도구(beads, MCP Agent Mail, superpowers 등)는 도입하지 않는다.

## 0단계 확인 결과 (호스트의 부모·자식 구분)

| 호스트 | 근거 | 판단 |
| --- | --- | --- |
| Claude Code | 공식 hooks 문서: 하위 에이전트 안에서 발생한 도구 이벤트 입력에 `agent_id`가 들어온다 | guard로 강제 |
| Codex | 공식 hooks 문서: `PreToolUse` 입력에 식별 필드가 없고 하위 에이전트 훅은 부모 `session_id`를 쓴다 | 프롬프트 규칙만, 강제 미보장 |
| OpenCode | 공식 plugins 문서에서 확인하지 못함 | 프롬프트 규칙만, 강제 미보장 |

## 검증

- 신규 `tests/test_orchestration.py`와 영향받는 기존 테스트 수정
- `python3 -m unittest discover -s tests -v`
- `bin/agent-policy audit`

## 위험 요소

- 실제 호스트를 띄운 종단 검증은 이 세션에서 수행하지 않는다. 호스트별 동작은 문서 근거와 단위 테스트까지다.

<!-- asan-plan:approval:end:v1 -->

## 진행 기록 (해시 제외)

- 승인: 사용자 "나머지 사항은 너가 계획한 방향 그대로 해서 필수 산출물들을 포함하여 작업 진행", "오케이. 작업 진행"
- 구현 완료: 범위 1~7. 변경 파일과 검증 결과는 `final-summary.md`에 기록한다.
- 범위 조정: 현황판을 관계 그래프(`graph.json`)에 넣지 않고 `work-board/v1/board.json`으로 분리했다. 그래프는 `owner`·`assignment` 필드를 거부하고, 준비된 Git 작업이 그래프 전체를 승인 대상과 비교하므로 단계 갱신이 승인을 무효로 만들기 때문이다.
- 수정 전 상태 확인: `HEAD`의 자식 정의 3종(`generator`)에 "부모에게 반환" 계약 문구가 0건이고 정책 경로가 상대 경로였다.
