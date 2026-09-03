# 포트폴리오 경험 기록 — T04 Policy non-UI

## 작업 개요

- **구현/수정 내용:** Policy의 `GET /v1/cp/policies`, `GET /v1/cp/policies/:policyId`, `POST /v1/cp/policies/:policyId/process` local provisional client/MSW contract를 완료하고, first-review 결함을 수정 후 독립 검증으로 폐쇄했다.
- **구현 이유:** 2 GET+1 POST가 typed response boundary, stateful follow-up, strict failure, cache ownership을 갖는지 UI와 분리해 보장하기 위해서다.
- **작업 유형:** non-UI API/DTO/Zod/query/mutation/stateful MSW 구현 및 독립 Watcher 재검토.

## 문제 상황

- **문제 출처:** 독립 Watcher attempt 1의 direct API 검증.
- **대상 도메인·서비스:** CP Policy의 local provisional API/MSW contract.
- **기존 문제와 영향:** 64건 status aggregate는 맞았지만 seed 생성이 `PL-003`, `PL-004` status를 fixture와 다르게 덮어써 base 4건 × 7필드 조건을 만족하지 못했다. 또한 기존 type import가 남은 상태에서 DoneClaim이 entity 전체 UI import `0`처럼 표현돼 source truth와 범위가 달랐다. [attempt-1 evidence](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/watcher/attempt-1/adversarial-verify.json)

## 요구사항 및 의사결정

- **사용자 요구·제안:** first-review 실패와 retry를 보존하고, 3 operation, `ApiResult<unknown> → unwrapApiResult → Zod`, state/cache, quality, ownership, provisional risk를 증빙 링크로 닫는다.
- **에이전트 제안:** base fixture fidelity를 field matrix로 검증하고 UI import 표현은 새 API/query/mutation hook 범위로 제한한다.

| 접근법 | 장점 | 단점 | 선택 여부와 이유 |
|---|---|---|---|
| base 4건에도 status quota 적용 유지 | 64건 분포 계산이 단순 | fixture source fidelity를 깨고 Watcher blocker를 해소하지 못함 | 미채택 — `PL-003`, `PL-004` mismatch가 실제로 확인됨 |
| base status 보존, 생성 60건에만 quota 적용 | fixture fidelity와 64건 분포를 함께 유지 | seed 분포 계산을 분리해야 함 | 채택 — base `28/28` equality와 `18/31/15`을 함께 확인 |
| entity 전체 UI import 0으로 계속 표기 | 짧은 claim | 기존 type-only import와 충돌해 증빙 신뢰도를 낮춤 | 미채택 — 실제 소스 범위와 다름 |
| 신규 API/query/mutation hook의 forbidden import만 검토 | UI side-effect 경계를 정확히 설명 | 기존 domain type import는 별도로 설명해야 함 | 채택 — `Table`·`useApi`·navigation 등 새 hook 경로 `0`을 정확히 기록 |

## 사용 기술과 구체적 목적

| 기술/패턴/아키텍처 | 해결하려는 문제 | 적용 위치와 목적 | 미채택 대안/이유 |
|---|---|---|---|
| `ApiResult<unknown> → unwrapApiResult → Zod` | failure/malformed success의 조용한 성공 방지 | Policy API와 query/mutation response boundary | parse 전 cast — contract failure를 숨길 수 있어 미채택 |
| TanStack query key/cache | Policy cache scope를 domain-local로 제한 | `all/lists/list/details/detail`, authoritative detail cache 및 lists-only invalidation | cross-domain invalidation — 실제 영향 범위를 넘어서 미채택 |
| `AbortSignal` + `withAbortSignal` | GET cancellation 전달 | TanStack query signal을 Policy GET API까지 전달 | 별도 mutation AbortController — non-optimistic sibling convention과 달라 미채택 |
| factory-local stateful MSW | POST 후속 GET과 context isolation 검증 | factory별 독립 64-record store | shared mutable store — state leakage 위험으로 미채택 |

## 적용 내용

- attempt 2에서 `src/mocks/cp-policy.handlers.ts`만 수정해 base 4건은 source status를 보존하고 생성 60건에 quota를 적용했다.
- `getList`, `getDetail`, `updateProcess`는 1:1 handler로 동작하며 POST 후 동일 session의 list/detail은 authoritative detail과 일치한다.
- strict query/body `400`, unknown ID `404`, injected `500`, HTTP `200` malformed success의 Zod rejection, GET AbortError를 검증했다.
- **AI 하네스 변경:** 없음. UI controls/render/routes/visual QA도 구현하거나 검증하지 않았다.

구현 범위와 static review는 [source review](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/source-review.md), mutation follow-up은 [stateful evidence](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/stateful-follow-up.json), retry 결과는 [attempt-2 DoneClaim](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/attempt-2/done-claim.json)에 근거한다.

## 결과 및 성과

- **before/after:** before는 attempt 1에서 base fields 일부가 불일치해 Watcher `needs-fix`였고, after는 4 record × 7 field `28/28` equality와 64 total(`REFLECTED 18`, `REVIEWING 31`, `SCHEDULED 15`)을 독립 Watcher가 확인해 `confirmed`(confidence `0.99`)가 됐다. 이는 observed evidence만 반영한 변화다.
- **검증 결과:** normal unhandled CP `0`; ESLint/tsc/build exit `0`; max pure LOC `135/250`; frozen writes `0`; cleanup에서 shared `4173` 보존 및 attempt 2 server/browser/temp artifact 정리를 확인했다. [independent verification](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/watcher/attempt-2/adversarial-verify.json) · [quality](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/attempt-2/quality.json) · [cleanup](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/attempt-2/cleanup.json)
- **사용자 후속 피드백:** 제공되지 않았다.
- **잔여 리스크:** actual backend compatibility, permission, idempotency는 검증되지 않았고 UI completion은 Claude-owned다. frozen historical baseline drift도 T04와 분리해 계속 추적해야 한다.

## 회고

- **잘된 판단:** aggregate count만으로 fixture fidelity를 추론하지 않고 Watcher의 field-by-field failure를 blocker로 유지한 점이다. 수정 뒤 같은 독립 기준으로 `28/28`을 재확인했다.
- **다시 한다면 바꿀 점:** 최초 DoneClaim부터 “신규 API/query/mutation hook의 forbidden import”처럼 검토 범위를 명시해 type-only legacy import와 혼동되지 않게 작성한다.
- **다음 작업에 적용할 인사이트:** stateful MSW seed에는 aggregate 분포와 source fixture fidelity를 별도 invariant로 두고, Closure에는 UI 소유권·backend provisional risk를 pass claim과 분리해 기록한다.
