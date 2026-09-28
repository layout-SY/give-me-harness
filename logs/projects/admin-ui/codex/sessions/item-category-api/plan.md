# 아이템 카테고리 API 연결

## 범위와 확정 계약

- 역할: logic, owner. 최초 요청의 “기존 API 연결 패턴 … 작업 진행해” 승인과 후속 계약 답변에 따라 구현한다.
- 위치: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`, `sy-main`, HEAD `efccd76b10a89e49e2c3f7a5c8c59326e6b6c3f3`.
- `/admin/items/categories` GET·POST, `/{categoryId}` PATCH·DELETE를 기존 items entity에서 제공한다. DTO·parser·TanStack Query options·hook·public export와 테스트를 포함한다.
- 모든 요청·응답 필드는 필수다. `name`, `id`는 명세 타입을 유지하고 부모 없는 요청의 `parentCatrgoryName`과 응답의 `parentName`은 null을 허용한다. 부모 필드도 생략할 수 없다.
- 조회 data는 배열 또는 null, 변경 data는 문자열 또는 null이다. null을 빈 배열·빈 문자열로 바꾸지 않는다. `parentCatrgoryName` 철자를 그대로 보존한다.
- categoryId는 명세의 필수 int64다. 기존 item의 int64 검증을 같은 숫자 형식의 검증에만 재사용하며 itemId와 categoryId를 서로 매핑하지 않는다.
- 명세가 없는 대분류·소분류 변환, 부모 ID 추론, 화면·폼·앱용 mock은 추가하지 않는다. src/pages·src/features에서 기존 카테고리 API 호출부는 확인되지 않았다.
- 기존 인증 관련 미커밋 변경은 보존한다. Git 변경은 요청·승인 범위에 없다.

## 재사용과 영향

- `src/entities/items/api/items.api.ts`, `items.dto.ts`, `items.parser.ts`: ApiClient factory·Zod 검증·응답 data parser·int64 검증.
- `src/entities/items/model/{query-keys,item-query-options,item-mutation-options}.ts`, `hook/`: query·mutation options, 요청 취소, 성공 후 캐시 무효화, 얇은 hook.
- `src/shared/api/{api-client,axios-instance,with-abort-signal}.ts`, `common/api-result/`, `common/response.dto.ts`: 인증·envelope·실패·취소 공용 처리.
- `src/entities/items/api/item-category.api.ts`, `item.category.dto.ts`: 사용되지 않는 이전 /v1/object-categories 계약을 새 명세로 교체한다. 이전 parentId 변환 테스트는 새 필드·원본 보존·인증·응답 검증으로 대체한다.
- 생성은 카테고리 목록을 취소·무효화한다. 수정·삭제는 categoryName과 카테고리 ID에 의존하는 items 조회 전체를 취소·무효화한다. 서버 문자열 응답으로 영향받은 item ID를 추측하거나 item 캐시를 직접 수정하지 않는다.
- 기존 PubSub의 사용되지 않는 카테고리 이벤트 계약은 현재 API 호출 흐름 밖이므로 변경하지 않는다.

## 수행 순서와 완료 기준

- [x] `src/entities/items/api/`에서 확정된 DTO·전송·parser를 구현한다.
- [x] 같은 entity의 model·hook·public export에서 조회와 변경 결과, 취소·갱신을 연결한다.
- [x] `tests/`에서 필수·nullable·int64·정확한 요청 필드와 원본 보존을 검증한다. 기존 Node test·tsx·Vite SSR·MSW로 실제 Axios·Query/Mutation observer 상태와 캐시·실패·취소를 검증한다.
- [x] 공통 포맷 트리거 실행 후 관련 테스트, lint, build, diff 확인을 실행한다.
- [x] `.codex/logs/sessions/item-category-api/final-summary.md`에 결과와 한계를 기록한다.

## 적용 스킬

중앙 snapshot의 task-role-routing, git-branch-strategy, skill-index, coding-convention, type-definition, data-fetch-layer, implementation-quality, documentation, api-authoring을 읽고 적용했다. 공통 역할 문서 logic·handoff-and-ownership·pipeline-roles도 확인했다.

## 검증 완료

이전 세션이 자신의 종료된 쓰기 기록을 복구했고 후속 문서 작업도 종료됐다. 현재 worktree의 writes가 비어 있음을 확인한 후 공통 포맷 트리거로 자신의 코드·테스트 13개 파일을 포맷했다. 관련 테스트 46개(카테고리 15개 포함), lint, build, diff check 모두 통과했다. 이번 세션에서 Git 변경은 실행하지 않았다. 상세 검증 결과와 실제 서버 미검증 한계는 final-summary에 기록했다.
