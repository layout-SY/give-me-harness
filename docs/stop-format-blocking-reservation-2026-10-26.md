# Stop 자동 포맷을 막은 쓰기 예약 표시와 worktree별 포맷 계속

## 발생한 문제

2026-10-26 user-ui의 Claude 세션에서 Stop 훅이 반복해서 다음 오류를 냈다.

```
Stop 자동 포맷 미완료: 같은 worktree에 실행 결과가 확인되지 않은 쓰기가 있습니다. 완료 후 포맷을 다시 실행하세요.
```

오류에는 어떤 예약이 막았는지가 없었다. 세션은 원인을 찾지 못하고 중앙 세션 확인을 요청했다.

막은 기록은 중앙 상태 `state/repositories/4513b4f4…/branch-relations/v1/writes/729aae49….json`이다.

- worktree: `remove-meeting-access-mode-dev`
- 호출: 에이전트 `a678c1665f239910c`의 Bash 호출 `toolu_01AWEzJH…`
- 생성: 2026-10-23 16:23:18(KST)

이 에이전트는 대화 기록(transcript)이 없다. 부모·하위 대화 기록과 중앙 상태 어디에도 이 호출의 내용과 결과가 없다. 예약은 부모의 Stop 2초 뒤, 재호출한 Generator `a57e3f0b…`가 시작된 4초 뒤에 생겼다. 에이전트의 정체는 확인하지 못했다.

## 원인

1. 셸 명령은 첫 단어가 조회 명령 목록에 없으면 쓰기로 예약된다. 예약은 PostToolUse 또는 `SubagentStop` 정리에서 지워진다.
2. 이 에이전트는 `SubagentStop`이 오지 않았다. 2026-10-15·10-22의 해소 경로는 모두 `SubagentStop`에서 시작하므로 이 예약은 남았다.
3. `formatting.ensure_idle`은 같은 worktree에 예약이 하나라도 있으면 포맷을 막는다. 오류 문구에 예약 ID·호출·정리 명령이 없어 원인을 찾을 수 없었다.
4. Stop의 `format-stop`은 대기 파일이 있는 worktree를 차례로 포맷하다가 첫 실패에서 전체를 멈췄다. 막히지 않은 다른 worktree도 포맷되지 않았다.

## 수정 (사용자 선택)

| 항목 | 내용 |
| --- | --- |
| 막은 예약을 오류에 표시 | 예약마다 ID, host, session, agent, call, 생성 시각을 보여 준다. 포맷 실행 중인 예약이 아니면 `write-recovery --id <ID> --reason <종료를 확인한 근거>` 명령을 함께 보여 준다 |
| 한 worktree 실패가 나머지 포맷을 막지 않음 | worktree별로 포맷하고 실패는 모아서 한 번에 보고한다. 정책 검사 제한 시간 초과(`PolicyTimeout`)는 worktree 실패로 삼키지 않고 hook 전체를 끝낸다 |

- 대화 기록이 없는 에이전트의 예약을 자동으로 해소하는 방안은 고르지 않았다. 호출이 끝났는지 확인할 근거가 없기 때문이다.
- 이번 예약은 사용자 지시로 중앙 세션에서 `events.lock`·`git.lock`을 쥐고 삭제했다. 근거는 `write-receipts/85606635….json`(`removed-by-central-session`)에 있다. worktree의 변경 파일은 이미 commit되었고 중앙 Prettier 3.7.4 `--check`를 통과했다.

## 회귀 테스트

- `tests/test_formatting.py`
  - `test_stop_names_the_blocking_reservation_and_still_formats_other_worktrees`: 기본 checkout에 `agent_id`가 있는 예약을 남기고 연결 worktree에도 대기 파일을 둔다. 수정 전에는 예약 ID·agent·call·`write-recovery`가 오류에 없고 연결 worktree도 포맷되지 않아 실패했다.

## 적용

- 커밋: `9f58e3c`
- 새 bundle은 다음 `start`부터 적용된다. 실행 중인 소비자 세션은 handoff 후 새 inject 세션으로 시작한다.
- 남은 확인: 이 에이전트가 어디서 생겼는지는 아직 모른다. 10-27 admin-ui에서 같은 형태가 다시 생겨 진단 기록과 자동 해소를 추가했다([대화 기록이 없는 에이전트의 쓰기 예약 해소](agent-without-transcript-reservation-2026-10-27.md)).
