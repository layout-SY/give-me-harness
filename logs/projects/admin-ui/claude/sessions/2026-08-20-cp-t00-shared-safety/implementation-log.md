# 구현 로그

## 작업 요약
- Tranche 0은 stale favicon 요청, 미등록 CP 요청의 silent passthrough, Axios no-response request 직렬화 위험을 세 개의 허용 제품 파일에서 처리했다.
- attempt 1은 Watcher가 CP 요청의 브라우저-visible 실패가 없다고 반려했고, attempt 2에서 `src/app/index.tsx`의 CP-only 분기만 보완한 뒤 독립 Watcher `confirmed`를 받았다.

## 재사용 자산
- 기존 MSW browser worker와 등록된 Dashboard/Proposal handlers를 유지했다.
- 기존 Axios interceptor를 유지하되 no-response branch의 출력만 고정 문자열로 축소했다.
- 신규 공용 컴포넌트·훅·handler factory는 추가하지 않았다.

## 신규 파일 / 수정 파일
- 제품 수정 파일(Generator 결과):
  - `index.html`: `/favicon.svg` 선언 대신 inert data favicon을 사용.
  - `src/app/index.tsx`: DEV MSW 시작 시 `/v1/cp/` unknown 요청만 보고하고 attempt 2에서 동기 throw하여 500 경계를 형성; non-CP는 bypass.
  - `src/shared/api/axios-instance.ts`: `JSON.stringify(err.request)`를 제거하고 `No response received`만 기록.
- Todo 3 신규 문서 파일: 이 세션 필수 문서 6개와 동일 slug portfolio 1개.

## 단계별 구현·검증 이력

### 1. Baseline
- dirty/untracked 52개 경로의 SHA-256과 failing-first를 기록했다.
- baseline Dashboard에서 `/favicon.svg` 요청이 있었고 unknown `/v1/cp/__unhandled`는 `200 text/html` Vite fallback으로 관찰됐다.
- 근거: [baseline.json](../../../../.omo/evidence/cp-admin-api-remediation/t00/generator/baseline.json), [baseline network](../../../../.omo/evidence/cp-admin-api-remediation/t00/generator/baseline-network.txt), [baseline unknown CP](../../../../.omo/evidence/cp-admin-api-remediation/t00/generator/baseline-unhandled-cp.json).

### 2. Generator attempt 1
- favicon: 명시적 SVG link만 제거했을 때 Chromium이 `/favicon.ico`를 요청해 404가 발생했다. inert data favicon으로 교정한 뒤 fresh Dashboard에서 favicon 요청 0과 console error 0을 확인했다.
- MSW: `/v1/cp/`에만 `print.error()`를 호출하고 그 외 요청은 bypass하도록 했다.
- Axios: no-response branch에서 request object/header/body 직렬화를 제거했다.
- 명령: scoped ESLint exit 0, `yarn tsc -b --pretty false` exit 0, `yarn build` exit 0.
- 근거: [제품 변경·hash](../../../../.omo/evidence/cp-admin-api-remediation/t00/generator/product-changes.json), [favicon 중간 실패와 교정](../../../../.omo/evidence/cp-admin-api-remediation/t00/generator/qa-summary.json), [명령 결과](../../../../.omo/evidence/cp-admin-api-remediation/t00/generator/command-results.json), [attempt 1 cleanup](../../../../.omo/evidence/cp-admin-api-remediation/t00/generator/cleanup.json).

### 3. Watcher attempt 1 반려
- 독립 Watcher는 favicon, Axios redaction, Dashboard/Proposal, non-CP bypass, baseline 보존을 확인했다.
- 그러나 unknown CP 요청은 MSW error log가 있어도 실제 fetch가 `200 text/html`로 resolve되어 `needs-fix` 판정을 받았다.
- 필수 수정은 unknown `/v1/cp/` 요청을 브라우저-visible 경계에서 rejected fetch 또는 non-2xx로 만드는 것이었다.
- 근거: [attempt 1 Watcher needs-fix](../../../../.omo/evidence/cp-admin-api-remediation/t00/watcher/adversarial-verify.json).

### 4. Generator attempt 2
- 원인: 설치된 MSW compatibility adapter의 legacy callback `print.error()`는 출력만 하고 resolve되어 passthrough를 허용했다.
- 수정: CP-only `print.error()` 직후 `throw new Error("Unhandled CP request")`를 추가했다. attempt 2에서 변경한 제품 파일은 `src/app/index.tsx` 하나다.
- hash: `src/app/index.tsx`가 `f912907503a7b9b72ddbd87a0c82ee54a2b56e89896386254d45909b193ed566`에서 `d042aa05e176566df07605d182fb234c32b998ffbf2102a338f9ffa89e502104`로 변경됐다. attempt 1의 `index.html`과 Axios hash는 유지됐다.
- 근거: [원인 조사](../../../../.omo/evidence/cp-admin-api-remediation/t00/generator/attempt-2/investigation.json), [source-change.json](../../../../.omo/evidence/cp-admin-api-remediation/t00/generator/attempt-2/source-change.json).

### 5. 최종 검증
- unknown CP: `500 application/json`, `ok=false`, body에 `Unhandled CP request`가 포함됐다.
- non-CP unknown: `200 text/html`, console error 0으로 bypass를 유지했다.
- Dashboard/Proposal: 등록된 GET이 각각 200이고 fresh normal session console error 0이었다. Dashboard favicon request는 0이었다.
- LSP: TypeScript LSP 미설치 및 이전 설치 거절로 unavailable.
- 대체 게이트: `yarn eslint src/app/index.tsx src/shared/api/axios-instance.ts`, `yarn tsc -b --pretty false`, `yarn build` 모두 exit 0. attempt 2의 좁은 재검증도 ESLint/tsc/build 모두 exit 0.
- 근거: [attempt 2 QA](../../../../.omo/evidence/cp-admin-api-remediation/t00/generator/attempt-2/qa-summary.json), [attempt 2 commands](../../../../.omo/evidence/cp-admin-api-remediation/t00/generator/attempt-2/command-results.json), [최종 Watcher](../../../../.omo/evidence/cp-admin-api-remediation/t00/watcher/attempt-2/adversarial-verify.json).

### 6. Cleanup
- Generator attempt 1의 자체 4174 서버 3개를 중지했고 browser를 닫았다. 사전 존재한 shared server 4173은 보존했다.
- Generator attempt 2의 4192 listener와 browser를 정리했고 임시 instrumentation은 남지 않았다.
- 최종 Watcher의 4193 listener와 모든 browser tab도 정리됐다.
- git state mutation은 수행하지 않았다.
- 근거: [attempt 1 cleanup](../../../../.omo/evidence/cp-admin-api-remediation/t00/generator/cleanup.json), [attempt 2 cleanup](../../../../.omo/evidence/cp-admin-api-remediation/t00/generator/attempt-2/cleanup.json), [Watcher attempt 2 cleanup](../../../../.omo/evidence/cp-admin-api-remediation/t00/watcher/attempt-2/adversarial-verify.json).

## 핵심 로직
- data favicon은 Chromium의 fallback favicon 요청 자체를 없애 네트워크/console 잡음을 제거한다.
- MSW CP-only throw는 unknown CP 요청을 성공 HTML로 오인하지 않도록 response boundary를 non-2xx로 만든다.
- Axios redaction은 no-response 진단에서 request/header/body 상태를 직렬화하지 않는다.

## 리스크
- 이는 local MSW 안전장치 검증이며 실제 backend 계약·auth/permission 호환성을 보장하지 않는다.
- unknown CP는 rejected fetch가 아니라 MSW가 exception을 500 JSON으로 변환하는 방식이다. acceptance는 non-2xx이므로 충족하지만 console에는 의도된 MSW error와 500 resource error가 남는다.
- build의 기존 `vite-tsconfig-paths` 안내와 500 kB 초과 chunk 경고는 잔존한다.

## 핸드오프 메모
- Watcher attempt 1 반려 사항은 attempt 2에서 보완됐고, 독립 Watcher 최종 판정은 `confirmed`다.
- Tranche 1 Comment는 이 Closure 완료 후에만 시작할 수 있다.
