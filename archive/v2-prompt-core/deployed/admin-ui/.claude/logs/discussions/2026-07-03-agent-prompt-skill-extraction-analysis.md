# Agent Prompt — Skill 추출 가능성 분석

> 작성일: 2026-07-03
> 범위: `.claude/{agents,multi-agent-spec,harness,skills/policy}`
> 목적: 에이전트 프롬프트/스펙에 **중복되었거나 인라인된 behavior**를 식별하고, 별도 skill로 추출/통합할 후보를 우선순위화한다.
> 배경: hook/ui 분리 3-질문을 `policy-hook-extraction §0`으로 단일화하고 4개 에이전트가 참조하도록 전환한 작업의 후속 — 동일 패턴을 전면 점검.
> 상태: **분석·문서화만 완료. 실제 추출은 미실행(사용자 지정 대기).**

---

## 0. 판단 기준

- **agent = identity, skill = behavior** (CLAUDE.md 원칙). 에이전트 파일에 재사용 가능한 규칙(behavior)이 인라인되어 있으면 추출 후보.
- **중복 정본화**: 같은 규칙이 여러 파일에 서술되면 divergence 위험 → 정본 1곳 + 나머지 참조.
- **신규 policy 최소화**: 프로젝트 policy 원칙상, 가능하면 기존 policy에 흡수. 신규는 소속이 모호할 때만.

---

## 1. 중복 지도 (grep 실측)

| 구문/규칙 | 출현 위치 | 성격 |
| --- | --- | --- |
| 권한 거부 폴백 "Approach A" (`prepared_changes`) | `agents/generator.md`, `agents/refactorer.md` | **12줄 verbatim**(agent명·조사만 상이) |
| 구현 판단 위임(`policy-abstraction-strategy`) | `agents/generator.md`, `agents/refactorer.md` | 거의 동일 |
| 신규 자산 문서화(watcher pass 후) | `agents/generator.md`, `multi-agent-spec/02` (+refactorer의 유사 블록) | 동일 규칙 |
| retry/반려 루프(`최대 3회`, `repeat_issue_detected`) | `agents/watcher.md`, `harness/retry-policy.md`, `multi-agent-spec/03` | **3중 중복** |
| per-invocation 종료/맥락 복원 | `agents/{planner,refactorer,watcher}`, `multi-agent-spec/{02,03}` | 개념 반복 |
| 상태 봉투 YAML 공통 필드 | 6개 agent + `harness/harness-hook.md` | 필드 반복(정본 `templates/agent-output-schema.yaml` 존재) |
| `code-simplifier` 위임 | `agents/{refactorer,watcher}`, `multi-agent-spec/03` | 반복 |
| `frontend-design` 위임 | `agents/publisher.md`, `multi-agent-spec/02` | 반복 |
| portfolio-entry 규칙 | `agents/{generator,planner,refactorer}`, `skills/policy/portfolio` | 정본은 policy, agent는 참조 중(양호) |

### 근거: 권한 거부 폴백 verbatim 확인
`generator.md` vs `refactorer.md`의 "## 권한 거부 시 폴백" 블록 diff 결과 — **의미 차이 0**, agent 이름과 문구 축약만 상이. 이미 copy-paste divergence가 시작됨(예: "동일 호출 재시도 금지, 다른 파일로 우회 금지" vs "재시도/우회 금지").

---

## 2. 추출 후보 (우선순위)

### P0 — verbatim 중복, 즉시 추출

#### ① 권한 거부 폴백 "Approach A"
- 위치: `generator.md` + `refactorer.md` (12줄 동일)
- 성격: 순수 behavior (도구 거부 → `decision: hold` + `denied_tool_calls`/`prepared_changes` + 2회 거부 시 `settings.local.json` 점검 요청)
- **권장**: 신규 `policy-tool-permission-fallback` **또는** `policy-harness`에 흡수 → 두 에이전트는 1줄 참조.

#### ② 구현 판단 위임 규칙 ("필수 동작 항목")
- 위치: `generator.md` + `refactorer.md` (거의 동일)
- 내용: 추상화→`policy-abstraction-strategy` / hook→`policy-hook-extraction` 기준 적용, 모호·레이어충돌 시 planner 경유·사용자 질의(본인 의견 첨부), 결정은 log 기록
- **권장**: 신규 `policy-implementer-judgment` — 세부 기준은 이미 정책 참조이므로 **"언제 위임/에스컬레이트하고 어디에 기록하나"의 공통 절차만** 추출.

#### ③ 신규/변경 자산 문서화 (watcher pass 후)
- 위치: `generator.md` + `refactorer.md` + `multi-agent-spec/02`
- 내용: 신규 공용→reference 작성 / 영향→갱신 / 도메인종속→`domain/` 하위 / portfolio-entry
- **권장**: 기존 `policy-documentation`에 흡수 → 에이전트는 참조.

### P1 — 다중 소스 통합(단일화)

#### ④ retry/반려 루프 — 3중 중복
- 위치: `watcher.md` + `harness/retry-policy.md` + `multi-agent-spec/03`
- **권장**: 정본 1곳(`policy-harness` 또는 `harness/retry-policy.md`)만 두고 나머지 참조.

#### ⑤ per-invocation 종료 / 맥락 복원
- 위치: planner·refactorer·watcher + spec 2곳
- **권장**: `policy-orchestration`(또는 harness)에 "실행 단위·맥락 복원" 1절로 단일화.

#### ⑥ 상태 봉투(YAML envelope) 공통 필드
- 위치: 6개 agent + harness-hook
- **권장**: 이미 존재하는 `templates/agent-output-schema.yaml`을 정본화 → 각 agent는 *고유 필드만* 선언 + 공통 봉투는 스키마 참조.

### P1 — 단일 위치이나 behavior라 skill이 적합

#### ⑦ planner Explore 병렬 탐색 프로토콜(A/B/C 각도)
- `planner.md` 단독. 재사용 가능한 "탐색 레시피" → recipe/policy 후보(단일 사용이라 우선순위 중).

#### ⑧ publisher `frontend-design` 위임
- `publisher.md` + `spec/02` 소규모 → `policy-publishing`에 흡수.

---

## 3. 메타 관찰 — 거버넌스 3중 서술

승인 게이트·역할 경계·retry 규칙이 **4곳**에 분산:
```
harness/*.md (approval-gate·pipeline-rules·retry-policy·role-boundaries)
skills/policy/harness/SKILL.md
multi-agent-spec/*
각 agent 인라인
```
divergence 위험이 큼. **정본을 `policy-harness` 하나로** 두고, `harness/*.md`는 hookify 실제 훅 등록 전용으로 축소, spec/agent는 참조만 하도록 정리하는 것이 최대 정합성 이득. (단, 큰 결정이라 별도 합의 필요.)

---

## 4. 권장 처리 순서 (ROI)

1. ①·③ — verbatim, 위험 0·이득 큼 (즉시)
2. ④ retry 3중 통합 — divergence 이미 시작됨
3. ② 구현자 판단 위임 — 신규 `policy-implementer-judgment`
4. ⑥ 상태 봉투 정본화 — 스키마 파일 이미 존재, 연결만
5. 메타 통합(harness 단일화) — 합의 후

**신규 skill 최소안**: ①·② 2개만 신규, 나머지는 기존 `policy-harness`/`policy-documentation`/`policy-orchestration`/`templates` 흡수.

---

## 5. 다음 액션
- 사용자가 추출 대상 지정 시 각 항목을 skill로 이관 + 에이전트는 참조로 치환.
- 실행 시 backlog에 `SKILL-EXT-0x` 티켓으로 승격 가능.
