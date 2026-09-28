# 문의 API·controller 연결

## 결론과 승인

- 역할: Logic, owner. 작업 위치: `/Users/okand/SynologyDrive/asan-metaverse-user-ui`, `sy-main`, 시작 HEAD `fe9d95afbcf9422f30c24c24f05b6275fefcad71`. 기존 미커밋 변경 없음.
- 사용자는 `src/features/inquiry/` 신규 DTO·parser·API·query·mutation 제안에 “다 구현하고, controller까지 구현해”라고 승인했다.
- `typeCode`는 `USER_SIGNUP` 한 항목만 `as const`로 정의한다. `status`는 `OPEN`, `COMPLETED`다.
- 명세의 목록·상세·작성 세 endpoint를 연결한다. UI·라우트 및 Git 변경은 이번 구현 대상에 포함하지 않는다.

## 근거와 재사용

- 중앙 `task-role-routing`, `git-branch-strategy`, `api-authoring` 및 전송·query/mutation 참조, `data-fetch`, `data-dto`, `coding-convention`, `type-definition`, `implementation-quality`, `data-fetch-layer`, `validation`, `custom-hooks`, `documentation`을 확인했다.
- `src/shared/api/api-client.ts`, `axios-instance.ts`, `common/page-response.dto.ts`, `common/dto.ts`, `withAbortSignal.ts`를 재사용한다. envelope와 pagination 구조를 중복 정의하지 않는다.
- `features/citizen-participation/api/notice/`의 정렬 직렬화·parser, query key·hook, `model/forms/proposalForm.ts`의 RHF/Zod 조합을 따른다.
- `features/meeting-reservation/hook/useMeetingReservation.ts`, `useMeetingReservationDetail.ts`와 `pages/citizen-participation/model/useDiscussionDetailController.ts`를 controller 근거로 확인했다.
- 기존 문의 slice는 검색 범위에서 찾지 못했다. 승인된 신규 slice 안에서 목록·상세·작성 controller를 제공한다. 기존 도메인 helper와 같은 방식으로 문의 내부 ApiResult 오류 변환을 둔다.

## 구현·검증 순서

1. `src/features/inquiry/api/`에서 DTO·Zod parser와 인증·취소 가능한 전송 factory를 작성해 명세를 코드 계약으로 고정한다.
2. 같은 feature의 `hook/`, `model/`에서 목록·상세 query와 작성 mutation을 연결하고 성공 시 문의 목록 캐시만 무효화한다.
3. 목록 controller는 페이지·크기·정렬 상태, 상세 controller는 데이터·조회 상태, 작성 controller는 폼 검증·명시적 요청 매핑·중복 제출 방지·성공/실패 상태를 제공한다. 이전 문의 ID는 호출자가 전달하며 서버가 소유권을 판단한다. 작성 성공에 반환 ID를 가정하지 않는다.
4. 기존 Vitest/MSW/Axios 환경에서 요청·응답·오류·취소, query key·캐시 무효화와 controller 상태 전이를 검증한다. 테스트용 응답은 제공된 명세와 사용자 확정 계약만 사용한다.
5. 실제 workdir에서 중앙 `formatting.py apply` 후 `npm run lint`, `npm run test`, `npm run build`를 실행하고 결과를 기록한다.

## 경계

- 새 문의 화면, 내비게이션, 성공 후 이동·폼 자동 초기화 정책을 만들지 않는다. controller의 명시적 초기화 동작과 반환 상태를 UI가 사용할 수 있게 제공한다.
- 제공되지 않은 5개 유형, 문자열 최대 길이, 유형 목록 API, 작성자 필드나 임의 ID를 추가하지 않는다.
- 실제 backend에 문의를 생성하는 검증은 수행하지 않는다.

## 완료 결과

- 승인된 문의 API·query·mutation·controller와 공개 export 구현 완료.
- 문의 테스트 26개, 최종 lint·build 통과. 실제 중앙 포맷 적용 완료.
- 전체 테스트 최종 결과: 807개 통과·13개 실패. 실패 경로와 동시 작업 중 일시 차단·해소 근거는 `final-summary.md`에 기록했다.
