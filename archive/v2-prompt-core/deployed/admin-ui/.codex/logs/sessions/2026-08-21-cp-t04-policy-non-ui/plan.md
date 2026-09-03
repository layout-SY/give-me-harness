# T04 Policy non-UI Closure 계획

## 결론

T04 Closure는 Policy의 non-UI API·캐시·stateful MSW 계약이 독립 Watcher attempt 2에서 `confirmed`(confidence `0.99`)된 사실과, attempt 1의 차단 결과를 함께 보존한다. 이 문서는 제품 코드를 변경하지 않고 Todo 4의 일곱 문서 증빙을 닫는다.

## 범위와 완료 기준

- 대상 operation은 정확히 3개다: `getList` — `GET /v1/cp/policies`, `getDetail` — `GET /v1/cp/policies/:policyId`, `updateProcess` — `POST /v1/cp/policies/:policyId/process`.
- 서버 경계는 `ApiResult<unknown> → unwrapApiResult → Zod`이며, GET은 TanStack `AbortSignal`을 `withAbortSignal`까지 전달한다.
- key/cache는 `all/lists/list/details/detail`, authoritative detail `setQueryData`, Policy list-family만 invalidate하는 범위다.
- UI control·render·route·navigation·visual QA와 실제 backend 호환성·권한·idempotency는 범위 밖이며 완료를 주장하지 않는다.

## 증빙 읽기 순서

1. attempt 1 Watcher가 `PL-003`, `PL-004`의 fixture status 불일치와 과도한 UI import 표현을 `needs-fix`로 판정한 사실을 확인한다. [attempt-1 Watcher](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/watcher/attempt-1/adversarial-verify.json)
2. attempt 2 Generator가 base 4건의 7필드 `28/28` 동일성과 문구 범위 정정을 수행한 결과를 확인한다. [attempt-2 DoneClaim](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/attempt-2/done-claim.json)
3. 독립 fresh Vite+MSW surface의 `confirmed` 판정을 최종 근거로 사용한다. [attempt-2 Watcher](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/watcher/attempt-2/adversarial-verify.json)
4. implementation, quality, cleanup, frozen-path 보존을 원본 증빙과 연결한다. [source review](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/source-review.md) · [quality](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/attempt-2/quality.json) · [cleanup](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/attempt-2/cleanup.json) · [frozen comparison](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/attempt-2/frozen-comparison.json)

## 소유 경계

- 기록 대상 구현 경로는 `src/entities/cp-policy/**`, `src/mocks/cp-policy.handlers.ts`, `src/mocks/handlers.ts`의 Policy 등록이다.
- attempt 2의 실제 제품 변경은 `src/mocks/cp-policy.handlers.ts` 하나이며 frozen write는 `0`이다.
- Claude 소유인 UI/shared/routes/navigation과 시각 검증은 열람·검증·완료 주장 대상이 아니다.

## Closure 산출물

세션 문서 6개와 같은 slug의 portfolio 1개만 작성한다. `.omo`, 활성 계획, ledger, 제품 코드, template, 기존 세션 문서는 수정하지 않는다.
