<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/hosts/claude/workflows/escalation-workflow.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# Escalation Workflow

## 발동 조건

- 동일 반려 사유가 2회 반복된 경우 (`repeat_issue_detected: true`)
- 총 반려 횟수가 3회를 초과한 경우
- 역할 경계 충돌이 감지된 경우
- 범위 모호성이 해소되지 않은 경우
- 현재 티켓 범위를 초과하는 구조적 이슈가 발견된 경우

## 이관 대상

| 이관 대상 | 이관 사유 |
| --- | --- |
| **Planner** | 범위·라우팅 문제, 섹션 재분류 필요 |
| **Evaluator** | 아키텍처 리스크, 기술 부채, 구조적 설계 이슈 |
| **User** | 요구사항 모호성, 트레이드오프 결정 필요 |

## 처리 흐름

1. 발동 조건 확인 후 `escalation_needed: true` 표시
2. 이관 대상과 이관 사유를 `review-log.md`에 기록
3. 해당 에이전트(Planner / Evaluator / User)에게 컨텍스트 전달
4. 이관 후 현재 에이전트 실행 종료

## 단계별 참조 SKILL

| 단계 | 참조 SKILL |
| --- | --- |
| Watcher 반려 판정 | [policy/review-checklist/SKILL.md](../skills/policy/review-checklist/SKILL.md) |
| Planner 재분류 | [policy/orchestration/SKILL.md](../skills/policy/orchestration/SKILL.md) |
| Evaluator 구조 분석 | [policy/review-checklist/SKILL.md](../skills/policy/review-checklist/SKILL.md) |
