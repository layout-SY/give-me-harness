# 탐색 기록

## 대상 경로
- 기존 Generator: [done-claim](../../../../.omo/evidence/cp-admin-api-remediation/t03/generator/done-claim.json), [provisional contract](../../../../.omo/evidence/cp-admin-api-remediation/t03/generator/provisional-contract.md), [runtime results](../../../../.omo/evidence/cp-admin-api-remediation/t03/generator/e2e/results.json)
- 독립 Watcher: [attempt-3 adversarial verify](../../../../.omo/evidence/cp-admin-api-remediation/t03/watcher/attempt-3/adversarial-verify.json)
- 후속 UI 참고: [attempt-4 done claim](../../../../.omo/evidence/cp-admin-api-remediation/t03/generator/attempt-4/done-claim.json), [deferred risks](../../../../.omo/evidence/cp-admin-api-remediation/t03/generator/attempt-4/deferred-risks.md)
- 정책/템플릿: `policy-documentation`, `policy-portfolio`, `.codex/templates/*`

## 발견한 기존 재사용 자산
- `ApiResult<unknown> → unwrapApiResult → Zod` 경계와 operation별 `AbortSignal` 전달 계약.
- list/detail query key 분리와 mutation 성공 시 일치 detail `setQueryData` + list-only invalidation.
- factory invocation마다 복제되는 4-item Discussion store와 same-session 후속 GET 증거.
- 재사용 제안: 이번 작업은 구현이 아니라 기존 증거 링크를 단일 closure index로 묶는 방식만 재사용했다.

## 사실 분류
### Source-confirmed
- 3 operations: `GET list`, `GET detail`, `POST process`.
- strict query/body schema, complete list/detail keys, domain-local cache scope, 4-item isolated store, exact-one handler registration.
- 모든 client operation의 `ApiResult<unknown>` 반환, unwrap 후 Zod parse, `AbortSignal` 인자/전달 계약.

### Runtime-measured
- strict query/body `400`, unknown GET/POST `404`, injected failure `500`.
- malformed-success HTTP `200` payload의 Zod rejection.
- mutation 후 같은 handler store의 detail/list GET 일치, fresh normal session unhandled CP `0`.
- scoped ESLint, `tsc`, build exit `0`; pure LOC 최대 `168 <= 250`.

## 재사용이 어려운 자산
- attempt 4의 UI/visual 결과는 더 늦은 UI 작업을 포함할 수 있어 non-UI closure의 완료 근거로 합산하지 않는다.
- shared navigation/global contrast finding은 T03 local non-UI 범위 밖이다.

## 신규 자산 필요성
- [evidence-index.json](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t03/closure/evidence-index.json): source/runtime 사실과 출처를 기계 판독 가능하게 통합.
- [handoff-boundary.md](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t03/closure/handoff-boundary.md): Claude 소유권과 미완료 visual blocker를 명시.
- [frozen-path-manifest.json](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t03/closure/frozen-path-manifest.json): ownership 결정 후 baseline 고정.
- `reusable-assets`: N/A — 제품 재사용 자산을 만들거나 수정하지 않는 문서 종료 작업이다.
