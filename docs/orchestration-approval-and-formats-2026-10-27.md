# 오케스트레이션 승인 조회와 형식 안내

## 발생한 문제

2026-10-27 admin-ui의 orchest 세션(`swagger-api-gap-analysis`)이 작성한 토큰 사용량 보고서 7절에 중앙 정책 개선안이 셋 있었다.

1. **작업별 승인을 확인할 수 없음**
   - 10-23 12:03 무렵 구현 에이전트 6개가 계획 승인 미기록으로 막혔다. 약 1.95M을 썼고, 부모의 재지시까지 합하면 약 2.55M(세션의 7.6%)이다.
   - 사용자가 넣은 승인 입력 중 다음 둘은 기록되지 않았다. 아무 안내도 나오지 않았다.
     - `- <ID> 진행` 목록
     - 줄마다 `<ID> 진행`
   - 계획을 고치면 승인 해시가 바뀌어 다시 승인받아야 하는데, 부모가 이를 확인할 수단이 없었다.
2. **검토 보고와 board 인자의 형식**
   - 보호 실행기 거부 12건 가운데 검토 보고 형식 2건, 단계 값 2건, 작업 등록 인자 2건이 있었다.
   - 형식을 찾으려고 Explore 에이전트(0.17M)를 따로 불렀다.
3. **토큰 집계 스크립트 차단**
   - 스킬이 안내한 대로 절대 경로로 실행해도 다음 오류로 막혔다.
     ```
     현재 프로젝트와 다른 Git 저장소의 명령 대상입니다: …/state/bundles/…/token_usage.py
     ```
   - 10-20 보고서에도 같은 차단이 있었다. 두 세션 모두 사용자가 `!`로 직접 실행했다.

## 원인

1. `approval_policy.task_prompt`는 입력 전체를 공백 하나로 합친 뒤 `<ID> [<ID> …] 진행` 한 형식만 읽었다. 줄바꿈 목록은 `- a 진행 - b 진행`이 되어 맞지 않았다. 맞지 않는 입력은 조용히 일반 대화로 처리됐다.
2. 승인 기록은 세션별 `harness-state-v3`에 있다. 세션 시작 안내는 현재 worktree의 작업 하나만 보여 주고, `board`에는 승인 정보가 없었다.
3. `review` 출력은 길다(이 세션 17.7K자). 보고 형식은 스킬 문서에만 있고 예시가 없었다. `board-set`의 새 작업 등록 조건과 단계 예시도 문서에 없었다.
4. 정책 번들(`state/bundles/…`)은 중앙 저장소 안에 있다. `project_boundary.command_denial`은 다른 Git 저장소의 경로를 인자로 받는 명령을 막는다. 예외는 `cat·head·tail·sed·rg·ls`로 중앙 경로를 읽는 경우뿐이었다.

## 수정 (사용자 선택)

| 항목 | 내용 |
| --- | --- |
| 목록형 승인 | 줄마다 `<ID> [<ID> …] 진행` 또는 `<ID> 구현 승인 취소`이면 각 줄을 승인·취소로 읽는다. 앞의 `-`·`*`·`•`는 허용한다. 한 줄이라도 형식이 다르거나 승인·취소가 섞이면 어떤 작업도 바꾸지 않는다 |
| 미기록 안내 | 입력에 열린 작업 ID와 승인 단어가 있는데 승인으로 읽지 못하면 `작업 승인으로 기록하지 않았습니다: <ID>`와 올바른 형식을 출력한다 |
| 승인 조회 | `board`의 작업마다 `approval`을 붙인다. `status`는 `approved`·`unapproved`·`plan-changed`·`no-plan`·`unknown`이다. 다시 승인받을 때 쓸 입력(`input`)과 계획 오류(`plan_error`)도 함께 보여 준다. 판정 기준은 구현 gate와 같고, 조회는 승인이나 상태 파일을 만들지 않는다 |
| 보고 틀 | `review` 출력 맨 앞에 `report_template`을 둔다. 틀에는 `evidence_digest`를 채운 보고, `complete` 명령과 형식 규칙이 있다. 틀의 설명(`<…>`)을 그대로 보낸 항목은 거부한다. 저장한 검토 근거와 digest에는 틀을 넣지 않는다 |
| 문서 예시 | `git-branch-strategy`에 보고 JSON 예시를 둔다. 오케스트레이션 문서에 `board-set` 새 작업 등록·갱신 예시, 목록형 승인과 `approval` 확인 절차를 둔다. 부모 system prompt에도 승인 확인을 한 줄 추가했다 |
| 집계 스크립트 | 현재 세션 번들의 `token-usage/scripts/token_usage.py`를 `python3 -I <절대 경로>`로 실행할 때만 허용한다. 스크립트 경로는 `orchestration-policy.json`의 `token_analysis.script`에 둔다. 같은 폴더의 다른 스크립트, `-I` 생략, 다른 번들의 사본은 계속 막는다 |

### 승인 조회의 세션 확인

보호 실행기는 hook 이벤트를 받지 않는다. 현재 대화는 호스트가 셸에 넘기는 ID로 찾는다.

- Claude: `CLAUDE_CODE_SESSION_ID`
- Codex: `CODEX_THREAD_ID`

ID가 없으면(OpenCode 등) `status`는 `unknown`이다. 세션 안 `/resume` 뒤에도 이 값이 바뀌는지는 실제 호스트에서 확인하지 못했다. 값이 바뀌지 않으면 이전 대화의 승인 기록을 보여 줄 수 있다.

## 회귀 테스트

- `tests/test_orchestration.py`
  - `test_task_approval_accepts_one_task_per_line_and_reports_unrecorded_input`: 수정 전에는 `- A 진행 - B 진행` 입력에 안내가 없어 실패했다.
  - `test_board_shows_each_task_approval_for_the_running_session`: 수정 전에는 `board` 작업에 `approval`이 없어 실패했다(`KeyError`).
  - `test_token_usage_script_of_the_running_bundle_runs_by_absolute_path`: 번들을 별도 Git 저장소로 둔다. 수정 전에는 보고서와 같은 `다른 Git 저장소의 명령 대상` 오류로 실패했다.
- `tests/test_relation_operations.py`
  - `test_review_output_starts_with_a_report_template_for_complete`: 수정 전에는 `review` 출력의 첫 키가 `version`이라 실패했다.

## 적용

- 새 bundle은 다음 `start`부터 적용된다. 실행 중인 소비자 세션은 handoff 후 새 inject 세션으로 시작한다.
- 보고서의 나머지 개선안(1~5번의 호출 방식)은 소비자 세션의 작업 방식이다. 이번 수정 범위가 아니다.
