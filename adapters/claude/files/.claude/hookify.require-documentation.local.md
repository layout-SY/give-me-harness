---
name: require-documentation
enabled: true
event: stop
pattern: .*
action: warn
---

⚠️ **문서화 완료 여부를 확인하세요**

작업을 완료 처리하기 전에 아래 필수 산출물이 생성되었는지 확인하세요.

**에이전트별 필수 문서:**

| 에이전트 | 필수 문서 |
|---------|---------|
| planner | `plan.md`, `exploration.md` |
| generator / refactorer | `implementation-log.md`, `final-summary.md` |
| watcher | `review-log.md` |
| evaluator | `evaluation-log.md` |

**저장 경로:** `.claude/logs/sessions/{날짜}-{작업명}/`

문서가 생성되지 않았다면 작업을 완료 처리하기 전에 반드시 작성하세요.
`artifacts` 필드에 명시된 파일이 실제로 존재해야 완료로 간주합니다.
