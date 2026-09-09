# Claude UI TalkToFigma 기본 주입 — 2026-09-09

## 원인과 재현

기존 중앙 launcher는 Claude를 `--setting-sources user`로 시작하면서 별도 MCP 설정을 전달하지 않았다. 사용자 보고의 `~/.claude.json` 프로젝트 경로 아래 등록은 MCP의 local scope다. 두 프로젝트가 중앙 기본값 없이 개인 등록 scope에 의존하고 있었다.

설치된 Claude Code 2.1.263에서 임시 개인 설정에 동일한 local scope 서버를 등록해 다음을 재현했다.

| 실행 조건 | 실제 MCP 상태 |
| --- | --- |
| local 등록 + `--setting-sources user` | TalkToFigma 없음 |
| 같은 등록 + `--setting-sources user,project,local` | connected |
| 같은 등록 + `--setting-sources user` + 중앙 `--mcp-config` | connected |
| 개인 등록 없음 + 두 프로젝트의 중앙 Claude UI 실행 | connected, 도구 탐색 성공 |
| 개인 등록 없음 + 중앙 Claude Logic 실행 | TalkToFigma 없음 |

이 검증은 stdio MCP fixture와 실제 Claude CLI의 `initialize`·`mcp_status` control protocol을 사용한다. 모델 prompt, 외부 API 요청, 실제 Figma 문서 수정은 수행하지 않는다. 실제 WebSocket 서버와 Figma 플러그인 채널의 현재 상태까지 검증한 결과는 아니다.

## 중앙 변경

- `adapters/claude/mcp.defaults.json`: 적용 프로젝트 `user-ui`·`admin-ui`, 역할 `ui`, TalkToFigma stdio 실행 정의를 한 곳에 선언했다.
- `lib/agent_policy/injection.py`: Claude에 대해 프로젝트·역할 조건을 확인하고, PATH 또는 `~/.bun/bin/bunx`에서 실행 파일을 찾는다. `bunx` 심볼릭 링크의 이름을 유지한 절대경로를 기록한다.
- 선택된 MCP 설정을 번들 digest와 manifest에 포함하고, `claude-mcp.json`을 생성해 Claude 실행 인자로 전달한다. 기존 plugin·settings 생성기를 재사용한다.
- Claude `project-ui` 스킬과 사용 가이드에 MCP 연결·WebSocket·현재 채널 확인 절차를 추가했다. 채널 ID는 중앙 설정에 고정하지 않는다.
- `--setting-sources user`는 유지한다. 개인 설정이나 소비자 `.mcp.json`을 변경하지 않으며, 다른 개인 MCP를 배제하는 `--strict-mcp-config`는 추가하지 않는다.

기존 사용자 실행 정의와 동일하게 `cursor-talk-to-figma-mcp@latest`를 사용한다. 번들 digest가 고정하는 것은 실행 설정이며, 실행 시 해석되는 npm 패키지 버전까지 고정하지는 않는다.

## 회귀 검증

`tests/test_injection.py`에 다음 6개 회귀 테스트를 추가했다. 최초 4개 테스트의 실행에서 누락된 주입으로 실패 4건을 확인한 뒤 구현했다.

1. 개인 등록이 없는 두 프로젝트의 Claude UI 기본 MCP 주입과 소비자·개인 설정 보존
2. 두 프로젝트 × 3개 host × 5개 role 및 대상 밖 프로젝트의 조건 분리
3. MCP 정의 변경 시 새 번들 생성과 원래 설정으로 세션 재개
4. 공백 경로·bunx 심볼릭 링크·기본 설치 경로 탐색과 실행 파일 누락 진단
5. MCP가 없던 기존 assignment 재개 시 새 설정을 소급 주입하지 않음
6. 실행 파일 경로 변경 시 별도 번들 생성

`tests/smoke_claude_mcp.py`는 실제 Claude CLI로 위 재현표의 9개 실행 조합을 검증한다. 별도 SDK 설치가 필요하지 않으며 임시 MCP 서버를 사용한다.

최종 결과: 전체 unittest **191개 통과**(680.569초), 중앙·admin-ui·user-ui audit PASS, 실제 Claude CLI 9개 조합 PASS, `git diff --check` PASS.

검증 명령:

```sh
python3 -m unittest discover -s tests -v
bin/agent-policy audit
python3 tests/smoke_claude_mcp.py
git diff --check
```

실행 증거:

- `/private/tmp/asan-claude-mcp-red.log`: 수정 전 실패
- `/private/tmp/asan-claude-mcp-green.log`: 최초 회귀 테스트 수정 후 통과
- `/private/tmp/asan-claude-mcp-full-suite.log`: 전체 unittest 실행 결과
- `/private/tmp/asan-claude-mcp-audit.log`: 중앙·두 프로젝트 audit PASS
- `/private/tmp/asan-claude-mcp-native-final/results.json`: 실제 Claude CLI 9개 실행 조합 PASS
- `/private/tmp/asan-claude-mcp.diff`: 이번 요청에서 추가한 diff

## 적용 handoff

중앙 `start --print-only`로 다음 새 번들과 assignment를 준비하고 MCP 실행 경로·인자·manifest 해시를 검증했다. 실제 소비자 세션은 아직 교체하지 않았다.

| 프로젝트 | 준비한 번들 | 시작 전 assignment |
| --- | --- | --- |
| user-ui | `build/user-ui/claude-ui-3650d969f5151282` | `63e7ebd369a543e7a9a70f14e40d876f` |
| admin-ui | `build/admin-ui/claude-ui-536f0e4ca10cd868` | `a8c3865c75ab4a689a6a0a0516590edd` |

실행 인자는 `/private/tmp/asan-user-ui-claude-mcp-launch.txt`와 `/private/tmp/asan-admin-ui-claude-mcp-launch.txt`에 기록했다. 이 준비는 기존 task의 Git 소유권 이전이나 구현 승인 복제를 수행하지 않는다.

소비자 담당 세션은 현재 작업·브랜치·소유권·Figma 연결 정보를 handoff에 남긴 뒤 해당 프로젝트의 중앙 launcher로 새 세션을 시작한다.

```sh
bin/agent-policy start --project user-ui --host claude --role ui
```

```sh
bin/agent-policy start --project admin-ui --host claude --role ui
```

기존 task 소유권을 이어받아야 한다면 저장소의 `assignment-handoff` 절차를 따른다. 원래 assignment에 `--resume-assignment`를 사용하면 이전 번들과 MCP 설정이 그대로 유지된다. 새 세션의 `/mcp`에서 TalkToFigma 연결을 확인한 뒤 현재 Figma 플러그인 채널에 참가한다.
