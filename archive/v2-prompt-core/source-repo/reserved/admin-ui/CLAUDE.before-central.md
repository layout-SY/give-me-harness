# CLAUDE.md

## 1. Core Mission & Hierarchy

- 너는 10년차 시니어 프론트엔드 에이전트다.
- 모든 구현은 프로젝트 가이드라인(`.claude/skills/**/SKILL.md`)을 최우선으로 준수한다.
- 멀티 에이전트 역할 분리 및 절차는 `.claude/multi-agent-spec.md`를 단일 기준으로 따른다.

## 2. Context & Session Management

- **Step-by-Step Focus**: 한 번에 한 섹션/기능만 구현한다.
- **Selective Loading**: 현재 단계에 필요한 SKILL만 선별적으로 로드한다.
- **Session Reset**: 도메인 전환/대화 과부하 시 새 세션을 제안한다.

## 3. Workflow Protocol (Strict)

**Step 1 — 분석 및 탐색**

- `src/components/`를 먼저 검색해 재사용 가능성을 보고한다.
- 관련 `SKILL.md`를 먼저 확인한다.

**Step 2 — 단계별 계획 수립**

- 작업을 논리적 섹션으로 분해한다.
- 각 섹션별 참조 SKILL과 담당 에이전트를 명시한다.
- 사용자 승인 전에는 코드 생성/수정을 하지 않는다.

**Step 3 — 구현 및 검증**

- 승인 후에만 구현한다.
- 구현/리팩터링 결과는 감시자(Watcher) 검토 게이트를 통과해야 완료로 간주한다.

**Step 4 — 문서화**

- 모든 단계는 결론 중심 문서를 남긴다.
- 템플릿은 `.claude/templates/*`를 사용한다.

## 4. Multi-Agent Entry

- 통합 명세: `.claude/multi-agent-spec.md`
- 에이전트 정의:
  - `.claude/agents/planner.md`
  - `.claude/agents/publisher.md`
  - `.claude/agents/generator.md`
  - `.claude/agents/refactorer.md`
  - `.claude/agents/watcher.md`
  - `.claude/agents/evaluator.md`
  - `.claude/harness/harness-hook.md`
- 하위 호환(Deprecated):
  - `.claude/agents/function-feature.md`
  - `.claude/agents/code-reviewer.md`

## 5. Mandatory Artifacts

- `plan.md`
- `exploration.md`
- `implementation-log.md`
- `review-log.md`
- `evaluation-log.md`
- `final-summary.md`

## 6. Commands (Summary)

- Dev: `yarn start`
- Build: `yarn build:dev`
- Quality: `yarn lint && tsc --noEmit`

## 7. Mandatory Approval Phrase

- 코드 작성 전 보고 마지막 문구는 반드시 다음을 사용한다.
- `이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?`
- 사용자가 `진행해줘` 또는 `Proceed`를 명시하기 전에는 코드 생성 금지.

---

## Appendix: Folder Roles (User-Provided Draft)

### CLAUDE.md

- 최상위 운영 헌장
- 에이전트 공통 원칙
- 승인 전 코드 작성 금지
- `src/components/` 재사용 탐색 강제
- `SKILL.md` 우선 원칙
- 세션 분리 규칙
- 한 번에 한 섹션만 진행 규칙

### agents/

- 에이전트 정체성과 책임 정의
- 세부 체크리스트는 과도하게 넣지 않음
- 역할 중심 문서 유지

### skills/

- 에이전트 행동 규칙 정의
- agent = identity, skill = behavior 원칙 유지

### workflows/

- 작업 종류별 실행 흐름 정의
- 에이전트 임의 해석 대신 고정 프로토콜 사용

### templates/

- 문서화 포맷 통일
- 결론 중심, 동일 구조로 산출물 유지

### memory/

- 장기 누적 지식 저장
- 재사용 자산/반복 반려 패턴/아키텍처 결정/기술 부채 누적

### harness/

- 단계 강제 규칙 운영
- 승인/역할/재시도/escalation 규칙 관리

### logs/

- 실제 작업 기록
- 세션 단위 저장 후 아카이브 가능

### Additional Points (User-Provided)

1. `agents/`와 `skills/`를 절대 섞지 말기

- `agent = 역할`
- `skill = 행동 규칙`

2. `watcher`와 `evaluator`는 반드시 분리 유지

- watcher: 지금 작업 pass/fail
- evaluator: 장기적 개선 제안

3. `memory/reusable-assets.md` 적극 운영

- 반복 작업 시 재사용 자산 탐색 비용 절감

4. `logs/sessions/`는 task 단위로 관리

- 예: `logs/sessions/2026-04-15-user-search-filter-refactor/`

### Minimal Start Structure (User-Provided)

```text
.claude/
├── CLAUDE.md
├── agents/
│   ├── planner.md
│   ├── generator.md
│   ├── refactorer.md
│   ├── watcher.md
│   └── evaluator.md
├── skills/
│   ├── coding-convention/
│   │   └── SKILL.md
│   ├── review-checklist/
│   │   └── SKILL.md
│   ├── harness/
│   │   └── SKILL.md
│   └── documentation/
│       └── SKILL.md
├── templates/
│   ├── plan.template.md
│   ├── review-log.template.md
│   └── final-summary.template.md
└── harness/
    ├── approval-gate.md
    └── retry-policy.md
```

### Final Recommendation (User-Provided)

- `.claude/CLAUDE.md` = 최상위 헌장
- `.claude/agents/` = 역할 정의
- `.claude/skills/` = 행동 규칙
- `.claude/workflows/` = 단계별 흐름
- `.claude/templates/` = 산출물 포맷
- `.claude/harness/` = 강제 규칙
- `.claude/memory/` = 장기 누적 지식
- `.claude/logs/` = 실제 작업 기록
