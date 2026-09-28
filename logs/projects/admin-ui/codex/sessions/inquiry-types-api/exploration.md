# 탐색

## 결론

문의 타입 API는 현재 slice에 없으며, 기존 답변 API·hook·MSW는 사용자 명세와 일치한다. 기존 문의 관련 테스트 33개가 기본 checkout에서 통과했다. 사용자 승인에 따라 기존 inquiries slice를 타입 모듈로 확장한다.

## 조사 경로와 재사용 근거

- `src/entities/inquiries/api/inquiry.api.ts`, `inquiry.dto.ts`, `inquiry.parser.ts`: 답변 POST·PUT·DELETE, 상태 PATCH, 문자열 응답 parser, 페이지 공통 DTO 사용.
- `src/entities/inquiries/hook/`, `model/inquiry-mutation-options.ts`, `model/query-keys.ts`: TanStack Query, 실패 unwrap, signal 전달, 성공 후 관련 캐시 갱신.
- `src/entities/items/api/item-category.api.ts`, `model/item-category-query-options.ts`, `model/item-category-mutation-options.ts`, `src/pages/item-category/hook/use-item-category-controller.tsx`: 같은 slice 안의 별도 하위 리소스 factory와 실제 화면 사용처 확인.
- `src/shared/api/common/response.dto.ts`, `api-client.ts`, `axios-instance.ts`, `with-abort-signal.ts`, `src/app/providers/query-client.ts`: envelope 정규화, 양수 응답 page, 인증·취소, 전역 오류 처리.
- `src/shared/ui/`: 공용 UI 파일 목록 확인. 이번 작업은 API·hook 범위다.
- `src/mocks/inquiries.handlers.ts`, `handlers.ts`, `tests/inquiries-*.test.mjs`, `tests/item-category-query-mutation.test.mjs`: 기존 MSW 등록 순서와 실제 Axios·QueryObserver 검증 패턴.

## 확인된 계약

- 타입 조회 항목: `id`, `code`, `name`. 목록: `items`, `total`, `page`, `size`.
- 타입 등록 body: `code`, `name`. 타입 수정 body: `name`. 타입 삭제에는 body가 없다.
- 변경 성공 envelope의 data는 string이다.
- 사용자가 요청·응답 1 기준, 요청 0의 첫 페이지 호환을 확인했다.
- 타입 모듈을 inquiries 내부 별도 파일로 추가하는 방식을 사용자가 선택했다.
- 사용자 프롬프트의 인증 토큰은 코드·fixture·기록으로 복사하지 않는다. 기존 인증 경로를 사용한다.

## 불러온 스킬

`skill-index`, `policy-task-role-routing`과 Logic·handoff·pipeline 참조, `policy-git-branch-strategy`, `recipe-api-authoring`과 transport-contracts·query-mutation 참조, `policy-coding-convention`, `policy-type-definition`, `policy-data-fetch-layer`, `policy-implementation-quality`, `policy-documentation`.

## 미확인 범위

실서버 호출은 실행하지 않았다. 타입 삭제 시 기존 문의 처리, 중복 code 제약과 생성 ID 규칙은 제공되지 않아 로컬 업무 규칙으로 추가하지 않는다.
