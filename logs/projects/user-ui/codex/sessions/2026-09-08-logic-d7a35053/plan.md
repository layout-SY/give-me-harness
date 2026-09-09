# 시민 토론 API 연결 계획

## 목표와 승인

- 작업 유형: feature
- 역할: logic, Git 통합 담당: codex, 산출물 책임: owner
- 사용자는 상세 구현 계획을 승인하고 기존 워크트리 대신 새 워크트리를 요청했다.
- 생성 계약 SHA: `7279d610ed7aad373703ff54dd9d715798298e6e2bcc8aedf5b4d45061f66d66`에 대한 독립 승인 후 create를 완료했다.
- branch: `task/citizen-discussion-api-resume`
- parent·직접 merge 대상: `sy-main@466567aee8476459c813c0575e3593eb296f8f33`
- worktree: `/Users/okand/SynologyDrive/asan-metaverse-user-ui-worktrees/citizen-discussion-api-resume`
- assignment: `d7a3505337b34a20a2c02ba719610e0c`, 세션 디렉터리는 launcher가 정한 현재 경로를 유지한다.

## 구현 범위와 순서

1. 새 워크트리에서 기존 lockfile의 의존성을 설치하고 기준 테스트를 실행해 기존 실패와 변경 회귀를 구분한다.
2. `src/features/citizen-participation/api/discussion/`에서 기존 `/citizen/discussions` 기반 임시 DTO·parser를 정의하고 ApiClient·ApiResult로 목록·상세·참여 응답을 검증한다.
3. 시민참여 hook과 pages의 model·route에서 토론 전용 조회와 UI 변환을 연결해 내 활동·페이지·개인 선택·종료 결과를 처리한다.
4. 토론 상태 hook에서 제출 조건·완료 응답·실패 시 선택 보존을 구현하고 댓글의 stance, 등록 조건, 목록 복귀 전 미저장 확인을 기존 UI props/callback에 연결한다.
5. 시민참여 mocks·testing 진입점에서 브라우저 토론 전체 경로를 실제 네트워크로 통과시키며 테스트용 factory는 유지한다.
6. Axios HTTP·parser·상태·route·MSW 통과를 기존 Vitest로 검증하고 lint·build·전체 테스트 및 검토 근거를 기록한다.

## 제약과 결정

- 화면 근거는 `/Users/okand/Downloads/시민참여v_4.8.pdf` 8~9쪽이다.
- endpoint·필드는 백엔드 명세 확정 전 임시 계약이며 실제 서버 호환 여부는 별도 검증 결과로 보고한다.
- 공용 UI 시각 변경, 정책 변경, 새 프레임워크 도입은 포함하지 않는다.
- 기존 워크트리와 미커밋 변경은 보존한다. 병합·정리는 별도 finish 계약 승인 후 수행한다.
- 실패 응답을 완료로 간주하지 않고 진행 중 집계를 노출하지 않는다. 표시용 기간 문자열로 참여 가능 시각을 추정하지 않는다.

## 검증

- 변경 전후 `npm run test`, 관련 Vitest, `npm run lint`, `npm run build`.
- 요청 URL·쿼리·본문, schema 오류, 필터별 캐시, 참여 성공·실패·재조회, 종료 등록 제한, 댓글 stance·좋아요·신고, 미저장 복귀 확인, 브라우저 MSW 통과를 확인한다.
- 기존 실패는 원인과 재현 결과를 기록하며 해당 작업의 회귀를 숨기지 않는다.

## 스킬

task-role-routing, git-branch-strategy, coding-convention, type-definition, data-fetch-layer, implementation-quality, validation, documentation, recipe/api-authoring와 Logic·handoff·pipeline 역할 문서를 적용한다.
