# 최종 요약

## 제공 사항

- 독립 Git 프로젝트 `/Users/okand/SynologyDrive/asan-agent-policy`
- user-ui Git HEAD 기반 공통 정책과 Codex·Claude Code·OpenCode adapter
- `audit`, `diff`, `check`, `sync`, `start` CLI
- source digest, 파일별 SHA-256 manifest와 안전 legacy 퇴역
- 소비자 managed 파일 수정 거부와 SessionStart drift 안내
- 중앙 단위 테스트 18개와 OpenCode 실제 load smoke test

## 제외 사항

- 실제 타깃 배포
- 프로젝트별 overlay와 Agora 전용 정책
- `폐기된 외부 정책 저장소`, 그 백업, `asan-harness` 수정·삭제

## 검증

| 명령어 | 결과 |
| --- | --- |
| `python3 -m unittest discover -s tests -v` | 18 tests, OK |
| `bin/agent-policy audit` | 두 프로젝트 127 managed outputs, PASS |
| `python3 tests/smoke_opencode_plugin.py` | PASS |
| `bin/agent-policy diff --project all --json` | 배포 예정 차이 탐지; manifest 없음 |

## 산출물

- 중앙 프로젝트 commit `1fc8070 feat: 중앙 에이전트 정책 프로젝트 구축`
- 중앙 감사 문서 `/Users/okand/SynologyDrive/asan-agent-policy/docs/baseline-audit.md`
- 현재 세션 문서 `.codex/logs/sessions/2026-08-26-asan-agent-policy-v1/`

## 남은 제한 사항

- 두 프로젝트 legacy `harness_core.py` 3개씩의 감사 hash가 동시 변경으로 달라 자동 퇴역할 수 없다.
- user-ui AI 파일 Git index 제거가 별도 작업에서 진행 중이며 의도를 확인해야 한다.
- 실제 sync/check와 세션 재시작은 아직 수행하지 않았다.

## 다음 단계

동시 변경을 폐기 가능한 legacy로 볼지 사용자에게 확인하고, 승인 시 감사 snapshot 갱신 여부를 결정한 뒤 `sync --project all --retire-legacy`, `check`, consumer test, handoff/restart를 수행한다.
