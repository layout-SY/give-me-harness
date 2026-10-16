---
name: policy-token-usage
description: orchest 세션에서 사용자가 `토큰 분석`을 요청했을 때, 작업 병합 뒤 branch·worktree 정리 전에 부모 세션과 하위 에이전트의 토큰 사용량을 응답 단위로 집계하고 원인·낭비 지점·개선안까지 상세 보고서로 작성한다.
---

# 토큰 사용량 분석

## 적용 조건과 시점

- `orchest` 세션에서 사용자가 `토큰 분석`을 입력했을 때만 작성한다. 요청은 세션이 끝날 때까지 유지되고, 사용자가 `토큰 분석 취소`를 입력하면 거둔다. 요청이 없으면 이 스킬을 쓰지 않는다.
- 작성 시점은 **작업의 병합이 끝난 뒤, 그 작업의 branch·worktree를 정리하기 전**이다. 정리하면 분석에 쓸 branch·commit·worktree 정보가 사라진다.
- 요청이 있으면 guard가 다음을 확인한다.
  - `review --cleanup`으로 준비한 완료(병합과 정리를 한 번에)는 막는다. `review`를 `--cleanup` 없이 다시 준비해 병합만 완료한다.
  - 정리(`cleanup --source <branch> --target <직접 부모>`)는 보고서가 있고, 그 보고서가 직접 부모의 마지막 commit보다 나중에 작성됐을 때만 준비·실행된다.
- 보고서 위치는 세션 산출물 폴더의 `unknown/token-usage-report.md` 하나다. 한 세션에서 여러 작업을 병합하면 같은 보고서를 갱신해 모든 작업 구간을 담는다. 이전 내용을 지우지 않고 새 작업의 절과 전체 합계를 갱신한다.
- 보고서는 부모가 작성한다. 분석 자체를 하위 에이전트에 맡기지 않는다. 회신이 부모 컨텍스트에 다시 쌓여 비용이 두 번 든다.

## 집계 기준

수치는 모두 아래 스크립트의 결과에서 가져온다. 직접 세거나 추정한 값은 그렇다고 표시한다.

| 항목 | 기준 |
| --- | --- |
| 집계 단위 | API 응답 1개당 usage 1회. 응답 하나가 블록마다 한 줄씩 같은 usage로 기록되므로 줄 단위로 더하지 않는다 |
| 입력 구분 | 캐시 신규 기록, 캐시 읽기, 비캐시 입력을 따로 센다 |
| 출력 | 응답마다 max(기록값, 생성 문자 추정)을 하한으로 쓴다(ASCII 3.8자/토큰, 그 외 1.1자/토큰). 저장되지 않는 추론 본문이 있어 실제보다 작다 |
| 비용 환산 | 캐시 신규 × 1.25 + 캐시 읽기 × 0.1 + 비캐시 입력 × 1 + 출력 × 5. 청구액이 아니라 같은 기준의 비교용 가중치다. 보고서마다 이 식을 그대로 적는다 |
| 컨텍스트 | 응답의 비캐시 입력 + 캐시 신규 + 캐시 읽기 |
| 재개 | 하위 에이전트에서 직전 응답과 4분 넘게 떨어진 응답. 그 응답의 캐시 신규가 컨텍스트의 80% 이상이면 전체 재기록으로 본다 |
| 도구 귀속 | 응답 N+1과 N의 컨텍스트 차이를 응답 N의 도구 호출(입력 + 결과 문자 수)에 크기 비례로 나눈 근사(±10%) |
| 작업 구분 | 부모 응답은 작업 구간 파일의 시작 시각으로, 하위 에이전트는 첫 응답 시각으로 작업에 넣는다. 맞지 않으면 구간 파일의 `agents`로 직접 지정한다 |
| 분석 비용 | 이 분석 요청과 분석 응답은 집계에서 뺀다(`--until`) |

## 절차

### 1. 시작 시각과 세션 확인

1. 분석을 시작하는 시각을 UTC로 확인한다(`date -u +%Y-%m-%dT%H:%M:%SZ`). 이후 모든 명령에 `--until <시각>`으로 넣는다.
2. 자기 세션의 native session ID를 찾는다.
   - `python3 -I <스크립트> <host> sessions --project <기본 checkout 경로>`가 이 프로젝트의 최근 세션을 시작·끝 시각, 첫 요청, 마지막 요청과 함께 보여 준다.
   - 첫 요청과 마지막 요청(분석 요청 직전의 입력)이 이 세션과 맞는 것을 고른다. 둘 이상이 맞으면 사용자에게 확인한다.
3. 스크립트는 정책 스냅샷의 `.agent-policy/common/skills/policy/token-usage/scripts/token_usage.py`다. 셸에서는 **절대 경로**로 실행한다. 상대 경로나 `cd … &&`를 붙인 형태는 guard가 다른 저장소 대상으로 보고 막을 수 있다.

### 2. 작업 구간 파일

세션 산출물 폴더의 `unknown/token-usage-tasks.json`을 `Write`로 만든다. 작업마다 사용자 입력 시각을 시작점으로 둔다.

```json
{
  "tasks": [
    {"id": "A", "label": "명세 대조 조사", "start": "2026-10-10T00:41:00+09:00", "workspace": "sy-main 기본 checkout(읽기 전용)"},
    {"id": "B", "label": "swagger-api-align", "start": "2026-10-10T18:26:00+09:00", "workspace": "feature/swagger-api-align"}
  ],
  "agents": {"aeaa79d6": "B"}
}
```

- 작업 경계는 `overview`의 사용자 입력 목록으로 정한다. branch·worktree가 있는 작업, 조사·질문처럼 작업 공간이 없는 구간, 병합·정리 구간을 따로 둔다.
- `agents`는 시각만으로 잘못 들어가는 하위 에이전트만 적는다(ID 앞부분).

### 3. 집계 실행 순서

공통 인자: `<host> <명령> --session <ID> --until <시각> --tasks <구간 파일> --session-directory <세션 산출물 폴더>`

| 순서 | 명령 | 보고서에 쓰는 곳 |
| --- | --- | --- |
| 1 | `summary` | 0절 요약, 2절 전체 합계·비용 구성, 3절 작업별, 4.1 역할별 |
| 2 | `overview` | 기간, 압축 시점, 사용자 입력, 하위 에이전트 목록 |
| 3 | `parent` | 5절 부모: 입력 구간별·작업별, 캐시 재기록, 압축, 큰 결과, 오류 |
| 4 | `agents` | 4.2 에이전트별 표, 4.5 낭비 지점 |
| 5 | `agents --agent <ID>` | 4.3 주요 에이전트 상세. 비용 상위 3~5개와 재개·오류가 있는 에이전트 |
| 6 | `inputs` | 재개된 하위 에이전트에 들어간 후속 지시 |
| 7 | `prompts` | 하위 지시문 길이와 묶음·읽기 범위 지시 여부 |
| 8 | `versions` | 모델·host 버전, 작업별 응답당 도구 수(4.4) |
| 9 | `docs` | 세션 문서의 현재 크기 |

- 출력은 JSON이다. 대화에 통째로 붙이지 않는다. 필요한 값만 골라 표로 옮긴다.
- 출력이 크면 `agents`는 작업별 요약만 보고, 상세는 `--agent`로 한 에이전트씩 본다.

### 4. Git 근거

작업마다 branch, commit, 변경 규모를 확인한다. 정리 전이라 모두 남아 있다.

- `git log --oneline <직접 부모>..<branch>` 또는 병합 commit 기준의 commit 목록
- `git diff --shortstat <분기점> <branch>`: 파일 수, 추가·삭제 줄
- 병합 방식(ff-only, merge commit)과 정리 여부, Watcher 판정 결과

### 5. 보고서 작성

`references/report.md`의 절 구조를 그대로 따른다. 각 절의 필수 항목을 빠뜨리지 않는다.

- **상세하게 쓴다.** 합계만 쓰지 않는다. 작업별, 하위 에이전트별, 부모의 입력 구간별로 나누고, 비싼 구간은 무엇을 읽고 쓰고 검색했는지까지 적는다.
- **근거와 추정을 나눈다.** 스크립트·Git·문서로 확인한 사실과 계산·추정을 구분해 적는다. 원인을 확인하지 못했으면 "확인하지 못했다"고 쓰고 가설만 적는다.
- **비교 기준을 둔다.** 같은 보고서 안의 작업끼리, 그리고 이전 보고서가 있으면 그 수치와 같은 기준으로 비교한다(파일당 비용, 응답당 도구, 재개 재기록, 부모 시작 컨텍스트).
- **개선안에는 절감 추정과 계산 근거를 붙인다.** 다음 작업에서 바로 적용할 것과 중앙 정책 변경이 필요한 것을 구분한다.
- 보고서는 한국어로 쓴다. 사용자 대화 원문은 짧게 인용하고 비밀값·토큰·개인 정보를 옮기지 않는다.

### 6. 마무리

1. 보고서를 다 쓴 뒤 정리를 준비한다(`cleanup --source <branch> --target <직접 부모>`). 정리 뒤 결과를 보고서에 덧붙일 필요는 없다.
2. 사용자에게는 0절 요약 3~5줄과 보고서 경로만 알린다.
3. 같은 세션에서 다른 작업을 이어 병합하면 보고서를 갱신한 뒤 그 작업을 정리한다.

## host별 기록 위치

스크립트는 host 기본 위치를 찾는다. 다른 위치를 읽어야 하면 `--home`으로 지정한다.

| host | 기록 위치 | 응답 usage | 하위 에이전트 |
| --- | --- | --- | --- |
| Claude Code | `~/.claude/projects/<cwd 경로 slug>/<session>.jsonl` (`CLAUDE_CONFIG_DIR`가 있으면 그 아래) | assistant 행의 `message.usage`. `message.id`당 1회 | `<session>/subagents/agent-<id>.jsonl`와 `.meta.json`(역할 `agentType`, 설명 `description`) |
| Codex | `$CODEX_HOME/sessions/**/rollout-*-<thread id>.jsonl`와 `archived_sessions/`. 없으면 `~/.codex` | `token_usage_record`(`response_id`당 1회). 이 행이 없는 이전 CLI는 `event_msg/token_count`의 `last_token_usage` | `session_meta.parent_thread_id`가 부모 thread인 별도 rollout. 역할은 `source.subagent.thread_spawn.agent_role` |
| OpenCode | `$XDG_DATA_HOME/opencode/opencode.db` (기본 `~/.local/share/opencode`) | assistant `message.data.tokens` | `session.parent_id`가 있는 session(하위의 하위까지). 역할은 `session.agent`, 설명은 `title` |

host마다 입력·출력의 의미가 달라 스크립트가 같은 기준으로 맞춘다.

- **Claude Code**: 입력이 비캐시·캐시 신규·캐시 읽기로 나뉘어 있다. thinking 본문은 저장되지 않아 출력은 기록값을 쓴다.
- **Codex**: `input_tokens`가 캐시 읽기(`cached_input_tokens`)와 캐시 기록을 포함하므로 둘을 빼 비캐시 입력으로 쓴다. `output_tokens`는 추론 출력을 포함한다. 2026-10 기록 987건에서 캐시 기록은 모두 0이었다.
  - 압축 호출은 `token_usage_record`에만 있고 `token_count`에는 없다.
  - `compacted` 안의 `latest_token_usage_record`는 직전 기록의 사본이라 세지 않는다.
  - 반복된 `token_count`(누적값이 같은 이벤트)는 버린다.
- **OpenCode**: `input`에 캐시가 들어 있지 않다. 출력은 `output + reasoning`으로 센다. `event` 테이블은 갱신마다 같은 메시지를 반복하므로 쓰지 않는다. 압축 요약 메시지의 usage도 집계한다.

주의할 점

- 자동 압축 직후에는 컨텍스트가 크게 줄고 캐시 신규가 잠깐 커진다. `parent`의 `compactions`로 구분해 낭비로 세지 않는다.
- 하위 에이전트의 역할이 `?`로 나오면 부모의 호출 지시문(`prompts`)과 시각으로 역할을 확인해 보고서에 적는다.
- Codex는 thread를 지우면 rollout도 사라진다. 분석은 세션이 끝나기 전, 정리 직전에 한다.
- Codex 하위 에이전트 중 자동 검토(`guardian`)도 별도 thread로 잡힌다. 보고서에서는 파이프라인 하위 에이전트와 나누어 적는다.
- Codex·OpenCode에서는 하위 에이전트의 Git 차단 등 guard 판정이 Claude와 다르다(`orchestration.md`의 현재 실행 하네스의 경계). 오류를 해석할 때 참고한다.
