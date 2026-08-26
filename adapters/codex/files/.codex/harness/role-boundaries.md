# 역할 경계

- Planner: 근거와 계획을 담당하며 구현하지 않는다.
- Publisher: UI 계약을 담당하며 도메인 효과를 다루지 않는다.
- Generator: 승인된 기능을 구현하며 스스로 판정하지 않는다.
- Refactorer: 동작을 보존하는 구조 변경을 담당하며 기능을 확장하지 않는다.
- Watcher: 현재 작업을 PASS 또는 FAIL로 판정하며 검토 중인 구현을 수정하지 않는다.
- Evaluator: 장기적인 권고 사항을 담당하며 Watcher를 대신하지 않는다.
