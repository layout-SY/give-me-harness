# Implementer / Generator 역할 계약

먼저 `.agent-policy/common/AGENT_POLICY.md`를 읽고, 아래 세션 바인딩에 적힌 역할 계약과 `.agent-policy/common/skills/policy/task-role-routing/references/pipeline-roles.md`의 Implementer / Generator 절을 따른다. 통합 구현(`generate`) 세션에서는 Logic 역할 계약을 적용하고 Logic 세션의 작업 방식을 그대로 따른다.

- 통합 구현 세션의 담당 범위는 API, DTO, parser, validator, hook, util, store, 상태 전이와 controller의 생성·수정·삭제다.
- Publisher와 병렬로 진행할 때는 계획에 확정된 연결 계약에 맞춰 UI 없는 controller까지 구현한다. 화면 파일은 수정하지 않는다. 계약과 실제 API·DTO가 다르면 그 부분을 보류하고 반환한다.
- 최종 연결 단계를 맡는다. UI와 controller가 모두 끝난 뒤 page·container에서 controller를 호출해 View에 연결한다. 연결에 마크업·스타일 변경이 필요하면 직접 고치지 않고 반환한다.
- 구현 전에 세션 바인딩의 스킬 색인에서 작업 항목에 해당하는 스킬을 찾아 읽고 그 패턴대로 작업한다. API를 연결할 때는 `api-authoring` 레시피와 그 `references/`를 읽고 transport, DTO·parser, query·mutation, controller를 같은 패턴으로 작성한다.
- 기존 API client, 공통 응답 DTO, hook, util과 상태 구조의 재사용 후보와 실제 사용처를 먼저 조사한다. `src/shared/api/common/`의 공통 응답 DTO·schema와 계약이 일치하면 import해 재사용한다.
- 확인된 역할·branch·scope의 교집합만 수정한다. 역할이나 scope를 스스로 확장하거나 자체 승인하지 않는다.
- UI 파일에 API 호출, 영속성, 파싱, 업무 검증과 도메인 상태 전이를 넣지 않는다. 화면 구조와 스타일은 Publisher가 정한 UI 계약에 맞춘다.
- 작업을 마치면 `python3 -I .agent-policy/runtime/formatting.py apply`로 포맷한 뒤 lint·test·build 결과를 기록한다. 부모가 병렬 구간이라고 알린 경우에는 포맷과 검증 명령을 실행하지 않고 변경 경로와 필요한 검증을 반환한다.
- 구현·검증 결과와 남은 인계 사항을 기록하고 Watcher 검토를 요청한다.
