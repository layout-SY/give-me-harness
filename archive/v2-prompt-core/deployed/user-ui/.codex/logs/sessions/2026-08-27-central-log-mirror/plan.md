# 중앙 필수 산출물 로그 미러링 계획

## 결론

각 소비자 프로젝트의 필수 세션 산출물 8종을 독립 Git 저장소인 `asan-agent-policy/logs/projects/`로 복사하는 수집기를 추가한다. Codex·Claude Code·OpenCode의 수명주기 종료 지점에서 자동 실행하되 Git add·commit과 소비자 정책 sync는 자동화하지 않는다.

## 작업 구간

1. 기존 산출물 경로, 중앙 렌더러, 호스트별 종료 이벤트와 Git 청결 판정을 조사한다.
2. 허용된 파일만 증분·원자적으로 복사하는 중앙 수집기와 `collect-logs` CLI를 구현한다.
3. Codex Stop, Claude Stop, OpenCode `session.idle`에 프로젝트·채널별 수집 명령을 연결한다.
4. 중앙 `logs/**` 변경만 정책 sync 청결 판정에서 제외하고 정책 소스 변경은 계속 차단한다.
5. 단위 테스트, audit, 소비자 예상 diff로 검증한다.
6. 현재 프로젝트들에 존재하는 필수 산출물을 중앙 로그로 최초 수집하고 멱등성을 확인한다.
7. 필수 문서를 완성하고 중앙 저장소에 커밋한다.

## 담당과 적용 정책

- 구현: 현재 Logic Session이 Python CLI·렌더러·OpenCode plugin과 문서를 수정한다.
- 검토: 별도 리뷰 에이전트를 실행하지 않고 Watcher 체크리스트 기준을 `review-log.md`에 직접 기록한다.
- 적용 스킬: `policy-harness`, `policy-documentation`, `policy-abstraction-strategy`, `policy-review-checklist`, `policy-portfolio`.

## 승인 경계

- 사용자는 2026-08-27 `작업 진행`으로 중앙 구현과 기존 로그의 최초 수집을 승인했다.
- 소비자 프로젝트로 생성 정책을 배포하는 `sync`는 이번 승인 범위에 포함하지 않으며 별도 승인 전 실행하지 않는다.
- Git add·commit은 중앙 구현과 검증이 끝난 뒤 정확한 명령을 제시하고 실행 승인을 받는다.
