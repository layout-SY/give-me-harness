# 오케스트레이션 역할

| 단계 | 역할 | 산출물 |
| --- | --- | --- |
| 탐색/계획 | Planner | exploration.md, plan.md |
| UI 계약 | Publisher | 계획/구현 로그의 계약 기록 |
| 기능 구현 | Generator | implementation-log.md |
| 구조 변경 | Refactorer | implementation-log.md |
| 현재 검증 | Watcher | review-log.md PASS/FAIL |
| 장기 학습 | Evaluator | evaluation-log.md |

Watcher와 Evaluator는 분리한다. 불명확한 요구 사항은 Planner에게, 계약 충돌은 Publisher에게, 구현 실패는 구현 담당 역할에게 전달한다. 반복 실패는 재계획을 위해 Planner에게 전달한다.
