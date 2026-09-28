# 예약 상세 후속 수정 계획

## 목표와 작업 유형

인계 문서의 Logic 후속 결함 3건을 수정한다. 반려 사유를 상세 화면에 연결하고, 제한 쿼리의 배경 갱신 중 예약 폼 입력을 유지하며, 제한 팝업을 닫으면 `/meeting`으로 이동한다.

## 범위와 제외 사항

- `src/features/meeting-reservation/api`: 상세 DTO의 nullable `noticeTitle`·`noticeMessage`와 parser의 표시 계약.
- `src/features/meeting-reservation/mocks`: 반려 사유 fixture, 새 예약의 null 안내 필드, HTTP 계약 테스트.
- `src/pages/meeting-reservation`: 상세 안내 props, 초기 로딩 조건, 팝업 닫기 이동, 라우트 회귀 테스트.
- 현재 세션 산출물: `.codex/logs/sessions/2026-09-09-logic-16de0016`.
- 제외: feature UI·스타일, 시민참여 기존 테스트 결함, 실제 서버 명세 확정, 부모 브랜치 병합과 sy-main 통합.

## 역할·소유권·승인 상태

- 요청 역할과 확인 역할: `logic`; inject 역할과 handoff의 다음 역할이 일치한다.
- assignment: `16de001656d34a7c841bf856b35ec3ca`, host `codex`, 책임 `owner`.
- 사용자 확인: `/meeting` 이동 지정 후 전체 계획에 `진행해`, 생성 계약에도 `진행해`로 승인했다.
- Git 통합 담당자: 현재 자식은 Codex, 부모 `task/reservation-detail-ui`는 Claude.
- 작업 branch: `task/reservation-detail-followup`.
- worktree: `/Users/okand/SynologyDrive/asan-worktrees/reservation-detail-followup`.
- parent·직접 merge 대상: `task/reservation-detail-ui`, 분기 SHA `2184467e3270acd2d49f7652122999fc1e8061f6`.
- 생성 계약 SHA: `f085a551ffc0fffa937338c1391127376c36007fa939106020b8caa743b1d934`.
- 구현·스킬·탐색·브랜치 계약 승인은 현재 assignment에서 확인했다. 병합 승인은 별도다.

## 설계 선택과 제약 조건

최소안인 클라이언트 고정 반려 문구는 예약별 사유를 표현하지 못한다. DTO·parser·MSW·기존 UI props를 연결하는 안을 선택한다. 상태 관리 구조 개편은 이 결함 수정에 필요하지 않아 도입하지 않는다. 서버 명세는 미확정이므로 기존 추정 계약 경계에 nullable 필드를 추가한다. 안내 제목과 본문이 모두 유효할 때만 UI에 전달한다.

초기 조회는 `isPending`으로 차단하고 배경 조회 중에는 기존 폼을 유지한다. 갱신 결과 제한 상태가 확인되면 기존 계약대로 제한 팝업으로 전환한다. UI·CSS는 소유권 밖이며 변경하지 않는다.

## 선택한 스킬

중앙 snapshot의 `policy-task-role-routing`, `policy-git-branch-strategy`, `skill-index`, `policy-coding-convention`, `policy-type-definition`, `policy-data-fetch-layer`, `recipe-data-dto`, `policy-implementation-quality`, `policy-documentation`을 적용한다. 최종 portfolio 기록 시 `policy-portfolio`를 적용한다.

## 작업 구간과 Todo

1. 승인 worktree의 기존 라우트·MSW 테스트에 결함 3건과 안내 필드의 빈 값 경계 테스트를 추가하여 수정 전 실패를 확인한다.
2. 같은 worktree의 API·mock·page 경계에 최소 변경을 적용하여 반려 사유 표시와 입력 보존, 로비 복귀를 구현한다.
3. 예약 도메인 테스트·lint·build로 변경 동작과 타입을 검증하고 Watcher 검토 및 owner 산출물을 남긴다.
4. 승인된 파일만 커밋하고 부모 Git 담당자가 검토할 수 있는 handoff를 작성한다.

## 검증과 위험 요소

- 회귀 재현 및 예약 도메인 검증: `npm run test -- src/features/meeting-reservation/ src/pages/meeting-reservation/`.
- 정적 분석: `npm run lint`.
- 타입·프로덕션 빌드: `npm run build`.
- 인계에 기록된 시민참여 테스트 6건 실패는 이번 실행 결과와 구분한다.
- 브라우저 캡처·시각 QA는 요청 범위에 없으며 실행하지 않는다.
- 새 worktree에는 의존성이 없어 lockfile에 고정된 패키지 설치가 필요하다.
