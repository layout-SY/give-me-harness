# 탐색 기록

## 대상
- attempt 3 Visual QA findings
- `src/pages/cp-discussion/ui/cp-discussion-detail-page.tsx`
- `src/pages/cp-discussion/ui/cp-discussion-list-page.css`
- 공용 컴포넌트 재사용 구조와 적용 정책

## 확인한 사실
- detail validation message는 이미 `role="alert"`와 `aria-describedby`로 연결돼 있었지만 invalid input 자체의 `aria-invalid`가 없었다.
- save disabled 조건은 change와 pending만 검사해 invalid draft에서도 버튼이 활성처럼 보였다.
- 기존 오류색 `#f31700`은 흰색 배경에서 `4.2566:1`로 12px AA 기준 `4.5:1`에 미달했다.
- shared 문제는 사용자 제약에 따라 T03 작업에서 분리해야 했다.

## 재사용 판단
- 기존 shared input/button/dialog 구조를 유지하고 새 공용 컴포넌트를 만들지 않았다.
- 로컬 validation contract만 보강해 blast radius를 두 파일로 제한했다.

근거: [behavior report](../../../../.omo/evidence/cp-admin-api-remediation/t03/generator/attempt-4/e2e/behavior-report.json), [deferred risks](../../../../.omo/evidence/cp-admin-api-remediation/t03/generator/attempt-4/deferred-risks.md)
