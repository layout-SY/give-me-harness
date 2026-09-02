# 탐색 기록

## 대상 경로
- `/Users/okand/SynologyDrive/asan-metaverse-user-ui/src/features/citizen-participation/`
- `/Users/okand/SynologyDrive/asan-metaverse-user-ui/src/shared/api/`
- `/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-*/`
- `/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/pages/cp-*/`
- `/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/shared/ui/`
- `/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/mocks/`
- `시민참여v_4.8.pdf` 식별 정보와 `CP_ADMIN_UI_HANDOFF.md` p15~p43 파생 기록

## 발견한 기존 재사용 자산
- 발견 항목: 공용 `ApiClient`, Axios instance, `ApiResult` envelope, TanStack Query provider, 계층형 query key, Zod parser, MSW handler composition
- 재사용 제안: user-ui 시민참여의 `unknown → envelope unwrap → schema parse → query cache` 흐름을 관리자 기준 구조로 사용한다.
- 근거: Dashboard·Proposal 수직 슬라이스가 이미 같은 방향으로 전환됐으며, 나머지 도메인은 실제 적용 범위를 추가 조사 중이다.

## 재사용이 어려운 자산
- 자산: 레거시 `useApi`·`useFetchAdapter`와 page 직접 fixture 소비
- 부적합 사유: TanStack Query cache identity, mutation 후 cache 조정, runtime response validation 계약을 제공하지 않는다.

## 신규 자산 필요성
- 필요 항목: 현재 단계에서는 없음
- 필요 이유: audit-only 단계이며 source code 추가 여부는 도메인별 격차 확인 후 결정한다.

## 초기 확인
- 현재 프로젝트에는 `src/components/`가 없고 공용 UI는 `src/shared/ui/`에 위치한다.
- 인수인계 문서가 식별한 PDF 원본명은 `시민참여v_4.8.pdf`, 관리자 범위는 p15~p43이며 p38 사용자 Mobile 화면은 제외된다.
- 관리자 23개 화면은 구현됐지만 초기 인수인계 기준 API 파일은 골격이고 화면은 fixture로 구동했다.
- 이후 Dashboard와 Proposal은 typed API·Zod·TanStack Query·MSW 수직 슬라이스로 전환됐다.
- TanStack Query v5 공식 기준은 queryFn의 모든 변수를 query key에 포함하고, mutation response로 특정 cache를 갱신할 때 `setQueryData`, 서버 정합성 재확인이 필요할 때 `invalidateQueries`를 사용한다.

## 감사 기준과 용어

- 기준선: 2026-08-20 현재 작업 트리의 on-disk source. 커밋된 HEAD 상태와 혼합하지 않는다.
- 로컬 API operation: `cp-*` API 모듈에 선언된 HTTP method + local path template 한 쌍. 실제 backend endpoint 확정 수를 뜻하지 않는다.
- API 통합: page가 fixture 대신 typed client/query 또는 mutation을 통해 데이터를 소비한다.
- 정적 mock: envelope 조회만 제공하고 상태 전이를 저장하지 않는다.
- stateful behavioral mock: request를 검증하고 mutation이 후속 조회 결과를 변경한다.
- backend contract: OpenAPI/backend DTO로 검증된 경우만 `검증됨`; 현재 CP 계약은 모두 `임시` 또는 `미확정`이다.
- 검증 증거: `자동`, `과거 수동 QA`, `현재 정적 감사`, `없음`으로 구분한다.

## user-ui 기준 흐름

```text
UI
  → useQuery/useMutation
  → 도메인 API client
  → createApiClient(axiosInstance)
  → Axios request interceptor
  → HTTP/MSW
  → Axios response interceptor
  → ServerResponse<T>
  → ApiResult<T>
  → unwrapApiResult
  → Zod parser
  → query cache 또는 mutation callback
```

- query key는 `src/features/citizen-participation/model/queryKeys.ts:6`의 factory로 관리하지만 예외가 있다. 댓글 queryFn은 `page/size/status/myActivity/search/sort` 전체를 사용하면서 key에는 `page`만 포함해 cache collision 위험이 있다.
- query는 `src/features/citizen-participation/hook/useCitizenParticipationQueries.ts:52`에서 `AbortSignal → Axios` 경로를 사용한다.
- mutation은 영향 범위별 cache 정책이 다르며 신고 mutation은 cache 조정이 없다.
- 좋아요는 cancel → snapshot → optimistic `setQueriesData` → 실패 rollback → 서버 결과 재보정 → settled invalidation 순서다.
- 전역 정책은 `staleTime: 30_000`, query retry 1회, mutation retry 0회다.
- feature MSW의 제안·투표·토론·댓글·좋아요 일부는 schema/state store를 사용하지만 범용 action handler는 body 검증이나 상태 저장 없이 성공만 반환한다.
- 개발 MSW는 미처리 요청을 bypass하지만 테스트 서버는 error 처리한다.

### user-ui mutation cache 매트릭스

| mutation | cache 처리 | 근거 |
|---|---|---|
| 제안 등록 | proposal lists, main, me invalidate | `useCitizenParticipationMutations.ts:41` |
| 투표 | 해당 vote detail invalidate | `useCitizenParticipationMutations.ts:56` |
| 설문 응답 | 해당 survey detail invalidate | `useCitizenParticipationMutations.ts:69` |
| 토론 참여 | 해당 discussion detail invalidate | `useCitizenParticipationMutations.ts:82` |
| 댓글 등록 | 해당 content comment root invalidate | `useCitizenParticipationMutations.ts:98` |
| 댓글 좋아요 | optimistic set, rollback, server 보정, settled invalidate | `useCitizenParticipationMutations.ts:113` |
| 신고 | cache 조정 없음 | `useCitizenParticipationMutations.ts:174` |

## admin-ui 도메인 커버리지

| 도메인 | UI 데이터 소스 | client 구조 | mock 수준 | backend 계약 | 검증 증거 |
|---|---|---|---|---|---|
| Dashboard | API 구동 | 통합 | 정적 envelope GET 1 | 임시 | 현재 정적 감사 + 과거 수동 QA |
| Proposal | API 구동 | 통합 | stateful GET 2/POST 1, 400/404 | 임시, 계획된 409 없음 | 현재 정적 감사 + 과거 수동 QA |
| Vote | fixture 구동 | 미통합 raw Axios 골격 | 없음 | 미확정 | 현재 정적 감사 |
| Discussion | fixture 구동 | 미통합 raw Axios 골격 | 없음 | 미확정 | 현재 정적 감사 |
| Policy | fixture 구동 | 미통합 raw Axios 골격 | 없음 | 미확정 | 현재 정적 감사 |
| Survey | fixture 구동 | 미통합 raw Axios 골격 | 없음 | 미확정 | 현재 정적 감사 |
| Comment | 혼합 | page raw mutation만 부분 연결 | 없음 | 미확정 | 현재 정적 감사 |
| Report | fixture 구동 | 미통합 raw Axios 골격 | 없음 | 미확정 | 현재 정적 감사 |
| Board/Notice | fixture 구동 | 미통합 raw Axios 골격 | 없음 | 미확정 | 현재 정적 감사 |
| Activity Log | fixture 구동 | 미통합 raw Axios 골격 | 없음 | 미확정 | 현재 정적 감사 |
| Reward | fixture 구동 | 미통합 raw Axios 골격 | 없음 | 미확정 | 현재 정적 감사 |
| Main Display | fixture 구동 | 미통합 raw Axios 골격 | 없음 | 미확정 | 현재 정적 감사 |
| Operation Policy | fixture 구동 | 미통합 raw Axios 골격 | 없음 | 미확정 | 현재 정적 감사 |

- 14개 `cp-*` API 모듈에는 로컬 API operation 41개가 선언됐고 실제 등록된 CP 업무 MSW handler는 Dashboard 1개와 Proposal 3개, 총 4개다. health handler는 제외한다.
- Dashboard·Proposal 외 API는 대부분 raw `AxiosInstance`와 미정의 request `unknown`/unparsed response 골격이다.
- Dashboard·Proposal의 `ApiClient<unknown> → runtime parser` response 경계는 의도된 안전 패턴이며 결함으로 분류하지 않는다.
- Comment만 fixture 목록과 page의 `useApi.execute` raw 처리 mutation이 혼재한다.
- 대표 근거: `src/entities/cp-proposal/model/use-cp-proposal-process-mutation.ts:15`, `src/entities/cp-vote/api/index.ts:1`, `src/entities/cp-comment/api/index.ts:1`, `src/mocks/handlers.ts:6`.
- admin 프로젝트에는 test script와 CP 자동 계약 테스트가 없어 현재 audit에서 구조 통합을 자동 검증하지 못한다.
- `/cp/*` route는 `CpAdminShell`에 직접 연결되고 `PrivateRoute`/`RoleBasedRoute`로 감싸지지 않는다.

## 인수인계 문서 기반 요구사항 추적

- 원본 식별자: `시민참여v_4.8.pdf`, 관리자 범위 p15~p43.
- 원본 PDF는 현재 저장소에 없고 로컬 Spotlight 검색에서도 발견되지 않았다. PDF 직접 검증은 `BLOCKED`다.
- 직접 확인 가능한 2차 근거는 `CP_ADMIN_UI_HANDOFF.md:14`의 페이지/라우트 매핑과 현재 화면 모델이다.
- p38 사용자 Mobile 화면은 관리자 범위에서 제외한다.

| 2차 근거의 PDF 표기 | 도메인 | 현재 계약 판정 | 핵심 미확정 계약 |
|---|---|---|---|
| p15 | Dashboard | 부분 충족 | KPI response는 typed, 실제 backend 필드명은 미확정 |
| p16 | Main Display | 미충족 | 콘텐츠 ID·순서·노출 여부·publish semantics |
| p17~18 | Proposal | 가장 높은 충족 | endpoint·필드명은 임시 계약, backend 확인 필요 |
| p19~20 | Vote | 미충족 | 상태·기간·결과 공개 request/response |
| p21~22 | Discussion | 미충족 | 상태·기간·공개 기준·결과 response |
| p23~24 | Policy | 미충족 | 처리 단계·반영 내용 payload |
| p25~26 | Survey | 미충족 | 운영 상태·기간·외부 링크 payload |
| p27 | Comment | 부분 충족 | 목록 query/response와 처리 결과 schema |
| p28~29 | Report | 미충족 | 처리·노출 상태·메모 payload |
| p30~31 | Board | 미충족 | 일괄 숨김 IDs, 상세 처리 payload |
| p32~33 | Activity Log | 미충족 | 필터 query·사용자 상세 response |
| p34 | Notice | 미충족 | draft/publish request와 revision |
| p35 | Operation Policy | 미충족 | draft/apply payload·결과 |
| p36~37 | Reward | 미충족 | 정책 수치·지급 단위·idempotency |
| p39~43 | 확인 팝업 5종 | endpoint 골격만 존재 | 각 팝업의 정확한 필드·성공 response |

## Mock의 실서버 유사성

- Dashboard는 공통 envelope를 반환하는 정적 GET mock이다.
- Proposal은 query/body 검증, pagination/filter, stateful mutation, 후속 GET 반영, 400/404를 제공하는 behavioral mock이지만 기존 계획의 409 conflict 계약은 없다.
- 나머지 도메인은 handler가 없어 fixture/placeholder이며 실서버 통신 모사로 볼 수 없다.
- operation별 필요 동작은 다르다. 목록은 query validation/pagination, 상세는 404, mutation은 body validation·상태 전이·필요 시 403/409·후속 조회를 적용하고 비적용 항목은 N/A 근거를 남겨야 한다.
- 실제 backend OpenAPI/DTO가 없으므로 현재 mock이 wire contract와 동일하다고 보증할 수 없다.
- 동일한 local schema를 parser와 MSW가 공유하는 것만으로는 backend 계약 검증이 아니며 OpenAPI 예제나 독립적으로 확보한 익명화 response가 필요하다.

## 로깅 판정

- 두 프로젝트 모두 성공 request/response의 method, route template, status, duration, request ID를 지속적으로 기록하는 애플리케이션 수준 structured telemetry가 없다.
- Axios interceptor는 인증 header 추가, response data unwrap, HTTP 오류 변환을 담당한다.
- `console.error`는 응답 없는 네트워크 오류와 일반 Error만 출력하며 `JSON.stringify(error.request)`는 환경별로 header/URL 등 불필요한 정보 노출 위험이 있어 제거 또는 redaction이 필요하다.
- `useApi`의 `console.warn`은 미처리 오류 계약 경고이며 HTTP traffic log가 아니다.
- `/v1/cp/activity-logs`와 user-ui `/me/activity`는 업무 데이터이며 HTTP request/response logging이 아니다.
- 브라우저 DevTools Network로 일시 확인할 수는 있지만 지속 가능한 애플리케이션 로그나 운영 telemetry는 아니다.
- telemetry를 추가할 경우 Authorization, Cookie, query, request/response body, 사용자 개인정보를 기본 제외하고 method, route template, status, duration, 서버 응답 header에서 받은 request ID, error code만 기록해야 한다.
- client telemetry는 서버의 권한 검사·멱등성·감사 로그를 대체할 수 없다.

## 보안 계약 판정

- `/cp/*` client route guard 부재는 확인됐지만 route guard 자체는 보안 경계가 아니다. 서버가 operation별 CP role/permission과 object-level authorization을 검증해야 한다.
- `pay(targetId)`, publish/apply/bulkHide는 서버가 actor의 대상 리소스·tenant 범위 접근 권한과 현재 처리 가능 상태를 함께 검증해야 한다.
- 현재 `RoleBasedRoute`는 등록된 admin role 중 하나만 있으면 통과하므로 CP 전용 최소 권한 matrix를 대체하지 못한다.
- Bearer token을 `localStorage`에서 읽는 구조는 XSS나 악성 extension이 전제되면 탈취될 수 있다. 확정 취약점으로 단정하지 않고, 보관 방식의 수용 근거와 CSP, 짧은 TTL, rotation/revocation, 더 안전한 cookie/session 방식 전환 가능성을 검토해야 한다.
- authoritative server audit log의 actor는 client payload가 아니라 서버 인증 문맥에서 결정해야 한다.
- 서버 감사 이벤트 최소 필드는 actor, permission, operation, target, result, reason, 이전/이후 revision, request ID, idempotency key/correlation ID, server timestamp다.
- 서버 감사 로그는 접근 권한, 보존 기간, 변조 방지 저장, 조회 추적 기준을 별도 계약으로 가져야 한다.
- client telemetry operation 값은 runtime URL을 정규식으로 가공하지 않고 allowlist된 operation name 또는 정적 route template만 기록해야 한다.
- backend 구현은 확인하지 못했으므로 위 항목은 발견된 서버 취약점이 아니라 출시 전 계약 증거 부재다.

## 결론

- user-ui는 주요 참조 패턴이지만 댓글 query key와 generic MSW 등 known gap이 있다.
- admin-ui의 현재 작업 트리에서 Dashboard·Proposal만 API client/query/MSW 구조가 통합됐으며 backend contract 완료를 뜻하지 않는다.
- 전체 관리자 시민참여가 user-ui와 동일하게 설정됐다고 볼 수 없다.
- PDF 파생 화면 구조는 모델화됐지만 원본 PDF와 backend API request/response 계약은 검증되지 않았다.
- 지속 가능한 성공 HTTP structured telemetry는 현재 설정돼 있지 않다.
