# T04 Policy non-UI 구현 로그

## 결론

최종 구현은 Policy non-UI 3 operation에 대해 typed DTO/Zod/API/query/mutation과 factory-local stateful MSW를 제공한다. attempt 1의 fixture fidelity 결함은 attempt 2에서 `src/mocks/cp-policy.handlers.ts`만 수정해 폐쇄했다.

## 구현 산출물과 계약

- `getList`는 `GET /v1/cp/policies`, `getDetail`은 `GET /v1/cp/policies/:policyId`, `updateProcess`는 `POST /v1/cp/policies/:policyId/process`다.
- API 반환은 `ApiResult<unknown>`이며 각 호출 경계에서 `unwrapApiResult` 후 Zod parser를 적용한다. GET query의 `signal`은 API와 `withAbortSignal`까지 전달한다.
- query key vocabulary는 `all/lists/list/details/detail`이다. process mutation은 parse된 authoritative detail로 해당 detail만 `setQueryData`하고 Policy list-family만 invalidate한다.
- handler는 정확히 3개(2 GET, 1 POST)이고 factory-local cloned 64-record store를 사용한다. POST는 stage·trim된 `reflectionContent`·관련 progress/history만 갱신하며 status는 보존한다.

구조·cache·Admin Table 경계의 정적 근거는 [source review](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/source-review.md), 세 operation의 direct API 결과는 [operations](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/operations.json)에 연결된다.

## 재시도와 수정

attempt 1 Watcher는 base fixture를 덮어쓴 문제와 DoneClaim UI wording을 blocking/evidence-blocking으로 판정했다. [attempt-1 verdict](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/watcher/attempt-1/adversarial-verify.json)

attempt 2는 base 4건의 source status를 유지하고 60건 생성 record에만 `16/29/15` quota를 적용했다. 따라서 최종 64건 분포는 `18/31/15`이고, `PL-001..PL-004`의 7필드 `28/28` equality가 성립한다. forbidden UI import claim도 신규 API/query/mutation hook 범위로 정정했다. [attempt-2 DoneClaim](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/attempt-2/done-claim.json) · [base equality matrix](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/attempt-2/base-equality-matrix.json)

## 검증·정리 결과

- strict `400`, unknown GET/POST `404`, injected `500`, malformed-success HTTP `200` 후 Zod rejection을 확인했다. [negative statuses](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/negative-status.json)
- POST 뒤 같은 handler store의 list/detail GET은 갱신된 stage·reflection content와 일치하고 status는 변하지 않는다. [stateful follow-up](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/stateful-follow-up.json)
- attempt 2 ESLint, `tsc`, build exit은 모두 `0`; 최대 pure LOC는 `135/250`이다. [quality](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/attempt-2/quality.json)
- attempt 2 server 2개와 browser context 2개를 정리했고 port `4221`, `4222`를 해제했으며 shared `4173`은 보존했다. [cleanup](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/attempt-2/cleanup.json)

## 소유 경계와 리스크

UI controls/render/routes/navigation/visual QA는 구현·검증하지 않았다. actual backend compatibility, permission, idempotency도 이 local provisional MSW contract로부터 도출할 수 없다.
