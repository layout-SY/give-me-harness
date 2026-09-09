# 탐색

## 결론

기존 `src/entities/news/api`는 사용처 없는 `/v1/news`와 translations 계약이다. 최근 `inquiries`의 ApiClient·Zod·TanStack Query 구조를 재사용하고 기존 공지 수정 폼의 조회·mutation을 교체한다.

## 요청

사용자가 전체 백엔드 명세 5개를 제공했다. 기존 공지 브랜치는 sy-main과 동일한 커밋이며 dirty 파일과 별도 worktree가 없었다. 사용자는 해당 빈 브랜치를 현재 세션에서 유지해 구현하는 데 동의했다.

## 조사 대상 경로

`src/entities/news`, `src/entities/inquiries`, `src/entities/cp-notice`, `src/pages/cp-board`, `src/shared/api`, `src/shared/ui`, `src/mocks/inquiries.handlers.ts`, `tests/inquiries-*.test.mjs`, `src/app/router/routes.tsx`, `package.json`.

## 현재 코드와 인접 구현의 사실

- 공용 Axios가 인증 토큰·서버 오류를 처리하고 ApiClient가 성공 envelope를 ApiResult로 변환한다. null data는 undefined가 된다.
- inquiries는 원시 unknown 응답을 parser로 검증한다. 반복 sort에는 `paramsSerializer: { indexes: null }`을 사용한다.
- mutation 성공 시 진행 중 목록·해당 상세를 취소한 뒤 무효화한다. 삭제한 상세는 캐시에서 제거한다.
- 기존 공지 폼은 `cp-notice` mock 전용 NT-숫자 ID, 노출 기간, 메인 노출을 사용한다. 현재 명세에는 이 필드가 없고 type/status/isPinned가 있다.
- 실제 수정 라우트는 `/cp/boards/notices/:noticeId/edit`다. 공지 단독 목록·등록 라우트는 없다.
- `src/shared/ui/choice-chip-group/choice-chip-group.tsx`는 disabled 선택지를 지원한다. 기존 입력·Dialog·폼 View 계약을 유지하며 기능 계층만 연결한다.
- package.json에 test script가 없으며 기존 테스트는 Node test와 tsx 또는 Vite SSR/MSW를 사용한다.

## 불러온 스킬

중앙 snapshot의 skill-index, policy-task-role-routing 및 logic/handoff/pipeline references, policy-git-branch-strategy, policy-coding-convention, policy-data-fetch-layer, policy-type-definition, policy-validation, policy-implementation-quality, policy-documentation, recipe-api-authoring, recipe-data-dto, recipe-data-fetch, reference-custom-hooks를 확인했다.

## 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| ApiClient·Axios·unwrapApiResult | 재사용 | 인증·취소·서버 오류 공통 계약 |
| inquiries query/mutation 구조 | 도메인 내부 동일 패턴 적용 | 목록·해당 상세 최소 갱신과 삭제 race 방지 |
| 기존 공지 폼 View·Dialog | 계약 유지 | UI 역할 소유 파일 변경 없이 지원 필드 연결 |
| 기존 Node test·Vite SSR·MSW | 재사용 | 실제 Axios와 QueryClient 검증 가능 |

## 재사용하지 않은 후보와 이유

legacy news batch/comments/translations는 이번 전체 명세에 없다. cp-notice의 fake draft/publish endpoint와 날짜 필수 검증을 실 API에 사용하지 않는다. 새 query hook을 useApi로 감싸지 않는다.

## 새 자산 필요 여부와 근거

news DTO/parser, query key, query/mutation hook 및 테스트 전용 handler가 필요하다. 공용 hook이나 추상화를 추가하지 않는다.

## 성능·의존성 영향

패키지 추가 없음. 필터·페이지·정렬을 query key에 포함하고 AbortSignal을 전달한다.

## 제약 조건 및 미확인 사항

실서버 호출은 수행하지 않았다. mock 카운트 규칙은 실제 응답 숫자 계산의 근거로 삼지 않는다. 현재 assignment는 owner이며 산출물은 launcher가 지정한 2026-09-08-logic-1e866cae 디렉터리에만 기록한다.
