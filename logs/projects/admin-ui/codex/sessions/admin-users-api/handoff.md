# 사용자·아이템 관리 API 로직 인계

## 요약

확정된 사용자 관리 API 로직과 테스트를 구현했다. 후속 item 요청은 사용자가 확정한 임시 enum·필수 nullable 계약으로 10개 API와 hook까지 구현·검증했다. 사용자 포인트의 미확정 차감 direction 값 확인 후 상수와 테스트를 보완하는 작업은 남아 있다. item의 추후 enum·nullable 강화는 실제 계약 확정 후 수행한다.

- `requested_roles`: logic
- `confirmed_roles`: logic
- `completed_roles`: logic의 확정 계약 구현·검증
- `next_role`: logic
- 역할 근거·승인: 사용자가 user API 로직을 요청하고 2026-09-15 “작업 진행해”로 구현 승인. direction은 사용자 확인 대기, as const 형식은 확정.

## 현재 및 인계 대상 작업 위치

- 작업 공간 이름: `admin-users-shared`
- project: admin-ui
- repository·worktree·실행 디렉터리: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`
- branch: `sy-main`
- HEAD: `52011e5ad746e3c62b7e75b0a3f11cf1472c6c78`
- 직접 부모: 기준 branch이므로 해당 없음
- 확인 기준: 2026-09-15 구현·검증 종료 시점
- 기존 기본 checkout을 그대로 사용한다. 별도 worktree를 생성하지 않았다.
- 후속 작업도 이 공간에서 순차 수행한다. 변경 전 HEAD와 기존 diff를 다시 확인한다.

## 변경 상태

- 새 commit: 없음
- staged: 없음
- unstaged: `src/entities/users/api/index.ts`에 관리자용 client와 export 추가
- untracked: `src/entities/users/api/admin-users.{api,dto,parser}.ts`, `src/entities/users/hook/`, `src/entities/users/index.ts`, `src/entities/users/model/admin-user.enum.ts`, `src/entities/users/model/admin-users-{query-keys,query-options,mutation-options}.ts`, `tests/admin-users-contract.test.mjs`, `tests/admin-users-query-mutation.test.mjs`
- 자기 산출물: `.codex/logs/sessions/admin-users-api/` (Git status에 표시되지 않는 로컬 기록)
- 보존할 변경: 위 구현·테스트 전체. 이전 `/v1/users` API와 기존 타입·store를 수정하지 않는다.

## 후속 logic 작업

1. 사용자에게서 백엔드의 차감 direction 값을 받는다. 현재 상수의 RECHARGE 외 값을 추정하지 않는다.
2. `src/entities/users/model/admin-user.enum.ts`의 `USER_POINT_DIRECTION`에 확인한 값을 추가한다. DTO의 z.enum은 해당 상수에서 자동 추론된다.
3. `tests/admin-users-contract.test.mjs`에서 차감 direction과 양수 amount 조합의 요청 검증을 추가하고, `tests/admin-users-query-mutation.test.mjs`에서 확인된 차감 요청에 대한 409 전달을 검증한다.
4. 관련 테스트·lint·build를 실행하고 자기 세션 기록에 결과를 남긴다.

## 연결 계약·재사용

- 새 public API: `~/entities/users`. hook 목록과 요청 형태는 같은 세션 `final-summary.md`에 기록했다.
- 공용 `apiClient`, `axiosInstance`, `unwrapApiResult`, `withAbortSignal`, 앱 QueryClient 오류 정책과 `news`의 query/mutation 구조를 재사용한다.
- userId는 정수 또는 정수 문자열로 전달한다. publicId와의 매핑이나 사용자 목록 API는 제공된 명세에 없으므로 추가하지 않았다.
- 상태 변경은 ACTIVE/SUSPEND만, 상세 조회는 WITHDRAWN도 지원한다.
- 권한 API는 실제 권한을 바꾸지 않는 no-op이며 string 응답 data만 전달한다.
- UI는 이번 작업 범위에 포함되지 않았다. 후속 화면 위치와 props 계약은 아직 정하지 않았다.

## 검증·승인

- 테스트 20개, lint, build, diff check 통과. 명령과 한계는 `final-summary.md` 참조.
- 실제 백엔드 요청·화면 검증·별도 Watcher 실행은 하지 않았다.
- Git 작업 승인·실행: 없음. commit·병합은 별도 사용자 승인이 필요하다.
- 차감 값 외에는 현재 구현에서 추가 확인 대기 항목이 없다.
- 적용 정책: 현재 snapshot의 task-role-routing, git-branch-strategy, API 작성·코딩·타입·데이터 계층·문서화 스킬.

## 후속 item 구현 인계

- 같은 `admin-users-shared` 공간, `sy-main`, HEAD `52011e5ad746e3c62b7e75b0a3f11cf1472c6c78`에서 작업했다. user와 item 수정은 같은 세션에서 순차 수행했다.
- 수정: `src/entities/items/api/{index,items.api,items.dto}.ts`, `tests/logic-api-contract.test.mjs`, `tests/logic-api-types.test.mjs`.
- 추가: `src/entities/items/api/items.parser.ts`, `src/entities/items/index.ts`, `src/entities/items/model/{query-keys,item-query-options,item-mutation-options}.ts`, `src/entities/items/hook/` 4개 파일, `tests/items-contract.test.mjs`, `tests/items-query-mutation.test.mjs`.
- 모두 미커밋이며 staged 변경은 없다. 앞선 user 변경과 함께 보존한다. Git 작업은 여전히 미승인·미실행이다.
- 현재 공개 계약은 `~/entities/items`의 조회 hook 3개와 변경 hook 7개다. 상세 입력·응답·캐시 규칙은 같은 세션의 `final-summary.md` 하단을 참조한다.
- item 항목·요청 DTO는 필드 필수·값 nullable이며 PATCH도 필드를 생략하지 않는다. 공용화 이후 목록의 items/total/page/size는 필수·non-nullable이다. JSON null은 보존되고, query null은 기존 Axios 방식으로 생략된다. query page/size 필드 자체는 필수이며 null일 때 1/10으로 정규화한다.
- `mainCateogoryId`와 `imageUrl`은 수정 응답의 실제 제공 명세 이름을 유지한다. 이를 상세 응답으로 캐시에 직접 대입하지 않는다.
- 목록의 null data는 공용화 이후 오류로 처리한다. 상세·mutation의 기존 null 응답은 유지하며 빈 객체나 목록으로 변환하지 않는다.
- 검증: 신규 item 20개를 포함한 관련 테스트 48개, lint, build, diff check 통과. 실제 서버 연결·화면 mount는 미검증이며 Query/Mutation observer로 로직을 검증했다.
- 이후 UI 구현자는 새 UI 역할 세션에서 실제 화면·props 계약을 확정하고 hook에 연결한다. 화면 경로·라우트·폼 상태·자동 이미지/ID 매핑은 이 작업에서 정하지 않았다.
- 이후 enum 목록·필수/null 계약을 받으면 logic 역할이 `src/entities/items/api/items.dto.ts`와 계약 테스트를 함께 갱신한다. 기존 과거 item.enum.ts를 새로운 백엔드 enum 근거로 사용하지 않는다.

## 후속 공용 응답 DTO 구현 인계

- 사용자 최종 승인 범위: 기존 추가 통계와 다른 응답 형식은 그대로 유지하며, items/total/page/size인 다섯 도메인만 공용화한다. 일반 배열 조회는 페이지 구조로 바꾸지 않는다.
- 새 공용 자산: `src/shared/api/common/response.dto.ts`의 `ApiResponseDto<TData>`, `PageResponseDto<TItem>`, `createPageResponseSchema`.
- 적용 대상: `src/entities/items/api/items.dto.ts`, `src/entities/users/api/admin-users.dto.ts`, `src/entities/inquiries/api/inquiry.dto.ts`, `src/entities/cp-proposal/api/cp-proposal.dto.ts`, `src/entities/cp-vote/api/cp-vote.dto.ts`.
- items parser는 공용 페이지 필드의 null을 거부한다. cp-proposal 목록 hook은 공용 readonly 배열을 복사해 기존 화면 rows 계약을 유지한다. 다른 화면은 수정하지 않았다.
- 전송 타입 연결: `src/shared/api/api-client.ts`, `src/shared/api/common/api-result/{api-result.mapper,server-response}.ts`. 새 envelope와 기존 정규화 envelope를 함께 받으며 기존 성공·실패·null 처리 동작을 유지한다.
- 검증: 전체34개 파일의 테스트211개, lint, build, diff check 통과. 상세 결과는 최신 final-summary 절을 따른다.
- 같은 worktree·sy-main·HEAD에서 순차 구현했고, staged 변경·새 commit·Git 작업 승인은 없다. 앞선 user·item 변경과 함께 현재 미커밋 변경을 보존한다.
- 이 공용화의 후속 필수 작업은 없다. 새 도메인을 붙일 때 실제 응답이 호환되는 경우에만 새 DTO/schema를 사용한다. 과거 조사 보고서의 미공용화 상태는 당시 기록이며 현재는 다섯 도메인에 적용됐다.
