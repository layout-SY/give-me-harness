# T04 Policy non-UI 리뷰 로그

## 결론

리뷰는 2회 수행됐다. attempt 1은 `needs-fix`, attempt 2는 독립 fresh Vite+MSW context에서 `confirmed`(confidence `0.99`)다. 따라서 첫 판정은 실패 이력으로 보존하고, 두 blocker가 닫힌 범위에서만 pass로 기록한다.

## attempt 1 — fail / needs-fix

- **base fidelity 차단**: `PL-003`, `PL-004`의 status가 fixture `REVIEWING` 대신 `REFLECTED`로 관측됐다. 요구사항인 4 record × 7 field equality를 충족하지 못했다.
- **증빙 표현 차단**: 기존 `src/entities/cp-policy/model/types.ts`의 `StatusBadgeColor` import가 남아 있으므로, `entityUiImports: 0`을 전 entity 범위에 대한 절대 주장으로 쓸 수 없었다.
- 나머지 3 operation, parser/abort/cache 및 quality는 통과했지만 stale-state와 misleading-success 항목이 실패해 전체 verdict는 pass가 아니다.

상세 재현과 blocking ID는 [attempt-1 Watcher verdict](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/watcher/attempt-1/adversarial-verify.json)에 원문으로 남아 있다.

## attempt 2 — pass / confirmed

- base 4건의 7필드가 `28/28` 동일하고 `PL-003`, `PL-004` status가 `REVIEWING`임을 fresh surface에서 확인했다.
- 3 operation은 1:1 handler, `all/lists/list/details/detail` key, `signal → API → withAbortSignal → unwrapApiResult → Zod`, authoritative detail cache + lists-only invalidation을 만족했다.
- invalid query 7종과 invalid body 5종은 `400`, unknown POST/detail은 `404`, list/detail/POST injected failure는 `500`, malformed success는 HTTP `200` 뒤 ZodError였다. 정상 unhandled CP는 `0`이다.
- factory-local state가 독립 context에서 초기 stage를 다시 보였고 POST 후 list/detail은 일치했다.

독립 검증의 원문은 [attempt-2 Watcher verdict](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/watcher/attempt-2/adversarial-verify.json), 수정 완료 주장은 [attempt-2 DoneClaim](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/attempt-2/done-claim.json)에 연결된다.

## 품질·범위 판정

- ESLint, `yarn tsc -b --pretty false`, `yarn build` exit은 모두 `0`; max pure LOC는 `135/250`이다. TypeScript LSP는 기존 설치 거절로 N/A다. [quality evidence](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/attempt-2/quality.json)
- frozen writes `0`, UI/shared/package/route writes `0`, attempt 2 start/end frozen digest는 동일하다. [frozen comparison](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/attempt-2/frozen-comparison.json)
- UI control·render·route·visual QA와 actual backend compatibility/permission/idempotency는 검사·pass 대상이 아니다.
