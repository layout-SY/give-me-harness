# 중앙 필수 산출물 로그 미러링 최종 요약

## 제공 범위

- user-ui/admin-ui의 Logic·Claude 필수 산출물 8종을 중앙 `asan-agent-policy/logs/projects/`로 복사하는 증분 수집기.
- `collect-logs` 수동 CLI.
- Codex Stop, Claude Stop, OpenCode `session.idle` 자동 실행 렌더링.
- 중앙 로그만 미커밋인 경우 정책 sync를 허용하는 청결 판정 분리.
- 허용 목록, 멱등 갱신, 비삭제, 심볼릭 링크, 채널 분리, 호스트 렌더링 회귀 테스트와 운영 문서.

## 제외 사항

- 소비자 프로젝트로의 중앙 정책 sync.
- 중앙 로그의 자동 Git add·commit.
- 필수 8종 외 transcript, 이미지, 임시 파일 복사.
- 원본 삭제의 중앙 반영, 보존 기간과 용량 정리 정책.

## 검증 근거

- `python3 -B -m unittest discover -s tests -v`: 30개 PASS.
- `bin/agent-policy audit`: user-ui/admin-ui 각각 128 managed files PASS.
- OpenCode plugin Node 구문 검사, 설치된 OpenCode 1.18.19 local plugin/config smoke와 `collect-logs --help` PASS.
- 소비자 예상 diff를 확인했고 실제 sync는 실행하지 않았다.
- 네 경로에서 필수 산출물 총 567개를 최초 복사했고 즉시 재실행은 `copied=0`, `unchanged=567`이었다.

## 산출물 경로

- 작업 근거: `.codex/logs/sessions/2026-08-27-central-log-mirror/`.
- 중앙 사본: `asan-agent-policy/logs/projects/{project}/{channel}/sessions/`.

## 제한 사항

- 자동 수집은 생성 정책이 소비자 프로젝트에 sync되고 새 세션이 시작된 뒤 활성화된다.
- legacy `harness_core.py` 불일치 파일은 이번 범위에서 변경하거나 퇴역하지 않았다.

## 다음 단계

1. 중앙 변경을 검토 후 승인된 Git 명령으로 커밋한다.
2. 별도 승인 시 소비자 diff를 다시 검토하고 중앙 정책을 sync한다.
