# 탐색 기록

## 대상 경로
- `AGENTS.md`, `.codex/templates/*.template.md`
- `.agents/skills/policy/{documentation,portfolio,harness,review-checklist}/SKILL.md`
- `.omo/plans/cp-admin-api-remediation.md`의 Todo 1~3
- `.omo/evidence/cp-admin-api-remediation/t00/generator/` 전체
- `.omo/evidence/cp-admin-api-remediation/t00/watcher/` 전체

## 발견한 기존 재사용 자산
- 발견 항목: 기존 제품 공용 자산을 새로 만들지 않고, 이미 사용 중인 MSW worker 시작 정책과 Axios interceptor의 좁은 지점을 수정했다.
- 재사용 제안: 다음 tranche도 현재 `src/mocks/handlers.ts`, Dashboard/Proposal 등록 handler, 기존 `src/shared/ui`·`src/widgets`를 유지한다.
- 근거: [상위 계획 guardrail](../../../../.omo/plans/cp-admin-api-remediation.md#must-not-have-guardrails-anti-slop-scope-boundaries), [최종 Watcher normalHandlers](../../../../.omo/evidence/cp-admin-api-remediation/t00/watcher/attempt-2/adversarial-verify.json).

## 재사용이 어려운 자산
- 자산: attempt 1의 custom `onUnhandledRequest` 내부 `print.error()` 단독 처리.
- 부적합 사유: 설치된 MSW browser compatibility adapter에서 `print.error()`는 출력만 하고 callback을 성공적으로 resolve하여 passthrough로 이어졌다. 그 결과 `/v1/cp/__unhandled`가 Vite SPA fallback의 `200 text/html`로 관찰되었다.
- 근거: [attempt 2 원인 조사](../../../../.omo/evidence/cp-admin-api-remediation/t00/generator/attempt-2/investigation.json), [attempt 1 Watcher 재현](../../../../.omo/evidence/cp-admin-api-remediation/t00/watcher/adversarial-verify.json).

## 신규 자산 필요성
- 필요 항목: 신규 공용 컴포넌트·훅·추상화 없음.
- 필요 이유: T00은 favicon 요청 제거, CP-only unhandled request 경계, Axios no-response 로깅의 세 좁은 shared safety 변경이며 재사용 API를 추가할 범위가 아니다.
- `.codex/memory/reusable-assets.md` 갱신: N/A. 신규 재사용 자산이 없다.

## 확인된 기준선
- tranche 시작 시 dirty/untracked 52개 경로와 SHA-256을 기록했다.
- Todo 1 허용 제품 경로는 `index.html`, `src/app/index.tsx`, `src/shared/api/axios-instance.ts` 세 개다.
- 52개 baseline 경로 중 최종 불일치는 허용된 `src/shared/api/axios-instance.ts` 하나이며, baseline-clean이었던 나머지 두 Todo 1 경로도 허용 범위로 확인됐다.
- 근거: [baseline](../../../../.omo/evidence/cp-admin-api-remediation/t00/generator/baseline.json), [attempt 2 Watcher scopeFidelity](../../../../.omo/evidence/cp-admin-api-remediation/t00/watcher/attempt-2/adversarial-verify.json).

## 결론
- 기존 구조를 보존한 최소 변경이 적합하다.
- 단, “오류 로그가 보인다”와 “브라우저 응답 경계에서 실패한다”를 구분해야 한다. 최종 합격 기준은 unknown CP 요청이 `500 application/json`, `ok=false`로 관찰되는 것이다.
