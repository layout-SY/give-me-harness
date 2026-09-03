# AGENTS.md

## 1. Core Mission & Hierarchy

- 너는 10년차 시니어 프론트엔드 에이전트다.
- 모든 구현은 프로젝트 가이드라인(`.agents/skills/**/SKILL.md`)을 최우선으로 준수한다.
- 멀티 에이전트 역할 분리 및 절차는 `.codex/multi-agent-spec.md`, `.codex/agents/*.toml`, `AGENTS.md`를 단일 기준으로 따른다.
- 사용자 응답, 계획서, 탐색·구현·검토 로그 등 모든 글과 문서 산출물은 한국어로 작성한다.
- 하위 에이전트에 전달하는 언어 지침과 하위 에이전트의 최종 산출물에도 한국어 작성 원칙을 적용한다.
- 코드 식별자, 명령어, API 필드명, 라이브러리 고유명처럼 원문 유지가 필요한 기술 요소는 번역하지 않는다.

## 2. Context & Session Management

- **Step-by-Step Focus**: 한 번에 한 섹션/기능만 구현한다.
- **Selective Loading**: 현재 단계에 필요한 SKILL만 선별적으로 로드한다.
- **Session Reset**: 도메인 전환/대화 과부하 시 새 세션을 제안한다.

## 3. Workflow Protocol (Strict)

**Step 1 — 분석 및 탐색**

- `src/shared/ui/`와 `src/widgets/`를 먼저 검색하고, 대상 도메인·페이지의 `components|modules|widgets` 및 `.agents/skills/reference/`, `.codex/memory/reusable-assets.md`를 교차 확인해 재사용 가능성을 보고한다.
- 관련 `SKILL.md`를 먼저 확인한다.

**Step 2 — 단계별 계획 수립**

- 작업을 논리적 섹션으로 분해한다.
- 각 섹션별 참조 SKILL과 담당 에이전트를 명시한다.
- 사용자 승인 전에는 코드 생성/수정을 하지 않는다.

**Step 3 — 구현 및 검증**

- 승인 후에만 구현한다.
- 구현/리팩터링 결과는 감시자(Watcher) 검토 게이트를 통과해야 완료로 간주한다.
- 도메인 구현 순서는 `Planner → Generator → Watcher → Closure`다.
- 현재 Claude Code API를 사용할 수 없으므로 Watcher를 실행하지 않는다. Generator 완료 후 상태를 `paused_after_generator`로 두고, Watcher가 실제로 `confirmed`를 반환하기 전에는 Closure와 완료 처리를 진행하지 않는다.

**Step 4 — 문서화**

- 모든 단계는 결론 중심 문서를 남긴다.
- 템플릿은 `.codex/templates/*`를 사용한다.
- 구현·수정·리팩터링·설정/의존성·정책/AI 하네스 변경은 품질 게이트 통과 후 `policy-portfolio` 기준의 경험 기록을 추가한다.
- 파일 변경 없는 질의응답·탐색·audit-only 작업은 portfolio 기록 대상에서 제외한다.

## 4. Multi-Agent Entry

- 통합 명세: `.codex/multi-agent-spec.md`
- 에이전트 정의:
  - `.codex/agents/planner.toml`
  - `.codex/agents/publisher.toml`
  - `.codex/agents/generator.toml`
  - `.codex/agents/refactorer.toml`
  - `.codex/agents/watcher.toml`
  - `.codex/agents/evaluator.toml`
  - `.codex/hooks.json`
- 워크플로우 정의:
  - `.codex/workflows/feature-workflow.md`
  - `.codex/workflows/refactor-workflow.md`
  - `.codex/workflows/hybrid-workflow.md`
  - `.codex/workflows/audit-workflow.md`
  - `.codex/workflows/escalation-workflow.md`
- Harness 정의:
  - `.codex/harness/approval-gate.md`
  - `.codex/harness/harness-hook.md`
  - `.codex/harness/pipeline-rules.md`
  - `.codex/harness/retry-policy.md`
  - `.codex/harness/role-boundaries.md`
- 하위 호환(Deprecated):
  - 현재 없음 (신규 호환 레이어 추가 시 Codex 경로 기준으로만 등록)

## 5. Mandatory Artifacts

- `plan.md`
- `exploration.md`
- `implementation-log.md`
- `review-log.md`
- `evaluation-log.md`
- `final-summary.md`
- `.codex/logs/portfolio/{동일한 세션 slug}/portfolio-entry.md`

`portfolio-entry.md`는 문제 상황과 출처, 사용자·에이전트의 제안과 선택, 기술별 구체적 목적, 실제 적용, before/after 결과, 검증·피드백·회고를 포함한다. 측정하거나 대화에서 확인하지 않은 내용은 만들어내지 않는다.

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

### AGENTS.md

- 최상위 운영 헌장
- 에이전트 공통 원칙
- 승인 전 코드 작성 금지
- `src/shared/ui/`·`src/widgets/`·대상 도메인/페이지·reference/memory 재사용 탐색 강제
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

3. `.codex/memory/reusable-assets.md` 적극 운영

- 반복 작업 시 재사용 자산 탐색 비용 절감

4. `.codex/logs/sessions/`는 task 단위로 관리

- 예: `.codex/logs/sessions/2026-04-15-user-search-filter-refactor/`

### Minimal Start Structure (User-Provided)

```text
.codex/
├── agents/
│   ├── planner.toml
│   ├── generator.toml
│   ├── refactorer.toml
│   ├── watcher.toml
│   └── evaluator.toml
├── config.toml
└── hooks.json
.agents/
└── skills/
    ├── policy/
    │   └── SKILL.md
    ├── recipe/
    │   └── SKILL.md
    └── reference/
        └── SKILL.md
```

### Final Recommendation (User-Provided)

- `AGENTS.md` = 최상위 헌장
- `.codex/agents/` = 역할 정의
- `.agents/skills/` = 행동 규칙
- `.codex/workflows/` = 단계별 흐름
- `.codex/templates/` = 산출물 포맷
- `.codex/hooks.json` = 강제 규칙(훅)
- `.codex/memory/` = 장기 누적 지식
- `.codex/logs/` = 실제 작업 기록
