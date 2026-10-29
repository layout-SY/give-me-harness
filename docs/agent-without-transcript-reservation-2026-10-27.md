# 대화 기록이 없는 에이전트의 쓰기 예약 해소

## 발생한 문제

Stop 자동 포맷이 같은 오류로 매 턴 막힌 일이 두 번 있었다.

| 날짜 | 프로젝트 | 예약 | 에이전트 | 생성 시각 |
| --- | --- | --- | --- | --- |
| 10-23 | user-ui | `729aae49…` | `a678c1665f239910c` | 부모 Stop 2초 뒤 |
| 10-27 | admin-ui | `256f16f7…` | `afeee3500c70b476f` | 부모 Stop(07:38:32Z) 2초 뒤 |

소비자 세션은 "하위 에이전트가 쓰기를 마쳐도 완료가 기록되지 않았다"고 보았다. 실제로는 부모가 부른 하위 에이전트가 아니었다.

- 10-27에 부모는 Publisher `a496d57e…`와 Generator `a9773421…`를 background로 실행했다. 둘 다 대화 기록(`subagents/agent-<id>.jsonl`)이 있다. Generator는 16:45까지 실행됐다.
- 예약을 남긴 에이전트는 대화 기록이 없다. 부모·하위 대화 기록 어디에도 그 호출(`toolu_01LKXEuE…`)이 없다. SubagentStop도 오지 않았다.
- 예약에는 명령·도구·에이전트 종류가 기록되지 않아 이 에이전트가 무엇인지 확인하지 못했다. Claude Code 내부 기능일 가능성이 있으나 확인하지 않았다.

## 원인

1. 셸 명령은 첫 단어가 조회 명령 목록에 없으면 쓰기로 예약된다. 예약은 PostToolUse 또는 SubagentStop 정리에서 지워진다.
2. 이 에이전트는 PostToolUse도 SubagentStop도 없었다. 2026-10-15·10-22의 해소 경로는 SubagentStop에서 시작하므로 예약이 영구히 남았다.
3. `formatting.ensure_idle`은 같은 worktree에 예약이 하나라도 있으면 포맷을 막는다.

## 수정 (사용자 선택)

| 항목 | 내용 |
| --- | --- |
| 진단 기록 | 예약에 `tool`, `command`(앞 200자), `agent_type`, `transcript`(부모 대화 기록 경로)를 함께 남긴다 |
| 자동 해소 | 포맷 전 idle 검사에서 다음을 모두 만족하는 예약은 `write-receipts/`에 `agent-transcript-missing` 근거를 남기고 해소한다. host가 Claude이고 agent가 있다. 생성 후 60초가 지났다. 부모 대화 기록이 있다. `<부모 기록>/subagents/agent-<id>.jsonl`이 없다 |

- 실제 하위 에이전트는 시작할 때 대화 기록이 생기므로 대상이 아니다. 대화 기록이 있는 에이전트의 예약은 이전처럼 막고 `write-recovery` 안내를 보여 준다.
- 해소한 호출이 실제로 파일을 바꿨는지는 확인하지 않는다. Write·Edit 호출의 결과 미확인 기록은 이 수정과 별개로 계속 포맷을 막는다.
- 포맷 실행기 자신의 예약(`formatter`)은 대상이 아니다.

## 이번 예약의 해소

`256f16f7…`는 사용자 지시로 중앙 세션에서 `events.lock`·`git.lock`을 쥐고 삭제했다. 근거는 `write-receipts/945eca61….json`(`removed-by-central-session`)이다.

## 회귀 테스트

- `tests/test_formatting.py`
  - `test_reservation_of_an_agent_without_a_transcript_is_released_after_a_minute`
    - 대화 기록이 없는 에이전트와 있는 에이전트의 예약을 함께 둔다.
    - 수정 전에는 예약에 진단 필드가 없어 실패했다(`KeyError: 'tool'`).
    - 수정 후 확인하는 내용은 다음과 같다.
      - 1분 전 예약은 막는다.
      - 1분 뒤에는 대화 기록이 없는 예약만 수령증과 함께 해소한다.
      - 대화 기록이 있는 에이전트의 예약은 계속 막는다.

## 적용

- 새 bundle은 다음 `start`부터 적용된다. 실행 중인 소비자 세션은 handoff 후 새 inject 세션으로 시작한다.
- 다음에 같은 예약이 생기면 기록된 `command`·`agent_type`으로 에이전트의 정체를 확인한다.
