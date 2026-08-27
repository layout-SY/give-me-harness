# evaluation-log.md

## Stage
- Agent: evaluator (orchestrator 직접 수행)
- Date: 2026-04-21
- Target: `.claude/agents/` 전체, `harness-hook.md`, `multi-agent-spec/`
- Status: recommendation_ready → implemented

---

## Diagnosis

### 문제 1 — 에이전트 도구 정의 불일치

**설계 의도** (`multi-agent-spec/06`, `multi-agent-spec/01`):
- 모든 에이전트는 "자신의 필수 산출물을 모두 생성했을 때" 종료
- "문서화 없이 완료 처리 금지"

**실제 구현 불일치:**

| 에이전트 | 수정 전 tools | 문제 |
|---------|-------------|------|
| planner | Read, Grep, Glob, Bash | Write 누락 → plan.md, exploration.md 작성 불가 |
| watcher | Read, Grep, Glob, Bash | Write 누락 → review-log.md 작성 불가 |
| evaluator | Read, Grep, Glob, Bash | Write 누락 → evaluation-log.md 작성 불가 |
| generator | Read, Grep, Glob, Bash, **Modify, Create** | 유효하지 않은 도구명 (Modify→Edit, Create→Write) |
| refactorer | Read, Grep, Glob, Bash, **Modify, Create** | 동일 |
| publisher | Read, Grep, Glob, Bash, **Modify, Create** | 동일 |

- **리스크: High** — 물리적으로 파일 작성이 불가능한 상태였음

### 문제 2 — Harness가 자율 준수에만 의존

`harness-hook.md:61`:
> "이 문서의 규칙은 LLM 자율 준수에 의존한다"

hookify 등록 파일이 전혀 없었음. "문서화 누락 시 단계 이동 차단" 규칙이 선언되어 있어도
실제 강제 메커니즘이 없어 에이전트가 무시해도 차단 불가.

- **리스크: High**

---

## Architectural Risks

- 에이전트 도구 정의에 유효하지 않은 도구명(`Modify`, `Create`) 사용 → Claude Code 런타임이 무시
- Harness 규칙이 문서에만 존재하고 설정 파일에 등록되지 않아 강제력 없음
- 문서화 책임 소재가 에이전트인지 orchestrator인지 시스템 설계 상 명시되어 있지 않아 혼선

---

## Applied Fixes

### 1. 에이전트 도구 수정

| 에이전트 | 수정 전 | 수정 후 |
|---------|--------|--------|
| planner | Read, Grep, Glob, Bash | Read, Grep, Glob, Bash, **Write** |
| watcher | Read, Grep, Glob, Bash | Read, Grep, Glob, Bash, **Write** |
| evaluator | Read, Grep, Glob, Bash | Read, Grep, Glob, Bash, **Write** |
| generator | ..., Modify, Create | ..., **Edit, Write** |
| refactorer | ..., Modify, Create | ..., **Edit, Write** |
| publisher | ..., Modify, Create | ..., **Edit, Write** |

### 2. Hookify 등록

- 파일: `.claude/hookify.require-documentation.local.md`
- 이벤트: `stop`
- 액션: `warn`
- 트리거: 에이전트가 작업을 완료 처리하려 할 때마다 문서화 체크리스트 주입

---

## Recommended Backlog

1. **[즉시 완료]** 에이전트 도구 정의 수정 — ✅ 완료
2. **[즉시 완료]** hookify 문서화 규칙 등록 — ✅ 완료
3. **[중기]** `harness-hook.md` "자율 준수 한계" 섹션 업데이트 — hookify 등록 완료 상태 반영
4. **[중기]** 각 에이전트 정의에 "세션 로그 경로" 명시 — 에이전트가 어느 경로에 파일을 써야 하는지 가이드 부재

---

## Suggested Next Step

hookify 등록으로 stop 이벤트마다 문서화 체크리스트가 주입되므로,
다음 에이전트 실행 시 실제 경고가 발생하는지 확인한다.
`harness-hook.md` 업데이트는 별도 작업으로 진행한다.
