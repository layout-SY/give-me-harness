# 하위 에이전트의 고아 쓰기 예약 수정

## 발생한 문제

2026-10-15 user-ui의 `orchest` 세션(`회의실-시간슬롯-mock-해제`, 작업 `vo-entry-code-route`)에서 Watcher가 묶음 A를 PASS로 판정했다. 그런데 승인된 commit 실행이 세 번 모두 같은 이유로 막혔다.

```
Git 작업: 해당 worktree에 실행 중이거나 결과 미확인인 변경 도구가 있습니다: 0a5bea8e…
```

막은 기록은 중앙 상태의 `branch-relations/v1/writes/0a5bea8e….json`이다. 내용은 Claude 세션 `c5a6ef1f…`의 호출 `toolu_01LnpAuHJgu87w8GzeF27owx`가 15:28:17에 남긴 쓰기 예약이다. 이 호출 ID는 부모와 모든 하위 에이전트의 대화 기록 어디에도 없다.

같은 시각에 Watcher가 `git -C <worktree> check-ignore -v dist node_modules/.tmp`를 실행했다. 이 호출은 "하위 에이전트는 Git 변경과 현황판 갱신을 실행하지 않습니다"로 차단됐고, 예약은 그로부터 0.2초 뒤에 기록됐다.

## 원인

1. `git check-ignore`는 조회 명령인데 조회형 Git 목록에 없었다. 그래서 Git 변경으로 분류됐고, 하위 에이전트의 Git 변경 거부에 걸렸다.
2. 쓰기 예약은 PreToolUse에서 만들어지고 PostToolUse에서 지워진다. 조회형이 아닌 셸 명령(`npx`·`npm` 등)도 예약 대상이다.
3. 추정: Watcher가 같은 응답에서 병렬로 낸 다른 호출의 PreToolUse가 예약을 남겼다. 그 뒤 앞선 호출이 차단되면서 이 호출은 취소됐고, PostToolUse와 대화 기록이 남지 않았다. Watcher는 이어서 `npx tsc -b`를 새 호출로 다시 실행했다. 취소된 호출의 실제 명령은 기록이 없어 확인하지 못했다.

기존 해소 경로는 둘이다. Claude의 PermissionDenied 근거로 해소하는 `write-denied`와, 실제 종료를 확인한 뒤 승인받아 지우는 `write-recovery`다. 이번 예약에는 PermissionDenied가 없었다. 부모 세션은 `write-recovery` 절차를 알지 못해 멈췄다.

## 수정 (사용자 선택)

| 항목 | 내용 | 적용 범위 |
| --- | --- | --- |
| `check-ignore` 조회 허용 | 조회형 Git 목록에 추가 | 모든 세션 |
| 예약에 하위 에이전트 기록 | PreToolUse의 `agent_id`를 예약에 저장 | 모든 세션(필드 추가만) |
| 하위 에이전트 종료 시 해소 | Claude `SubagentStop` 훅(`subagent-stop`)이 끝난 에이전트의 대화 기록(`agent_transcript_path`)과 대조해, 그 에이전트가 남긴 예약 중 기록에 없는 호출만 해소한다. 해소 전에 `write-receipts/`에 `not-recorded` 근거를 남긴다 | `orchest` 세션 |

- 기록에 있으나 결과가 확인되지 않은 호출은 해소하지 않는다. 실제 종료 확인이 필요하므로 `write-recovery`를 쓴다.
- 다른 에이전트의 예약, 기록 경로가 없거나 파일 이름이 `agent-<agent_id>.jsonl`이 아닌 경우는 건드리지 않는다.
- 부모 세션이 직접 남긴 고아 예약과 Codex·OpenCode는 대상이 아니다.

## 회귀 테스트

`tests/test_orchestration.py`

- `test_git_check_ignore_is_a_read_only_query`: 수정 전 실제 차단 문구로 실패
- `test_reservation_of_a_call_missing_from_the_finished_child_transcript_is_released`: 수정 전 예약에 `agent`가 없어 실패
- `test_child_stop_does_not_release_reservations_outside_orchestration`: 수정 전 `subagent-stop` 모드가 없어 실패

## 이번 세션의 해소

이번 예약은 수정 전에 생겼으므로 `agent` 필드가 없어 자동 해소 대상이 아니다. 소비자 세션의 부모가 `write-recovery`로 해소한 뒤 대기 중인 commit 작업을 다시 실행한다.
