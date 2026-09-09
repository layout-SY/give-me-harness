# Codex 읽기 근거 누락 수정

## 결론

admin-ui의 `1e866cae40624c5aa22f87e7338c4063` assignment는 구현 승인이 등록됐지만, 성공한 스킬·코드 읽기를 훅이 성공으로 판정하지 못해 source 변경을 차단했다. 중앙 Codex 어댑터와 공통 이벤트 정규화를 수정하고 영구 회귀 테스트를 추가했다.

## 확인한 원인

설치된 **codex-cli 0.153.2**를 임시 저장소와 로컬 응답 서버로 실행해 원시 PreToolUse·PostToolUse 이벤트를 확보했다. 실제 모델이나 소비자 저장소는 사용하지 않았다.

| 정보 | 실제 Codex Bash 훅 | 기존 guard의 기대 |
| --- | --- | --- |
| 명령 | `tool_input.command` | `command` |
| 실행 결과 | 성공·실패 모두 `tool_response`에 출력 문자열만 전달 | 명시적인 종료 코드·성공 상태 또는 결과의 상태 문구 |
| 실행 경로 | 외부 worktree에서 실행해도 `cwd`는 세션 경로이며 `workdir` 생략 | 세션 경로 또는 `tool_input.workdir` |

따라서 인계 문서의 `cmd` 가설은 실제 원시 훅에서는 주원인이 아니었다. Codex가 `exec_command.cmd`를 `Bash.tool_input.command`로 변환하고 있었다. 다만 `cmd`를 그대로 보내는 다른 호출 형식의 호환성 결함도 확인해 공통 입력에서 정규화했다.

기존 성공 판정기는 종료 코드가 없는 출력 문자열을 미확인으로 처리했다. 이 때문에 `skill_confirmed`·`exploration_completed`를 기록하지 않았다. 반대로 파일 내용에 `Process exited with code 0`가 있으면 성공으로 오인할 수 있는 문제도 회귀 테스트로 확인했다.

## 수정 내용과 책임

- `adapters/codex/files/.agent-policy/runtime/codex_events.py`: Codex 실행 기록 형식을 처리한다. 현재 CODEX_HOME의 sessions 아래에서 native 세션·턴·도구 호출 ID·원래 명령이 일치하는 `CommandExecution` 완료 기록을 찾고, 종료 코드와 실제 작업 경로를 반환한다. 명시적인 workdir가 있으면 실행 기록과도 일치해야 한다.
- `policy/guards/event_protocol.py`: 확인된 결과를 공통 `exit_code`·`workdir` 형식으로 보완한다. Codex Bash 출력 본문의 성공 문구는 근거로 사용하지 않는다.
- `policy/guards/tool_paths.py`: shell `cmd`를 `command`로 한 번 정규화한다. 두 값이 다르면 거부한다.
- `policy/guards/managed_policy_guard.py`: PostTool 처리를 시작하기 전에 결과를 정규화한다. 기존 승인·산출물·소유권 판정은 그대로 사용한다.
- `policy/guards/runtime_loader.py`: 중앙 원본 직접 실행과 렌더된 bundle에서 동일한 Codex 어댑터를 로드한다. bundle은 자기 runtime에 포함된 파일을 사용한다.

기록의 첫 세션 식별자와 최근 최대 4 MiB만 읽는다. 전체 대화 이력을 반복 탐색하거나 추가 Git 명령을 실행하지 않는다. 최초 session cwd는 재개 시 달라질 수 있으므로 실제 경로는 해당 도구의 완료 기록에서 판정한다.

## 검증

처음 추가한 전용 테스트 9개를 수정 전 실행해 정상 읽기 누락·실패 출력 오인·입력 별칭 누락을 재현했다. 외부 worktree에서 재개한 세션의 경로 처리도 추가 실패 사례로 고정한 뒤 보완했다.

영구 테스트는 `tests/test_codex_events.py`의 12개 사례다.

- 정상 스킬·소스 읽기 등록과 기존 구현 승인 보존.
- 읽기 근거 충족 후 source 변경 gate 통과.
- 실패한 읽기와 출력 본문의 위조 성공 문구 거부.
- 실행 기록 누락, 다른 세션·턴·호출·명령·경로, 진행 중 상태, 잘못된 종료 코드 거부.
- 다른 위치나 symlink의 transcript 거부.
- 기본 경로와 다른 worktree의 실제 읽기 및 worktree에서 세션 재개.
- 큰 transcript의 마지막 완료 기록 확인.
- 세 host의 `cmd` 호환, 관리 파일 변경 탐지, 충돌하는 별칭 거부.

`tests/smoke_codex_hooks.py`는 설치된 Codex가 수정된 guard를 직접 호출하는 테스트다. 성공한 스킬 읽기, 실패한 소스 읽기, 외부 worktree에서 성공한 소스 읽기를 검증했다.

문제 세션의 실제 rollout에서도 스킬 읽기 2건과 news 코드 읽기 1건을 새 판정기에 대조해 모두 `exit_code: 0`으로 확인했다. 실제 assignment 상태나 기존 bundle을 수정하지 않았고, 기존 `implementation_approved: true`가 보존된 것을 확인했다.

- 전용 테스트 12개: PASS.
- 실제 Codex 0.153.2 훅 smoke: PASS.
- `bin/agent-policy audit`: 중앙·admin-ui·user-ui PASS.
- 전체 unittest: **176개 PASS**, 528.784초. 재개 경로 보완 후 전용 12개도 다시 실행해 PASS했다.

실행 로그: `/private/tmp/asan-codex-events-before.log`, `/private/tmp/asan-codex-events-after.log`, `/private/tmp/asan-codex-resumed-cwd-before.log`, `/private/tmp/asan-codex-events-full-suite.log`. 실제 CLI 이벤트 캡처는 `/private/tmp/asan-codex-events-native/`, 문제 세션 읽기 대조 결과는 `/private/tmp/asan-codex-events-real-session-replay.json`에 남겼다.

## 적용과 범위

기존 inject 세션은 원래 bundle을 유지하므로 새 중앙 `start`로 수정된 정책을 적용한다. 기존 assignment에 `--resume-assignment`를 사용하면 옛 bundle이 유지된다. 같은 `task/connect-news-api`의 기능 변경과 인계 문서는 계속 활용할 수 있으며, 이번 수정은 승인 상태의 수동 변경이나 다른 assignment로의 자동 승계를 수행하지 않는다.

이 어댑터는 **PostTool의 결과와 탐색 경로**를 보완한다. Codex 0.153.2가 PreToolUse에서 생략한 외부 workdir를 사전에 복원하는 기능은 아니다. 외부 worktree의 Git 변경은 명령 자체에 `git -C <절대 경로>`를 명시하고, 파일 변경에는 실제 대상의 절대 경로를 사용해야 사전 검사에서도 대상이 드러난다.

Codex 공식 문서는 Bash의 비정상 종료에도 PostToolUse가 발생하며 transcript 형식은 안정된 인터페이스가 아니라고 설명한다. 이 때문에 기록이 없거나 형식이 달라졌을 때 성공을 추정하지 않으며, CLI 변경 시 native smoke로 호환성을 확인한다. [OpenAI Hooks 문서](https://learn.chatgpt.com/docs/hooks)
