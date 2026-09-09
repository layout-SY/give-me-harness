# T04 Policy non-UI 탐색 기록

## 결론

근거는 attempt 1의 차단 결과를 삭제하거나 대체하지 않고, attempt 2의 수정·독립 재검증으로 폐쇄한다. 최종 판정은 Watcher attempt 2 `confirmed`, confidence `0.99`다.

## 확인한 계약

- direct API는 2 GET과 1 POST이며 정상 세션의 unhandled `/v1/cp/` 요청은 `0`이다.
- 64건의 목록 상태 분포는 `REFLECTED 18`, `REVIEWING 31`, `SCHEDULED 15`다.
- base `PL-001..PL-004`는 `id/status/title/department/stage/registeredAt/reflectionContent` 7필드, 총 `28/28`가 fixture와 동일하다.
- handler factory는 호출마다 독립적인 stateful store를 만들고, POST 후 같은 세션의 list/detail GET이 authoritative 응답과 일치한다.

## attempt 1 실패 보존

Watcher attempt 1은 `needs-fix`로 두 blocker를 기록했다.

1. `T04-POLICY-BASE-FIDELITY-001`: seed 생성이 `PL-003`, `PL-004`의 `REVIEWING`을 `REFLECTED`로 덮어써 7필드 보존 조건을 위반했다.
2. `T04-POLICY-DONE-CLAIM-UI-WORDING-002`: 기존 `StatusBadgeColor` type import가 남아 있는데 DoneClaim의 `entityUiImports: 0` 표현이 전 도메인 범위처럼 과도했다.

재현 요청, 실제 mismatch, 수정 요구는 [attempt-1 Watcher](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/watcher/attempt-1/adversarial-verify.json)에 보존된다. attempt 2는 base record의 source status를 유지하고 신규 생성 60건에만 quota를 적용했으며, forbidden import 판정을 새 API/query/mutation hook으로 제한했다. [attempt-2 DoneClaim](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/attempt-2/done-claim.json)

## 구현·검증 근거

- operation 상태, pagination, filter 및 KPI 계산 규칙: [operations](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/operations.json)
- POST 후 list/detail 일치와 status 불변: [stateful follow-up](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/stateful-follow-up.json)
- strict query/body `400`, unknown ID `404`, injected `500`, HTTP 200 malformed success의 parser 거절: [negative statuses](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/negative-status.json)
- query/cache·parser·handler 1:1·factory-local store에 대한 정적 점검: [source review](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/source-review.md)
- fresh surface의 재현 및 base `28/28`: [attempt-2 Watcher](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/watcher/attempt-2/adversarial-verify.json)

## 탐색 결론과 미확인 범위

이 탐색은 local provisional client/MSW contract만 다룬다. 실제 backend endpoint/envelope 호환성, 인증·권한, production idempotency는 검증하지 않았다. UI controls·render·routes·visual QA도 구현하거나 검증하지 않았다.
