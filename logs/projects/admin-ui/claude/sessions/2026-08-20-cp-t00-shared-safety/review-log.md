# 리뷰 로그

## 리뷰 대상
- Todo 1 Shared Safety의 허용 제품 변경 3개와 Generator/Watcher 검증 증거.
- 기준: 상위 계획 Todo 2 acceptance와 `policy-review-checklist`.

## 결과
- 최종 결과: **confirmed**.
- attempt 1 결과: **needs-fix**.
- attempt 2 결과: **confirmed**.
- 근거: [Watcher attempt 1](../../../../.omo/evidence/cp-admin-api-remediation/t00/watcher/adversarial-verify.json), [Watcher attempt 2](../../../../.omo/evidence/cp-admin-api-remediation/t00/watcher/attempt-2/adversarial-verify.json).

## Attempt 1 — needs-fix
- 통과: inert data favicon, Axios no-response redaction, normal Dashboard/Proposal, non-CP bypass, scoped ESLint/tsc/build, baseline 보존, cleanup.
- 반려: unknown `/v1/cp/__unhandled`가 MSW error를 출력했지만 fetch는 Vite fallback `200 text/html`로 resolve됐다.
- 판단 이유: “loud detection”만으로는 상위 계획의 expected MSW error를 브라우저-visible 실패로 보장하지 못하며 성공 응답으로 오인될 수 있다.
- 필수 수정: unknown CP 요청이 rejected fetch 또는 non-2xx가 되도록 request boundary를 실패시킨 후 fresh 독립 검증한다.

## Attempt 2 — confirmed
- source: CP-only 분기에서 `print.error()` 뒤 동기 throw를 추가했고 non-CP 분기는 그대로 bypass한다.
- browser: unknown CP는 `500 application/json`, `ok=false`; non-CP unknown은 `200 text/html`, console error 0.
- 정상 회귀: Dashboard/Proposal 등록 GET은 200, fresh normal session console error 0, favicon request 0.
- 범위: 52개 baseline hash를 재검사해 허용된 Axios baseline mismatch 외 비허용 변경이 없음을 확인했다.
- cleanup: Watcher 자체 4193 listener와 browser sessions를 정리했다.

## 체크리스트 검토
- SKILL 준수: 결론 중심 문서, 승인 범위, 독립 Watcher 게이트, 측정된 주장만 사용했다.
- 재사용 확인: 기존 MSW/Axios/handler 구조를 유지했고 신규 공용 자산은 없다.
- 검증 확인: scoped ESLint, `tsc -b`, build, fresh Playwright, baseline hash, cleanup을 확인했다. LSP는 unavailable임을 숨기지 않았다.
- Payload 완결성: N/A. T00은 API payload 또는 DTO를 추가하지 않았다.
- 성능 우려: 신규 반복 fetch·render·N+1은 추가하지 않았다. 기존 500 kB 초과 bundle warning은 잔존한다.
- 중복 코드 우려: 없음. generic factory 또는 병렬 shared abstraction을 추가하지 않았다.
- FSD/의존 방향: 기존 파일 위치에서 최소 수정했으며 신규 layer나 cross-layer 의존을 만들지 않았다.
- validation/hook/추상화: 신규 form validation, hook, 추상화가 없어 해당 항목은 N/A다.

## 위반 사항
1. attempt 1에서 CP-only `print.error()`를 transport failure로 오인했다.
2. attempt 1 결과는 최종 합격으로 사용할 수 없다.
3. 최종 attempt 2에서는 미해결 위반 사항이 확인되지 않았다.

## 필수 수정 사항
1. 완료: CP-only callback을 throw하여 unknown CP를 non-2xx로 전환.
2. 완료: Generator fresh browser/port에서 Dashboard, Proposal, CP-negative, non-CP를 재검증.
3. 완료: 독립 Watcher가 별도 4193 server/browser로 다시 검증하고 `confirmed` 판정.

## 반복 이슈
- false. 1회 반려 후 attempt 2에서 해결됐다.

## 에스컬레이션
- none. 동일 실패 3회 조건에 도달하지 않았다.

## 잔여 리스크
- 실제 backend/auth는 계획상 제외되어 검증되지 않았다.
- TypeScript LSP는 unavailable이며 compiler/linter 결과로 대체했다.
- `vite-tsconfig-paths` 안내와 500 kB 초과 chunk warning은 기존 경고로 남는다.
