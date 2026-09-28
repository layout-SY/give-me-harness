# 계획

## 목표

사용자가 제공한 문의 타입 CRUD 명세를 기존 inquiries slice 안의 독립 모듈로 연결한다. 이미 구현된 답변 등록·수정·삭제와 상태 변경은 재사용하고 계약 테스트로 함께 확인한다.

## 작업 유형과 범위

- 작업 유형: feature
- 역할: logic (inject로 확인), 산출물 책임: owner
- 작업 위치: `/private/tmp/asan-metaverse-admin-ui-inquiry-types-api`
- 브랜치: `feature/inquiry-types-api`, 직접 부모: `sy-main`
- 분기 기준: `2b9ca35bd20fb9b071d18655e859576fc9a02e49`
- API: GET·POST `/admin/inquiries/types`, PUT·DELETE `/admin/inquiries/types/{typeId}`
- 추가 범위: `src/entities/inquiries`의 타입 API·DTO·parser·query/mutation options·hook과 공개 export, MSW, 계약 테스트
- UI 연결, 다른 기능의 수정, commit·merge는 이번 구현 범위 밖이다.

## 결정 사항과 재사용

- 사용자 확인: 요청·응답 page는 1부터 시작하고 요청 0도 첫 페이지로 처리한다. page·size는 호출자가 명시한다.
- 사용자 선택: 기존 inquiries 내부에 별도 inquiry-type 모듈을 추가한다.
- 공통 `ApiClient`, `ApiResult`, `customConfig`, `withAbortSignal`, `unwrapApiResult`, `PageResponseDto`, `createPageResponseSchema`를 재사용한다.
- 변경 응답의 data는 문자열이므로 기존 `parseInquiryMutationResponse`를 재사용한다.
- 타입 등록은 타입 목록, 수정·삭제는 타입명에 의존하는 문의 목록·상세까지 취소 후 무효화한다. 응답 문자열로 조회 데이터를 덮어쓰지 않는다.
- 타입 code는 명세의 string을 따른다. 기존 정적 코드 enum을 서버 응답의 허용 목록으로 사용하지 않는다.
- MSW는 제공된 6개 타입과 확인된 페이지 계약, 문자열 성공 응답을 사용한다. 미확정 삭제 제약·ID 생성·문의와의 연쇄 변경 정책은 모사하지 않는다. 오류 검증은 테스트에서 명시적으로 주입한다.

## 작업 순서

1. 새 worktree에서 API·DTO·parser를 추가해 요청 필드와 응답 경계를 확정한다.
2. 같은 slice의 query key와 options·hook을 확장해 조회 취소·캐시 무효화를 연결한다.
3. MSW·기존 node:test 도구로 실제 Axios 전송, 성공·빈 목록·실패·취소와 관련 캐시 영향을 검증한다.
4. 공통 포맷 트리거를 실행하고 관련 테스트, `npm run lint`, `npm run build` 결과를 기록한다.

## 승인 및 검증 기준

- 구현 승인: 사용자 “별도 작업 브랜치와 워크트리에서 그대로 진행”.
- Git 생성 승인: 사용자 “명령 실행 승인”. 보호 작업 `2aa58089650a4757adbfd6ea65a48eb3`으로 생성 완료.
- 생성 전 기준 테스트: 기존 inquiry 관련 33개 테스트 통과.
- package.json에 test script가 없어 `node --test`로 관련 `.test.mjs`를 실행한다.
- 필수 포맷: 현재 bundle의 `.agent-policy/runtime/formatting.py apply`를 실제 worktree에서 실행한다.

## 스킬

`recipe-api-authoring`, `policy-task-role-routing`, `policy-git-branch-strategy`, `policy-coding-convention`, `policy-type-definition`, `policy-data-fetch-layer`, `policy-implementation-quality`, `policy-documentation`.
