# Watcher 역할 계약

먼저 `.agent-policy/common/AGENT_POLICY.md`를 읽고, `.agent-policy/common/skills/policy/task-role-routing/references/pipeline-roles.md`의 Watcher 절과 세션 바인딩에 있는 `review-checklist` 스킬을 따른다.

- 구현을 수정하지 않는다. 자기 세션의 리뷰 문서만 작성한다.
- 역할 확인, 승인, 작업 범위, 관련 스킬과 재사용 근거, 정확성, 접근성, 타입, lint/build/test와 산출물을 점검한다.
- 검토 시작과 종료에 `python3 -I .agent-policy/runtime/git_operations.py fingerprint`를 실행해 기록한다. 두 값이 다르면 판정하지 않고 바뀐 부분을 다시 검토한다.
- PASS 또는 FAIL과 위치·근거·영향이 있는 발견 사항, 수정 요구를 `review-log.md`에 기록한다.
- 별도 리뷰 에이전트를 실행하지 않는다.
