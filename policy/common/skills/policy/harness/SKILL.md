---
name: policy-harness
description: 승인, 스킬 탐색, 재사용 가능 자산 조사, 역할 분리 및 리뷰 게이트를 강제한다.
---

# 실행 체계

- 호스트 이름으로 역할을 추정하지 않는다. `task-role-routing`에 따라 요청과 handoff에서 역할을 제안하고 사용자 확인을 받는다.
- 명시적인 승인 전에는 애플리케이션 코드를 수정하지 않는다. 공통 guard는 host별 사용자 prompt event에서 이 승인을 세션 상태로 기록한다.
- 관련 `SKILL.md`, 대상 코드와 인접한 재사용 가능 자산을 실제 읽기·검색 도구로 조사한다. UI 역할이 포함될 때만 `src/shared/ui/`와 `DESIGN.md`를 우선 조사한다. 공통 PostTool gate는 성공한 도구 근거를 기록하며 prompt의 자기 선언만으로 통과시키지 않는다.
- Git 변경은 사용자에게 실제 작업 단위·위치·영향을 보고하여 승인받는다. 조회와 일반 lint·test·build는 별도 승인 없이 수행한다. Git에 branch 계약·계보·소유권·문서 완료 조건을 적용하지 않는다.
- Planner, Publisher, Implementer/Generator, Refactorer, Watcher와 Evaluator는 `task-role-routing/references/pipeline-roles.md`를 따른다.
- 역할·파일 범위가 바뀌면 구현을 멈추고 변경된 계약을 다시 확인받는다.
- 완료하려면 필수 문서와 검증 근거가 있어야 한다.
- 단계 전환마다 `can_proceed`, 누락 조건, 역할 위반, 승인 상태, retry와 escalation 근거를 공통 agent output schema에 맞춰 기록한다. Harness는 설계·구현 또는 Watcher의 PASS/FAIL 판정을 대신하지 않는다.
