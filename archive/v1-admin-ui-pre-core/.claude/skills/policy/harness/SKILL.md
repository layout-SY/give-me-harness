---
name: policy-harness
description: synthoria-admin-ui 작업 실행 시 중단·승인·재시도 조건을 판정하는 횡단 규칙. 승인 전 코드 생성 금지, SKILL 미확인 중단, 리뷰 누락 시 완료 불가를 강제해야 할 때 사용.
---

# Harness (Policy)

## 언제 이 스킬을 사용하나요?

- 에이전트가 작업을 시작/재개/종료하기 직전
- 승인·검증 없이 다음 단계로 넘어가려는 상황을 감지했을 때
- 반복 실패·역할 침범이 발생해 escalation 판단이 필요할 때

## Enforcement

- **승인 전 코드 생성 금지**
- 관련 **SKILL 미확인** 시 작업 중단
- `src/components` / `reference/*` 탐색 **전** 구현 시작 중단
- **review(검증) 누락** 시 완료 처리 금지
- **retry / escalation** 규칙 준수 (동일 실패 3회 이상이면 상위 에이전트로 보고)

## 금지

- 에이전트가 자의적으로 승인 범위를 확장
- 중단 조건 충족 시 경고만 남기고 진행
- escalation 규칙 우회 (무한 retry)
