# 구현 로그

## 승인된 범위

중앙 프로젝트 구현과 두 타깃 dry-run까지 승인되었다. 실제 타깃 배포는 제외한다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `/Users/okand/SynologyDrive/asan-agent-policy/policy/common/` | user-ui Git HEAD 기반 공통 AGENTS와 skills 구성, 프로젝트 고유 카탈로그 제거 | 완료 |
| `/Users/okand/SynologyDrive/asan-agent-policy/adapters/` | Codex·Claude Code·OpenCode host 형식과 hook/plugin 구성 | 완료 |
| `/Users/okand/SynologyDrive/asan-agent-policy/policy/guards/managed_policy_guard.py` | managed 파일 편집 및 명시적 shell write 차단, SessionStart drift 안내 | 완료 |
| `/Users/okand/SynologyDrive/asan-agent-policy/lib/agent_policy/` | audit/diff/check/sync/start, source digest, manifest, 안전 퇴역 구현 | 완료 |
| `/Users/okand/SynologyDrive/asan-agent-policy/projects/` | 두 대상의 경로·명령과 최초 legacy hash 감사 스냅샷 | 완료 |
| `/Users/okand/SynologyDrive/asan-agent-policy/tests/` | 렌더·guard·manifest·consumer hook·OpenCode smoke 검증 | 완료 |
| `.codex/logs/sessions/2026-08-26-asan-agent-policy-v1/` | 현재 작업 필수 8종 근거 | 완료 |

## 결정 사항

- `asan-prompt-core` 및 `asan-harness` 소스를 재사용하지 않고 user-ui commit `9edd378560c3c3b7f258984698202498f5c31831`을 기준으로 삼았다.
- 공통화 근거가 없는 실제 컴포넌트·custom hook 목록은 중앙 출력에서 제외하고 대상 검색 규칙으로 바꿨다.
- Claude UI 전담 역할은 baseline대로 유지하되 산출물 경로 모순만 해결했다.
- manifest는 파일별 SHA-256과 source digest를 기록한다. 이전 manifest 또는 감사 hash와 일치하지 않는 파일은 삭제하지 않는다.
- host와 model은 `start`에서 별도 인자로 받는다.
- 커밋 메시지는 영어 Conventional Commit type과 한글 요약을 사용한다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `python3 -m unittest discover -s tests -v` | 18 tests, OK |
| `bin/agent-policy audit` | admin-ui/user-ui 각각 127 managed files, PASS |
| `python3 tests/smoke_opencode_plugin.py` | OpenCode local agent-policy plugin 실제 load PASS |
| `bin/agent-policy diff --project all --json` | 각 대상 add 9, change 99, legacy 11, manifest missing |
| `git show --check --stat --oneline HEAD` | whitespace 오류 없음 |
| `git log -1 --oneline` | `1fc8070 feat: 중앙 에이전트 정책 프로젝트 구축` |

## Watcher 인계

- 중앙 프로젝트 구현과 dry-run은 검토 가능하다.
- 소비자 sync는 수행하지 않았다.
- legacy 11개 중 3개씩은 최초 감사 후 hash가 변경되어 명시적인 폐기 승인 없이는 `--retire-legacy`가 실패한다.
