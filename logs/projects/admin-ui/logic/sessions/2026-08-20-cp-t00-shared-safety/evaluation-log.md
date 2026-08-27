# 평가 로그

## 컨텍스트
- 이 문서는 Tranche 0 Closure가 확인한 장기 관점의 잔여 항목을 기록한다.
- **Evaluator는 실행되지 않았고 PASS 판정도 없다.** 상위 계획은 장기 평가를 Todo 39/T12에 두고 있다.
- 이번 writing category는 billing limitation으로 실행되지 못해 fallback Closure가 문서를 작성했다. 장기 Evaluator 평가는 결제 가능 여부와 관계없이 T12에서 다시 시도하고, 실패 시 계획에 정의된 fallback과 사유를 기록해야 한다.

## 구조적 리스크
1. unknown CP failure는 MSW legacy callback에서 exception을 던져 500 JSON으로 변환하는 local development 정책이다.
2. 실제 backend 계약과 auth/permission 모델은 T00 및 전체 계획의 명시적 제외 범위다.
3. build에는 기존 `vite-tsconfig-paths` native-resolution 안내와 500 kB 초과 minified chunk 경고가 남아 있다.

## 왜 중요한가
- local MSW의 `confirmed`를 production backend 호환성 또는 권한 안전성으로 확대 해석하면 검증 범위를 넘는 주장이다.
- throw 기반 policy는 현재 설치된 MSW adapter에서 확인됐지만 향후 MSW API/adapter 변경 시 동작을 재확인해야 한다.
- build warning은 T00 회귀 실패가 아니지만 최종 tranche에서 전역 품질 리스크로 집계할 가치가 있다.

## 개선 옵션
1. T12 종합 회귀에서 23 routes/41 operations/25 controls와 함께 unknown CP/non-CP 경계를 다시 검증한다.
2. 실제 backend 계약·auth 검증은 별도 승인된 backend integration/security 작업으로 분리한다.
3. dependency 변경이 허용되는 별도 작업에서 MSW의 최신 selective unhandled API와 Vite path resolution/chunk 전략을 검토한다.

## 권장 백로그
1. Todo 39/T12: 장기 Evaluator 시도 및 billing failure 시 fallback 사유 기록.
2. T12/F4: backend/auth 미검증과 dependency/package guardrail 준수 여부를 최종 scope fidelity에 명시.
3. 별도 성능 tranche: 500 kB 초과 chunk 원인과 code splitting 필요성을 측정 후 판단.

## 다음 단계 제안
- 현재 T00은 독립 Watcher `confirmed`로 닫되 Evaluator PASS를 주장하지 않는다.
- 이 Closure 이후 상위 오케스트레이터가 문서를 독립 읽기 검증한 뒤 Todo 3 완료 여부를 결정한다.
