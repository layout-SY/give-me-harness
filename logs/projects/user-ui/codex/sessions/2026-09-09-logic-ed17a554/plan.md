# 계획

## 목표 및 범위

화면 명세 기반 추정 DTO로 예약 목록·상세·취소·신규 예약 제한 API와 MSW를 구현하고 기존 controlled UI에 hook·라우트를 연결한다. 사용자가 실제 API 명세가 없으므로 최신 UI handoff의 추정 요청·응답을 사용하도록 지정했다.

- 유형: feature
- `src/features/meeting-reservation/api`, `model`, `hook`, `mocks`: DTO·parser·API, 상태 6종, 조회 및 취소 상태, mock과 테스트.
- feature `index.ts`, `testing.ts`: 공개 계약 export.
- `src/pages/meeting-reservation`, `src/app/routing.ts`, `src/shared/config/meetingReservationRoutes.ts`: 기존 UI와 hook 연결 및 보호 라우트 등록.
- 현재 Codex 세션 디렉터리: owner 필수 8종 산출물.

## 제약 및 제외 사항

UI JSX·CSS·표현 계약 수정, 실제 서버와 관리자 승인 API 구현, 배포는 제외한다. 입장 코드는 상세 응답에서 받으며 별도 발급·재발급 요청은 없다. 취소 최종 요청에서 예약자·상태·시작 5분 전 조건을 MSW가 재검증한다. 목록 페이지네이션은 유지한다. 화면 캡처는 하지 않는다.

## 역할 및 스킬

- 역할: logic (inject), Git 통합 담당: codex, 산출물 책임: owner.
- 스킬: policy-task-role-routing, policy-git-branch-strategy, skill-index, recipe-api-authoring, policy-data-fetch-layer, policy-type-definition, policy-coding-convention, policy-implementation-quality, policy-documentation, reference-custom-hooks.

## 작업 순서

1. 예약 feature에서 DTO·parser·API를 추가해 추정 서버 계약과 표시 모델을 분리한다.
2. MSW에 상태별 fixture, 탭·페이지, 취소 전이, 예약 제한을 구현한다.
3. query key·hook을 확장하고 pages에서 목록·상세·취소·예약 제한 팝업을 연결한다.
4. Axios→MSW 계약, parser, hook·라우트 흐름을 검증하고 결과를 기록한다.

## 검증 및 대안

Vitest로 정상·빈 목록·오류, 상태 6종, 페이지·탭, 취소 시점 재검증, 코드 폐기·캐시 갱신, 예약 제한을 확인한다. `npm run lint`, `npm run build`, `npm run test`를 수행한다. handoff가 보고한 시민참여 테스트 6개 실패는 실제 실행 결과로 재확인한다.

fixture를 UI에 직접 주입하는 안은 API 흐름을 검증하지 못하고 도메인 전반 재설계는 범위를 넘는다. 기존 ApiClient·Zod·TanStack Query·MSW를 확장하는 안을 선택한다.

## 승인 및 브랜치

- 구현 계획과 브랜치 SHA 보고 각각에 사용자가 `진행해`로 승인했다.
- branch: `task/reservation-mock-logic`, parent·직접 merge 대상: `task/reservation-detail-ui`.
- parent HEAD: `b5b07fab0a0f93cf1b1423d8ee2cc1a7088377ac`.
- contract SHA: `015f49eca96ee1c73add084c10faef2b8715b2dff63a17382e492ec7714f97d2`.
- worktree: `/Users/okand/SynologyDrive/asan-worktrees/reservation-mock-logic`.
- 현재 세션의 실제 산출물 귀속은 `2026-09-09-logic-ed17a554`이다. 최초 시도한 작업명 기반 폴더는 귀속 불일치로 거부됐고 파일은 생성되지 않았다. 귀속된 문서는 별도 artifact 검사 대상이므로 브랜치 소스 범위를 변경하지 않고 등록 경로를 사용한다.
- 병합은 구현·검증·문서화 후 별도 승인 대상이다.
