# 포트폴리오 경험 기록

## 작업 개요
- 구현/수정 내용: data favicon, CP-only MSW unknown-request failure, Axios no-response redaction을 적용하고 독립 Watcher 반려 후 재검증했다.
- 구현 이유: 개발 네트워크 잡음, 미등록 CP API의 성공 HTML 오인, request 상태 직렬화 가능성을 각각 좁은 shared safety 경계에서 처리하기 위해서다.
- 작업 유형: shared safety 수정 + 독립 검증 + 문서 Closure.

## 문제 상황
- 문제 출처: [상위 계획 Todo 1~3](../../../../.omo/plans/cp-admin-api-remediation.md#todos), [Generator baseline](../../../../.omo/evidence/cp-admin-api-remediation/t00/generator/baseline.json), [Watcher attempt 1](../../../../.omo/evidence/cp-admin-api-remediation/t00/watcher/adversarial-verify.json).
- 대상 도메인·서비스: 시민참여 관리자 개발 환경의 favicon, MSW request handling, Axios error diagnostics.
- 기존 문제와 영향:
  - fresh Dashboard에서 `/favicon.svg`가 요청됐다.
  - unknown `/v1/cp/__unhandled`는 handler가 없어도 Vite SPA fallback `200 text/html`로 resolve되어 성공 응답처럼 보였다.
  - Axios no-response branch가 `err.request` 전체를 직렬화해 request/header/body 상태가 로그에 포함될 여지가 있었다.

## 요구사항 및 의사결정
- 사용자 요구·제안: stale favicon 요청 제거, CP-only unhandled safety, Axios redaction, dirty baseline 보존, fresh command/browser/hash/cleanup 검증, 독립 Watcher `confirmed` 후 문서화.
- 에이전트 제안: 제품 파일 세 개만 좁게 수정하고, unknown CP와 non-CP를 분리하며, Generator와 Watcher가 서로 다른 server/browser에서 검증한다.

| 접근법 | 장점 | 단점 | 선택 여부와 이유 |
|---|---|---|---|
| favicon link만 삭제 | 변경이 가장 작음 | Chromium이 `/favicon.ico`를 fallback 요청해 404 발생 | 미채택. 실제 중간 QA에서 실패가 확인됨 |
| inert data favicon | 별도 asset 요청 없이 browser fallback도 억제 | 빈 favicon을 명시해야 함 | 채택. fresh Dashboard에서 favicon request 0 확인 |
| CP branch에서 `print.error()`만 호출 | CP-only 진단과 non-CP bypass를 쉽게 분리 | legacy MSW callback이 resolve되어 Vite `200 text/html` passthrough | attempt 1 채택 후 Watcher 반려 |
| CP branch에서 보고 후 동기 throw | CP-only 진단을 유지하면서 browser-visible non-2xx 형성 | 격리 negative session에 의도된 500/MSW console error 발생 | attempt 2 채택. 독립 Watcher confirmed |
| Axios request object 전체 직렬화 | 디버깅 정보가 많음 | request/header/body 상태 노출 가능 | 미채택. 고정 no-response signal만 기록 |

## 사용 기술과 구체적 목적

| 기술/패턴/아키텍처 | 해결하려는 문제 | 적용 위치와 목적 | 미채택 대안/이유 |
|---|---|---|---|
| data URI favicon | stale SVG 및 browser fallback favicon 요청 | `index.html`에서 네트워크 요청 없이 favicon 선언 | link 삭제만으로는 `/favicon.ico` 404 재현 |
| MSW custom `onUnhandledRequest` + throw | unknown CP 요청의 silent passthrough | `src/app/index.tsx`에서 `/v1/cp/`만 500 경계, non-CP bypass | `print.error()` 단독은 200 HTML을 허용 |
| Axios diagnostic redaction | request/header/body 직렬화 가능성 | `src/shared/api/axios-instance.ts` no-response branch를 고정 문자열로 축소 | `JSON.stringify(err.request)`는 범위가 과다 |
| SHA-256 dirty baseline | 기존 사용자 변경 침범 판별 | 52개 dirty/untracked path를 tranche 시작과 최종에 대조 | HEAD 기준 diff만으로는 시작 시 dirty 상태를 분리하기 어려움 |
| fresh Playwright sessions | stale server/browser 상태 오판 방지 | Dashboard, Proposal, CP-negative, non-CP를 분리 검증 | Generator session 재사용은 독립성을 약화 |

## 적용 내용
- 실제 구현·수정·리팩터링:
  - before: `/favicon.svg` 요청 존재. after: fresh Dashboard favicon request 0.
  - before: unknown CP가 `200 text/html`, `ok=true`. attempt 1: MSW error는 보이나 여전히 200 HTML. attempt 2 after: `500 application/json`, `ok=false`.
  - before: no-response에서 `err.request` 직렬화. after: `No response received` 고정 문자열만 기록.
- AI 하네스 변경(해당 시): 제품 하네스 자체를 변경한 것은 아니며, Generator → independent Watcher → Closure 역할과 반려/재시도 게이트를 적용했다. writing category billing limitation으로 Todo 3은 fallback Closure가 수행했다.
- 구조 변화 도식(해당 시): `unknown CP → MSW report → throw → 500 JSON`; `unknown non-CP → bypass → Vite fallback`.

## 결과 및 성과
- before/after: 위 세 경계의 실제 관찰값만 기록했다. 사용자 체감 속도, 장애 감소율, 보안 사고 감소 등은 측정하지 않아 주장하지 않는다.
- 검증 결과:
  - scoped ESLint, `yarn tsc -b --pretty false`, `yarn build` exit 0.
  - TypeScript LSP는 미설치 및 이전 설치 거절로 unavailable.
  - Dashboard/Proposal fresh normal session console error 0, registered GET 200.
  - 52개 baseline hash 재검사에서 허용된 Axios mismatch 외 비허용 차이 없음.
  - Generator/Watcher browser와 자체 ports 정리, 사전 존재 4173 server 및 git state 보존.
- 사용자 후속 피드백: 별도 제품 피드백은 기록되지 않았다. Watcher attempt 1이 transport failure 부재를 `needs-fix`로 반려했고, attempt 2 독립 Watcher가 `confirmed`했다.
- 잔여 리스크: 실제 backend/auth 미검증, unknown CP가 rejected fetch 대신 500 Response를 사용, 기존 build advisory/chunk warning 잔존, Evaluator는 T12로 유예되어 PASS 없음.
- 증거: [attempt 2 QA](../../../../.omo/evidence/cp-admin-api-remediation/t00/generator/attempt-2/qa-summary.json), [attempt 2 commands](../../../../.omo/evidence/cp-admin-api-remediation/t00/generator/attempt-2/command-results.json), [최종 Watcher](../../../../.omo/evidence/cp-admin-api-remediation/t00/watcher/attempt-2/adversarial-verify.json), [cleanup](../../../../.omo/evidence/cp-admin-api-remediation/t00/generator/attempt-2/cleanup.json).

## 회고
- 잘된 판단: console message 존재를 성공 조건으로 삼지 않고 response status/content type까지 독립 검증한 Watcher 게이트가 attempt 1의 misleading success를 발견했다.
- 다시 한다면 바꿀 점: 첫 구현 전에 설치된 MSW legacy callback의 resolve/reject semantics를 확인하고 failing-first acceptance를 “non-2xx 또는 rejected fetch”로 명시해 재시도를 줄인다.
- 다음 작업에 적용할 인사이트: mock safety는 로그, 네트워크 응답, 정상 handler 회귀, non-domain bypass를 각각 분리해 검증하고 negative session의 의도된 console error를 fresh normal session과 섞지 않는다.
