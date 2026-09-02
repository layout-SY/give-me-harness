# 계획

## 요청 요약
T03 Discussion의 Generator attempt 3 Visual QA blocker 세 건을 T03-owned 두 파일 안에서 최소 수정하고 fresh behavior·9-state visual evidence로 재검증한다.

## 범위
- detail invalid 종료일의 `aria-invalid` 노출
- invalid 종료일에서 `처리 저장` 비활성화
- T03-local 오류 문구 대비 개선
- fresh port에서 기능 검증, 9개 PNG, 접근성 snapshot, 독립 시각 QA

## 제외 범위
- shared navigation, shared muted/KPI tokens, shared `Dialog`/`Button`, non-T03 source
- 실제 backend/auth 계약 확정

## 검증
- scoped ESLint, `yarn tsc -b --pretty false`, `yarn build`
- invalid request 0, corrected rapid save POST 1, native Dialog recovery
- 1440/1024 9-state capture와 PNG signature/dimension/hash
- 독립 read-only Visual QA Pass A/B

근거: [attempt 4 evidence](../../../../.omo/evidence/cp-admin-api-remediation/t03/generator/attempt-4/)
