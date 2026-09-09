# 탐색

## 결론

현재 소스는 미변경이며 `/v1/news`는 사용처가 없다. 사용자가 이전 세션에서 제공한 전체 명세 원문을 해당 세션 history에서 확인했다. 기존 inquiries의 ApiClient·Zod·TanStack Query·MSW 패턴을 news에 적용한다.

## 현재 확인한 근거

- `git status --short --branch`, `git log`, branch metadata: clean, 시작 HEAD와 V3 계약 일치.
- 이전 `2026-09-08-logic-1e866cae` handoff: 구현 승인 완료, 소스 적용 전 중앙 이벤트 처리 결함으로 중단. 현재 bundle은 80bc872b88c3c486이며 gate 세 항목이 true로 등록됨.
- `src/entities/inquiries/api`, hook, query-keys, mutation-options: unknown 응답 parser, AbortSignal, 반복 sort, 대상 상세와 목록의 취소·무효화, 삭제 상세 제거.
- `src/shared/api`: null 성공 data를 undefined로 정규화하므로 news mutation parser는 둘을 void로 수용한다.
- `src/shared/ui/choice-chip-group`: 선택지 disabled 지원. 기존 폼 View와 popup 계약도 확인했다.
- `src/pages/cp-board` 폼: 현재 NT-형식 mock ID, 작성자·기간·메인 노출을 사용하는데 API 명세에는 해당 필드가 없다. 유형·상단고정 UI도 없다.
- 기존 tests는 Node test, tsx, Vite SSR와 MSW를 사용하며 package.json에 test script는 없다.

## 스킬과 재사용 판단

중앙 snapshot의 task-role-routing 및 logic/handoff/pipeline references, git-branch-strategy, skill-index, coding-convention, type-definition, data-fetch-layer, validation, implementation-quality, documentation, api-authoring, data-dto, data-fetch, reference-custom-hooks를 읽었다.

ApiClient·unwrapApiResult·Axios 인증/오류 처리를 재사용한다. news 내부 query key/DTO/parser는 서버 계약이 다르므로 별도로 만든다. useApi로 query를 감싸지 않는다. 공용 훅 신설 없이 news 훅이 요청 취소와 캐시를, 폼 process가 편집 상태와 제출 부수 효과를 소유한다.

## 명세 제약

목록은 totalElements/totalPages/pinnedItemCount와 items 순서를 그대로 반환한다. by/keyword 동시 입력, page/size 기본값 1/20, sort 반복 파라미터를 적용한다. 생성 필드 5개는 필수이고 PATCH 필드는 선택이다. soft delete 이후 상세·중복 삭제는 NEWS_NOT_FOUND다. 집계값과 고정 목록의 계산 관계는 명세만으로 확정하지 않으므로 프런트에서 재계산하지 않는다.
