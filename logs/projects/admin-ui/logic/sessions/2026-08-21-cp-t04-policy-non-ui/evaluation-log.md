# T04 Policy non-UI 평가 로그

## 결론

T04의 non-UI 계약은 attempt 2에서 독립 확인됐지만, closure는 local provisional contract의 경계를 유지해야 한다. 이 결과는 UI 완료나 실제 backend 보증으로 확장할 수 없다.

## 구조 평가

- response boundary는 `ApiResult<unknown> → unwrapApiResult → Zod`로 unknown을 parse 전 cast하지 않는 경계를 유지한다.
- `all/lists/list/details/detail` key와 matching authoritative detail cache, lists-only invalidation은 Policy 도메인 영향 범위로 제한된다.
- factory-local stateful MSW는 POST 후속 GET을 재현하면서 factory 간 state leakage를 막는다.
- handler 3개와 client method 3개가 1:1이며 cross-domain generic factory와 cross-domain invalidation은 없다.

위 평가는 [source review](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/source-review.md)와 [independent confirmation](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/watcher/attempt-2/adversarial-verify.json)에 근거한다.

## 재시도에서 얻은 개선점

attempt 1은 aggregate count가 맞더라도 base fixture 필드를 개별 비교하지 않으면 stale-state를 놓칠 수 있음을 보였다. 또한 “UI import 0” 같은 범위 불명확한 표현은 source truth와 충돌할 수 있었다. [attempt-1 findings](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/watcher/attempt-1/adversarial-verify.json)

attempt 2는 4×7 `28/28` field matrix와 신규 API/query/mutation hook에 한정한 forbidden import 검토로 이를 보완했다. [base equality](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/attempt-2/base-equality-matrix.json) · [import scope](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/attempt-2/import-scope.json)

## 잔여 위험과 권장 백로그

1. endpoint/envelope는 MSW 기반 local provisional contract다. actual backend compatibility, permission, idempotency는 별도 통합 환경에서 검증해야 한다.
2. UI controls, request validation, rendering, routes/navigation, visual QA는 Claude-owned이며 이 Closure가 구현·검증하지 않았다.
3. T03 declared aggregate와 T04 시작 전 recomputed aggregate의 historical baseline drift는 T04가 야기한 변경이 아니지만, 최종 종합 검증에서 계속 분리 추적해야 한다. T04 attempt 2 start/end는 동일하다. [frozen comparison](../../../../.omo/evidence/cp-admin-api-remediation-non-ui/t04/generator/attempt-2/frozen-comparison.json)

## 다음 단계

Hephaestus는 이 문서 set과 evidence link를 검사한 뒤 Todo 4를 닫고 T05를 시작한다. 제품 코드나 Claude-owned 경로를 추가 수정할 근거는 이 Closure에 없다.
