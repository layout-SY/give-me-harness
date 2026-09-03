# 계획

## 요청 요약
- `cp-admin-api-remediation` 계획의 Todo 1~3 중 Tranche 0 Shared Safety 완료 이력을 결론 중심 문서로 닫는다.
- Generator attempt 1, Watcher 반려, Generator attempt 2, 독립 Watcher 최종 `confirmed`를 증거와 연결한다.

## 작업 유형
- hybrid (제품 안전장치 수정 이력의 문서 Closure)

## 범위
- 제품 변경 범위: `index.html`, `src/app/index.tsx`, `src/shared/api/axios-instance.ts`의 Todo 1 결과를 기록한다.
- 문서 범위: 이 세션의 필수 문서 6개와 동일 slug 포트폴리오 1개를 작성한다.
- 검증 범위: scoped ESLint, TypeScript, build, Playwright, SHA-256 baseline, cleanup 및 독립 Watcher 판정을 인용한다.

## 제외 범위
- 제품 코드, 계획, Boulder, todo/ledger, 다른 세션 로그, git index/history는 변경하지 않는다.
- 실제 backend 호환성과 auth/permission 동작을 보장하거나 평가하지 않는다.
- Tranche 1 Comment 작업은 시작하지 않는다.

## 섹션
1. Planner/Closure: 계획·템플릿·정책·T00 전체 증거를 읽고 사실과 잔여 리스크를 확정한다.
2. Closure: 필수 세션 문서 6개와 동일 slug 포트폴리오를 작성한다.
3. Closure: 경로·제목·링크·범위 검사를 수행하고 closure receipt를 남긴다.

## 필요 에이전트
- Generator: Todo 1 제품 변경과 재시도 증거 생산(완료).
- Watcher: Todo 2 독립 검증, attempt 1 `needs-fix`, attempt 2 `confirmed` 판정(완료).
- Closure fallback: 결제 제한으로 writing category를 실행하지 못해 현재 세션이 Todo 3 문서화를 수행한다.
- Evaluator: Tranche 0에서는 실행하지 않고 Todo 39/T12 장기 평가로 유예한다.

## 필요 스킬
- `policy-documentation`: 결론 중심 필수 산출물과 중복 없는 근거 기록.
- `policy-portfolio`: 문제·선택·적용·검증·피드백·회고와 측정된 결과만 기록.
- `policy-review-checklist`: Watcher 게이트와 범위·검증·재사용 판단 기록.
- `policy-harness`: 승인 범위, 역할 경계, 반려 후 재검증, 완료 게이트 준수.

## 리스크 / 가정
- 실제 backend·auth 계약은 계획상 제외되어 local MSW 검증 결과를 backend 보장으로 확대하지 않는다.
- TypeScript LSP가 설치되지 않았고 설치가 이전에 거절되어 LSP 진단은 unavailable이다. scoped ESLint와 `tsc -b`를 대체 게이트로 기록한다.
- build는 통과했지만 기존 `vite-tsconfig-paths` 안내와 500 kB 초과 chunk 경고가 남는다.
- attempt 1의 MSW `print.error()`는 탐지만 했고 HTTP 200 HTML passthrough를 막지 못했다. 최종 결론은 attempt 2와 최종 Watcher 증거만으로 확정한다.

## 승인 요청
- 상위 계획은 승인되어 Todo 1·Todo 2가 수행되었고, 사용자 요청으로 Todo 3 Closure 범위가 명시적으로 위임되었다.

## 근거
- [상위 계획 Todo 1~3](../../../../.omo/plans/cp-admin-api-remediation.md#todos)
- [Generator baseline](../../../../.omo/evidence/cp-admin-api-remediation/t00/generator/baseline.json)
- [Watcher attempt 1 반려](../../../../.omo/evidence/cp-admin-api-remediation/t00/watcher/adversarial-verify.json)
- [Watcher attempt 2 confirmed](../../../../.omo/evidence/cp-admin-api-remediation/t00/watcher/attempt-2/adversarial-verify.json)
