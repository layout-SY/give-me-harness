# 제한 시간을 넘긴 PostToolUse가 남긴 쓰기 예약 수정

## 발생한 문제

2026-10-22 admin-ui의 `orchest` 세션(`ec-관리자-UI`, 작업 `ec-admin-ui` B2)에서 Stop 자동 포맷과 부모의 포맷·검증 명령이 반복해서 막혔다.

```
Stop 자동 포맷 미완료: 같은 worktree에 실행 결과가 확인되지 않은 쓰기가 있습니다. 완료 후 포맷을 다시 실행하세요.
```

막은 기록은 중앙 상태의 `branch-relations/v1/writes/d75a2aef….json`이다. Publisher 하위 에이전트(`af97b099…`)의 호출 `toolu_017gW3Y4czhKM61rK3EtnAxv`가 남긴 예약이다. 호출 내용은 다음 조회였다.

```
shasum <파일>; tail -c 1 <파일> | xxd
```

이 호출은 대화 기록에 결과까지 남았다. 그러나 PostToolUse의 정책 검사가 `정책 검사가 제한 시간 8초를 초과했습니다`로 끝나 예약이 지워지지 않았다. 직전의 같은 조회(`toolu_01HCDsmJ…`)는 PreToolUse에서 같은 제한에 걸렸다. 같은 날 01:40에는 다른 하위 에이전트의 PostToolUse도 같은 이유로 실패했다. 두 시각 모두 부모의 Stop 훅이 실행 중이었고, 01:40의 Stop은 17초 걸렸다.

Stop 오류에 나온 파일 경로 일부가 잘려 보인 것은 터미널 표시 문제다. 대화 원본(JSONL)의 경로는 정상이다.

## 원인

1. `shasum`·`xxd`가 조회 명령 목록에 없어 이 조회가 쓰기로 예약됐다.
2. 정책 검사는 `events.lock`을 기다리는 시간까지 8초 안에 끝내야 한다. Stop 자동 포맷은 이 잠금을 쥔 채 파일마다 Git을 여러 번 조회했다(경로 확인 2회, staged 조회 1회, 병합 여부 등). 이번 작업은 대기 파일이 36개였다. 재현 테스트에서는 파일 1개에 41회, 4개에 98회였다.
3. 이 사이 하위 에이전트의 PostToolUse가 잠금을 기다리다 8초를 넘겨 쓰기 완료를 기록하지 못했다.
4. 2026-10-15의 `SubagentStop` 해소는 대화 기록에 없는 호출만 대상이다. 이번 호출은 기록에 있어 남았다.

## 수정 (사용자 선택)

| 항목 | 내용 | 적용 범위 |
| --- | --- | --- |
| 해시·바이트 조회를 읽기로 분류 | `shasum`·`sha1sum`·`sha256sum`·`sha512sum`·`md5`·`md5sum`·`od`·`cmp`·`stat`을 쓰기 예약에서 뺀다. `xxd`는 출력 파일 인자와 `-r`이 없을 때만 조회로 본다 | 모든 세션 |
| Stop 포맷의 잠금 시간 단축 | 포맷의 잠금 구간마다 Git 조회 결과를 공유한다. 재현 테스트에서 98회가 18회로 줄었고, 파일 수와 무관하다 | 모든 세션 |
| PostToolUse 제한 시간 연장 | 내부 제한 8초 → 25초. host hook 제한 10초 → 30초(Claude `PostToolUse`·`PostToolUseFailure`, Codex `PostToolUse`, OpenCode `post-tool`) | 모든 세션 |
| 하위 에이전트 종료 시 결과 있는 호출도 해소 | `SubagentStop`에서 결과가 기록된 호출의 예약도 해소한다. 실행 결과를 확인할 수 없으므로 실패한 호출과 같게 처리한다. 바뀐 파일은 포맷 기록에서 결과 미확인으로 남기고, `write-receipts/`에 `post-tool-missing` 근거를 남긴다 | `orchest` 세션(Claude) |

- 결과 미확인 파일은 자동 포맷하지 않는다. 내용을 확인한 뒤 수정 도구로 다시 저장해야 포맷 대상이 된다.
- 결과가 기록되지 않은 호출은 여전히 남긴다. 실제 종료를 확인한 뒤 `write-recovery`로 해소한다.
- 부모 세션이 직접 남긴 예약은 대상이 아니다.

## 회귀 테스트

- `tests/test_orchestration.py`
  - `test_hash_and_byte_queries_do_not_reserve_a_write`: 수정 전 조회가 예약되어 실패
  - `test_write_completion_waits_for_the_events_lock_beyond_the_old_limit`: 잠금을 9초 쥔 동안 PostToolUse 실행. 수정 전 실제 오류 문구 `정책 검사가 제한 시간 8초를 초과했습니다`로 실패
  - `test_reservation_of_a_finished_child_call_with_a_result_is_released_as_unconfirmed`: 수정 전 결과가 기록된 호출 2건의 예약이 남아 실패
- `tests/test_formatting.py`
  - `test_formatter_git_queries_do_not_grow_with_the_file_count`: 수정 전 파일 1개 41회, 4개 98회로 실패

## 이번 세션의 해소

이번 예약은 수정 전 bundle에서 생겼다. 사용자 결정에 따라 소비자 세션의 부모가 `write-recovery --id d75a2aef… --reason`으로 해소한다. 근거는 다음과 같다. 호출이 조회뿐이었고, 대화 기록에 결과가 남았고, 저장 전후 파일 해시가 `2607412f…`로 같았다. 새 bundle은 다음 `start`부터 적용된다.
