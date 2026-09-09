# 구현 로그

## 변경 내용
1. `cp-discussion-detail-page.tsx`
   - invalid 종료일 입력에 conditional `aria-invalid=true`를 추가했다.
   - `!isClosedAtValid`를 save disabled 조건에 추가했다.
2. `cp-discussion-list-page.css`
   - T03-local validation text token을 `#d91500`으로 조정했다.

## 선택 이유
- 접근성 상태, 요청 차단, 시각적 affordance를 동일한 `isClosedAtValid` source of truth에 연결하기 위해서다.
- shared token 변경 금지 제약을 지키면서 12px 오류 문구의 WCAG AA 대비를 충족하기 위해 로컬 token만 조정했다.

## 검증 결과
- scoped ESLint, TypeScript build, production build: PASS
- `#d91500`/computed white: `5.1755:1`
- invalid detail POST 0, corrected rapid save POST 1
- invalid list GET 0, reset 후 corrected GET 1
- success/failure Dialog native dismiss 확인
- fresh 9/9 PNG와 접근성 snapshot 생성

근거: [static gates](../../../../.omo/evidence/cp-admin-api-remediation/t03/generator/attempt-4/static-gates.md), [behavior report](../../../../.omo/evidence/cp-admin-api-remediation/t03/generator/attempt-4/e2e/behavior-report.json), [capture metadata](../../../../.omo/evidence/cp-admin-api-remediation/t03/generator/attempt-4/capture-metadata.json)
