# 계획

## 목표

시민참여 모바일 13개 화면을 mock backend로 사용할 수 있도록 FSD 기반의 typed Axios API, DTO/parser, TanStack Query, MSW, RHF/Zod form, route 계약을 구현하고 Claude Code가 제작한 UI에 안전하게 연결한다.

## 범위

1. `@tanstack/react-query`, `react-hook-form`, `zod`, `@hookform/resolvers`, `msw` 의존성과 QueryClient/MSW 개발 진입점을 추가한다.
2. 배너, 공지, 제안, 투표, 토론, 정책반영, 설문조사, 댓글, 신고, 내 활동 도메인의 DTO·parser·API·query key를 정의한다.
3. 목록/상세 query, 생성·투표·참여·설문 제출·좋아요·댓글·신고 mutation과 캐시 무효화를 구현한다.
4. 제안 작성 form schema와 form payload → request DTO mapper를 구현한다.
5. 모바일 route와 URL query 계약을 추가하고 Claude Code UI props/callback 계약을 제공한다.
6. MSW handler와 fixture가 loading·empty·error·상태별 응답 및 pagination을 재현하도록 한다.

## 제외 사항

- 반응형과 전역 모바일 스타일, production UI 마크업·CSS·자산
- 사용자 Mobile 13개 화면과 모바일 신고 팝업 외의 모든 화면·기능
- 실제 backend 구현과 운영 인증 방식
- 승인 전에 애플리케이션 소스 또는 `package.json` 변경

## 제약 조건

- API 파일은 `api/<도메인>/<도메인>.api.ts`, factory는 `<도메인>Api`, 메서드는 `<HTTP메서드><도메인><대상>` 형태를 사용한다. 예: `proposalApi`, `getProposalList`, `postProposal`.
- `ApiClient`/`ApiResult`는 전송 경계로 유지한다. query 함수는 실패 결과를 throw 가능한 typed error로 변환해 TanStack Query가 오류 상태를 소유하게 한다.
- 신규 query hook을 `useApi`로 감싸지 않는다. 이중 loading/cancel/error 처리를 방지한다.
- 상태는 `as const` 객체와 파생 union으로 정의하고 UI 노출 label과 서버 wire value를 분리한다.
- query key에는 결과에 영향을 주는 route id, filter, search, sort, page를 모두 포함한다.
- mutation 성공 시 영향을 받은 detail/list/main/my-activity key만 무효화한다. 사용자 직접 갱신은 해당 query의 `refetch`를 사용한다.
- route 이동은 component state 대신 URL을 사용한다.

## 제안 FSD 및 파일 계약

```text
src/
  app/providers/query-client.ts
  app/mocks/start-mocks.ts
  shared/api/unwrap-api-result.ts
  shared/config/citizen-participation-routes.ts
  shared/mocks/browser.ts
  shared/mocks/handlers.ts
  entities/citizen-participation/{banner,notice,proposal,vote,discussion,policy,survey,comment,report,me}/
    api/<domain>/<domain>.api.ts
    api/<domain>/<domain>.dto.ts
    api/<domain>/<domain>.parser.ts
    model/<domain>.constants.ts
    model/<domain>.types.ts
  features/citizen-participation/*/model/use-*.ts
  features/citizen-participation/create-proposal/model/proposal-form.schema.ts
  features/citizen-participation/create-proposal/model/to-create-proposal-request.ts
  pages/citizen-participation/*
```

도메인별 API factory는 `ApiClient`를 인자로 받고 메서드 객체를 반환한다. 기존 예시의 거대한 전역 `api` 객체 및 `daoModule` spread 조합은 사용하지 않는다. 전역 service locator는 tree-shaking과 소유권을 흐리고 도메인 충돌을 숨기므로 query/mutation이 필요한 factory를 직접 import한다.

## route 계약 권고안

| 화면 | route |
| --- | --- |
| 메인 | `/citizen-participation` |
| 제안 | `/citizen-participation/proposals`, `/proposals/:proposalId`, `/proposals/new` |
| 투표 | `/citizen-participation/votes`, `/votes/:voteId` |
| 토론 | `/citizen-participation/discussions`, `/discussions/:discussionId` |
| 정책반영 | `/citizen-participation/policies`, `/policies/:policyId` |
| 설문조사 | `/citizen-participation/surveys`, `/surveys/:surveyId` |
| 내 활동 | `/citizen-participation/me/activity?type=all|proposal|vote|discussion|policy|survey` |

목록 조건은 URL query에 둔다. 예: `?myActivity=true&status=reviewing&page=1`, `?status=open&search=...&sort=latest&page=1`. 상세 route parameter는 문자열로 parse한 뒤 DTO 경계에서 backend id 타입으로 변환한다.

## API·query 계약 초안

| 도메인 | operation | query key / 무효화 |
| --- | --- | --- |
| main/banner/notice | 메인 집계, 배너, 공지 조회 | `['citizenParticipation','main']` 및 하위 key |
| proposal | 목록·상세·생성 | list(filters), detail(id); 생성 후 lists/main/me |
| vote | 목록·상세·투표·좋아요 | list(filters), detail(id), comments(id,page); mutation 후 detail/list/me |
| discussion | 목록·상세·참여·좋아요 | vote와 동일한 독립 key |
| policy | 목록·상세 | list(filters), detail(id), comments(id,page) |
| survey | 목록·상세·응답 제출 | list(search/sort/status/page), detail(id); 제출 후 detail/list/me |
| comment | 대상별 목록·작성·좋아요 | comments(targetType,targetId,page); mutation 후 해당 comments/detail |
| report | 신고 제출 | 성공 후 대상 detail 또는 comments 무효화 |
| me | 프로필·유형별 활동 | profile, activity(type,page) |

DTO는 `ListQueryDto`, `ListItemDto`, `DetailDto`, mutation `RequestDto`/`ResponseDto`를 분리한다. UI 모델은 parser가 알 수 없는 외부 값을 검사한 뒤 생성하며, mock도 실제 서버 envelope와 같은 `ServerResponse<T>`를 반환한다.

## MSW 계획

- `src/shared/mocks/browser.ts`에서 `setupWorker(...handlers)`를 구성한다.
- 개발 entry에서 선택된 mock mode일 때만 동적 import 후 `worker.start()` 완료 뒤 React를 mount한다.
- handler는 path parameter와 `URL.searchParams`를 검증하고 fixture를 필터·정렬·paginate한다.
- 공통 fixture에 status별 제안/투표/토론/정책/설문과 댓글 데이터를 둔다.
- 미처리 요청은 개발 중 계약 누락을 발견할 수 있도록 경고한다. 테스트에서는 handler reset 경계를 둔다.

## RHF/Zod 계획

- Zod schema를 validation의 단일 소스로 두고 `zodResolver`로 RHF에 연결한다.
- schema input/output과 API request DTO를 동일 타입으로 간주하지 않고 mapper에서 허용 필드만 명시적으로 옮긴다.
- 오류 text와 field 연결은 Claude Code UI 계약으로 제공한다.
- 필드별 필수 여부, 길이, 첨부 제한은 사용자 결정 또는 backend 계약 확보 후 확정한다.

## Claude Code UI 인계 계약

- Claude Code는 페이지 2–14와 모바일 신고 팝업의 production UI를 소유한다.
- 재사용 검토 대상은 service tabs, status/category badge, 콘텐츠 카드 shell, 투표 결과 그래프, comment card/pagination, filter/search/sort control, form field/error, confirm/report popup이다.
- Hephaestus는 각 화면에 `data`, `isPending`, `isFetching`, `error`, pagination 값과 typed callback을 제공한다.
- hook/util 구현 후 사용자에게 `Claude Code의 UI 작업이 완료되었나요?`를 확인한다. 확인 전 production UI에는 연결하지 않는다.
- 확인 후 최신 UI 파일을 다시 읽고 props/callback 경계만 연결한다.

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 계약 확정 | 사용자 + Hephaestus | `policy-type-definition`, `recipe-data-dto` | endpoint/envelope/status/pagination 결정 |
| transport·DTO·parser | Hephaestus | `api-authoring`, `policy-data-fetch-layer` | typed API와 검증된 도메인 모델 |
| query·mutation·form | Hephaestus | `recipe-data-fetch`, `policy-validation` | 캐시·상태·form 동작 |
| MSW | Hephaestus | `api-authoring` | 실제 계약과 동일한 mock server |
| production UI | Claude Code | `project-ui`, `reference-components` | 모바일 화면과 재사용 UI |
| route·통합 | Hephaestus | `policy-coding-convention` | URL 기반 화면 이동과 UI 연결 |
| 검토 | Watcher / Evaluator | `policy-review-checklist` | 현재 변경 판정 및 장기 권고 |

## 구현 순서

1. 승인된 서버 계약과 route/status vocabulary를 문서화한다.
2. 의존성, QueryClient provider, 개발 전용 MSW bootstrap을 추가한다.
3. 공통 API result unwrap과 pagination DTO를 추가한다.
4. main/proposal/notice/banner/me의 API·query·fixture를 구현한다.
5. vote/discussion/policy/survey/comment/report의 API·query·mutation·fixture를 구현한다.
6. proposal form schema와 mapper를 구현한다.
7. route와 page orchestration을 추가하되 production UI 연결 전 Claude Code 완료를 확인한다.
8. 최신 UI에 typed props/callback을 연결한다.
9. 최소 동작 테스트, `npm run build`, `npm run lint`를 실행하고 Watcher/Evaluator 문서를 갱신한다.

## 검증

- 변경된 API/parser/query/form 경계에 중요한 상태·필터·mutation 무효화 테스트를 최소한으로 추가한다.
- MSW를 통해 목록 조회, URL filter, 상세 조회, 생성/투표/댓글, 오류 응답을 실제 Axios 표면으로 실행한다.
- `npm run build`, `npm run lint`를 실행한다.
- 프로젝트 규칙에 따라 시각 QA, screenshot, browser capture는 수행하지 않는다.

## 위험 요소 및 결정 사항

승인 전에 다음을 선택해야 한다.

1. **endpoint namespace**: 권고안 `/v1/api/citizen-participation`; 실제 backend 예정 경로가 있으면 그 값을 사용한다.
2. **응답 envelope**: 권고안은 현재 `ServerResponse<T>`/`ApiResult<T>` 유지다. raw Axios `data` 직접 반환으로 이원화하지 않는다.
3. **인증**: 모든 시민참여 요청에 `authRequired: true`인지, 공개 조회/인증 mutation으로 구분하는지 확인이 필요하다.
4. **pagination**: 권고안은 1-based `page`, `pageSize`, 응답 `items`, `itemCount`, `pageCount`다.
5. **mock mode**: 권고안은 `VITE_ENABLE_MSW=true`에서만 시작하여 실제 backend 연결을 방해하지 않는 방식이다.
6. **상태 vocabulary**: 제안·투표·토론·정책·설문별 wire value와 사용자 화면에서 허용할 동작이 필요하다.
7. **제안 작성 규칙**: 제목/내용/카테고리/첨부 필수 여부와 길이·개수 제한이 필요하다.
8. **투표/토론/설문 중복 제출**: backend가 idempotency 또는 409를 보장하는지 확인이 필요하다.
9. **내 활동**: 권고안은 단일 endpoint의 `type` filter이며, 유형별 endpoint가 예정되어 있으면 query factory만 분리한다.

## 승인

- 상태: approved and logic implementation completed
- Production UI 통합: Claude Code 완료 확인 대기
- 필수 문구: `이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?`
