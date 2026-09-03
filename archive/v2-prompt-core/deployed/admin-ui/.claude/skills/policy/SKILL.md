---
name: policy-index
description: synthoria-admin-ui의 policy(횡단 정책) 카테고리 인덱스. 코드 작성/리뷰/리팩터 중 어떤 정책이 적용되는지 확인하거나, 새 횡단 규칙을 추가할지 판단해야 할 때 사용.
---

# Policy (synthoria-admin-ui)

> Policy = "어떤 작업이든 항상 적용되는 횡단 규칙".
> Reference/Recipe와 달리 특정 조각이나 플로우에 묶이지 않는다.

## 언제 이 스킬을 사용하나요?

- 코드 작성 직전, 적용 가능한 횡단 규칙을 일괄 점검할 때
- 리뷰/리팩터 시 판정 기준을 통일해야 할 때
- 작업 유형(구현/리뷰/리팩터)별로 적용할 정책을 선별할 때
- 새 횡단 규칙을 추가할지 판단할 때

---

## 1) 카탈로그

### 코드 정책 (어떤 작업이든 적용)

| Policy | 위치 | 다루는 규칙 |
| --- | --- | --- |
| `policy-coding-convention` | [coding-convention/SKILL.md](coding-convention/SKILL.md) | any 금지, type alias, functional component, early return, 네이밍/임포트 |
| `policy-type-definition` | [type-definition/SKILL.md](type-definition/SKILL.md) | interface vs type 결정 — 두 관계 간 계약(props·콜백·hook 반환·경계 DTO)이면 interface, 그 외 형태/유니온/파생이면 type |
| `policy-styles` | [styles/SKILL.md](styles/SKILL.md) | 이모지/SVG 처리, 공용 스타일 재사용 우선순위 |
| `policy-ui-library` | [ui-library/SKILL.md](ui-library/SKILL.md) | 외부 UI(HeroUI v3)는 shared/ui 어댑터로만 격리, feature/entities 직접 import 금지, UI 구현 전 HeroUI 검색+사용자 confirm, 채택 범위 |
| `policy-validation` | [validation/SKILL.md](validation/SKILL.md) | 유효성 표준 스택 zod+react-hook-form, 스키마=검증 계약(model), RHF 폼 훅(hook), 공용 어댑터(shared/ui/form), payload 매핑, 한글 에러 메시지 |

### 작업 절차 정책 (구현·리뷰 단계에서 적용)

| Policy | 위치 | 다루는 규칙 |
| --- | --- | --- |
| `policy-harness` | [harness/SKILL.md](harness/SKILL.md) | 승인 전 코드 생성 금지, SKILL 미확인 중단, retry 규칙 |
| `policy-publishing` | [publishing/SKILL.md](publishing/SKILL.md) | UI 구조/접근성/이벤트 계약 설계 단계의 범위 |
| `policy-refactoring` | [refactoring/SKILL.md](refactoring/SKILL.md) | 구조 개선 단계의 공통화 조건, 범위 분리, 기능 보존 |
| `policy-abstraction-strategy` | [abstraction-strategy/SKILL.md](abstraction-strategy/SKILL.md) | 추상화 4조건, 계약 vs 추상화, 강한/약한 추상화, closed vocabulary 트레이드오프 |
| `policy-hook-extraction` | [hook-extraction/SKILL.md](hook-extraction/SKILL.md) | 분리 판단 3-질문(진입 결정 절차·만능훅 안티패턴), hook 분리 기준(상태성), 도메인 전용 vs 공용 마이크로 hook, 3-layer 분리, searchState 패턴 |
| `policy-data-fetch-layer` | [data-fetch-layer/SKILL.md](data-fetch-layer/SKILL.md) | 데이터 페치 4계층(api.ts/useApi/fetch hook/modal hook/component) 책임 분리, ApiResult 계약, alert/pubsub 책임 위치 |
| `policy-review-checklist` | [review-checklist/SKILL.md](review-checklist/SKILL.md) | 구현 산출물 판정용 품질 게이트 체크리스트 |
| `policy-documentation` | [documentation/SKILL.md](documentation/SKILL.md) | 단계별 문서 작성, 로그 톤(결론 중심) |
| `policy-portfolio` | [portfolio/SKILL.md](portfolio/SKILL.md) | 이력서/포트폴리오용 경험 기록 — 문제·고민·결과·성과·회고 구조 |

---

## 2) Policy 작성/추가 기준

### 2-1. 신규 policy를 만드는 시점

다음 모든 항목이 참일 때만 새 policy를 만든다.

- 규칙이 **특정 조각/플로우에 한정되지 않고** 여러 도메인·여러 에이전트에 동일하게 적용된다
- "이 규칙을 어디에 둘지" reference/recipe로 분류 시 **소속이 모호하거나 중복 기재**가 된다
- 규칙 위반 시 **반려/escalation 사유가 될 만큼 중요**하다

### 2-2. 신규 policy를 만들지 않는 시점

- 한 컴포넌트/훅에 한정된 사용 규칙 → 해당 reference에 흡수
- 한 플로우 안에서만 의미 있는 절차 → 해당 recipe에 흡수
- 1회성 결정/임시 우회 → 코드 주석 또는 PR 설명으로 처리

### 2-3. 작성 표준

- frontmatter `description`은 **언제 적용되는가** 중심
- 본문 구조: `언제 이 스킬을 사용하나요?` / `규칙(또는 Principles)` / `금지` 3개 섹션이 기본
- 짧고 단정적으로. 횡단 규칙은 길면 잘 안 읽힌다 (대부분 50줄 이내)

---

## 3) Policy 적용 우선순위

같은 작업에 여러 policy가 동시 적용될 때:

1. `policy-harness` (실행 자체 차단 조건이 우선)
2. 코드 정책(`coding-convention`, `type-definition`, `styles`, `ui-library`, `validation`)
3. 단계 정책(`publishing`, `refactoring`)
4. `policy-review-checklist` (완료 직전 self-review)
5. `policy-documentation` (산출물 마무리)

> 호출 순서·분기·escalation 등 **역할에 의존하는 규칙은 스킬이 아니다.**
> 역할 계층 문서(`.harness/roles/orchestration.md`)에서 정의하며, 역할 개념이 있는 엔진에서만 적용된다.

---

## 4) Reference vs Recipe vs Policy 구분 표

| 질문 | 위치 |
| --- | --- |
| "이 조각이 뭘 하나?" | reference |
| "이 플로우를 어떻게 조립하나?" | recipe |
| "무엇을 지켜야 하나?" | policy |

특정 조각이나 플로우에 묶이지 않고 **항상 지켜야 하는 규칙**이라면 policy.
