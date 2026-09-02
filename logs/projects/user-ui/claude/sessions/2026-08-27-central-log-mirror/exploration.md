# 중앙 필수 산출물 로그 미러링 탐색

## 결론

새로운 범용 동기화 계층은 필요하지 않다. 중앙 CLI에 허용 목록 기반 단방향 수집기를 추가하고 기존 세 호스트의 종료 수명주기에 연결하는 것이 가장 작은 구현이다. 활성 세션의 원본은 각 프로젝트에 유지하고 중앙 사본은 별도 Git 이력용 아카이브로 취급한다.

## 확인한 구조

- Logic Session 필수 산출물: 각 프로젝트의 `.codex/logs/sessions/{session}/`.
- Claude Session 필수 산출물: 각 프로젝트의 `.claude/logs/sessions/{session}/`.
- 필수 파일: `plan.md`, `exploration.md`, `implementation-log.md`, `grill-me-review.md`, `review-log.md`, `evaluation-log.md`, `final-summary.md`, `portfolio-log.md`.
- 중앙 렌더링 진입점: `lib/agent_policy/core.py`와 `lib/agent_policy/cli.py`.
- Codex·Claude: 생성되는 JSON hook 설정에 수명주기 명령을 추가할 수 있다.
- OpenCode: 생성되는 plugin이 `session.idle` 이벤트를 받을 수 있다.
- `src/shared/ui/`를 먼저 확인했으며 이번 작업은 UI 생성·수정이 아니므로 재사용할 프로덕션 UI가 없다.

## 기존 로그 현황

승인 전 탐색 시 필수 산출물은 user-ui Logic 324개, user-ui Claude 31개, admin-ui Logic 187개, admin-ui Claude 17개로 집계되었다. 이번 세션의 산출물이 추가되므로 최초 수집 결과는 이 기준보다 늘어날 수 있다. 이미지·대화 원문·필수 목록 외 파일은 대상에서 제외한다.

## 발견한 충돌과 결정

- 현재 중앙 `central_is_clean()`은 모든 미커밋 파일을 정책 sync 차단 사유로 본다. 중앙 로그를 Git에 별도 관리하면 새 로그가 생길 때마다 정책 배포가 막히므로 `logs/**`만 제외하고 정책 소스 변경은 계속 차단해야 한다.
- 소스 로그 삭제를 중앙에 전파하면 아카이브 목적과 충돌한다. 따라서 추가·변경만 반영하고 중앙 사본은 자동 삭제하지 않는다.
- 종료 훅에서 Git add·commit까지 수행하면 사용자 승인 정책과 충돌하고 병렬 세션 간 Git 잠금 위험이 생긴다. 자동화 범위는 파일 복사까지로 제한한다.
- Codex Stop 훅의 오류 코드 `2`는 반복 실행 의미와 충돌할 수 있으므로 수집 실패는 오류를 표시하되 CLI 종료 코드 `1`을 사용한다.
- 심볼릭 링크를 따라가면 허용 경로 밖 파일이 복사될 수 있어 세션 디렉터리와 산출물 파일의 심볼릭 링크를 건너뛴다.
