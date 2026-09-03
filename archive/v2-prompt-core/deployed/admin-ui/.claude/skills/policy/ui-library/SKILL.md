---
name: policy-ui-library
description: synthoria-admin-ui에서 외부 UI 라이브러리(현재 HeroUI v3)를 사용할 때의 횡단 규칙. 외부 UI는 shared/ui 어댑터로만 감싸고 feature/entities는 어댑터만 사용(직접 import 금지). UI 구현 전 HeroUI 항목 검색 후 사용자 confirm. 버튼/토글 등 프리미티브·날짜 선택을 구현·교체할 때 사용.
---

# UI Library (Policy)

> **표준 외부 UI 라이브러리 = HeroUI v3** (`@heroui/react`, React Aria + Tailwind v4 기반).
> 핵심 원칙: **외부 UI는 shared/ui 어댑터 뒤에 격리한다.** feature/entities/pages/widgets는 HeroUI를 직접 import 하지 않고, 어댑터(`shared/ui/*`)만 사용한다. → 라이브러리 교체 시 어댑터만 수정하면 된다(anti-corruption layer).

## 언제 이 스킬을 사용하나요?

- 버튼/입력/토글/뱃지/로딩/페이지네이션 등 UI 프리미티브를 구현·교체할 때
- 드롭다운(Select)/모달(Modal)/사이드모달(Drawer)을 구현할 때
- 날짜 선택 UI를 구현할 때
- 새 UI 컴포넌트를 shared/ui에 추가할지 판단할 때

---

## 1. 어댑터 경계 규칙 (필수)

- `@heroui/react`(및 `react-aria*`) **import는 오직 `shared/ui/*` 어댑터 파일 안에서만** 허용한다.
- `features/`, `entities/`, `widgets/`, `pages/`, `app/`에서 HeroUI를 직접 import 하면 **위반**(리뷰 반려 사유).
- 어댑터는 프로젝트 고유 **props 계약(interface)** 을 노출하고, 내부에서 HeroUI로 렌더한다. 소비처는 HeroUI API(compound·naming·타입)를 몰라야 한다.
- 어댑터 props는 계약이므로 `interface`(`policy-type-definition`).

### HeroUI v3 특이사항(어댑터가 흡수)
- **Provider 불필요**(v3). `<HeroUIProvider>` 사용 안 함.
- Tailwind v4 필수 — `@tailwindcss/vite` + `@import "tailwindcss"` + `@import "@heroui/react/styles"`(이미 배선됨).
- compound API: `Select.Item`(≠ `SelectItem`), 이름 케이스 `TextArea`(≠ `Textarea`) 등. 어댑터에서만 다룬다.
- 날짜 컴포넌트는 `@internationalized/date`의 `CalendarDate` 기반 → 어댑터가 문자열(`YYYY-MM-DD`) ↔ CalendarDate 변환을 흡수한다.

---

## 2. UI 구현 전 절차 (필수 — 사용자 confirm)

UI 컴포넌트를 신규 구현하거나 교체하기 전:

1. **HeroUI 카탈로그에서 해당 항목을 검색**한다(예: 날짜 → DateRangePicker/DatePicker, 토글 → Switch). export 여부·props를 실제 패키지(`node_modules/@heroui/react`)로 확인한다.
2. 찾은 HeroUI 컴포넌트와 어댑터 매핑안을 **사용자에게 제시하고 confirm을 받는다.**
3. **confirm 전에는 어댑터/구현 코드를 작성하지 않는다.** (CLAUDE.md 승인 게이트와 별개로, UI는 항목 선택 확인이 추가 게이트다.)
4. HeroUI에 마땅한 항목이 없으면(예: 파일 업로더·이미지 뷰어) 커스텀 유지를 제안한다.

> **HeroUI vs frontend-design 역할 구분**: HeroUI(어댑터)는 **UI 조각(프리미티브·컨트롤)** 을 제공한다. **페이지/컴포넌트 레이아웃(배치·그리드·간격·반응형·시각 계층)** 은 라이브러리와 무관하게 `frontend-design` 스킬의 상시 책임이다. 즉 `frontend-design`은 "HeroUI에 없을 때의 대체"가 아니라, HeroUI 어댑터와 커스텀 조각을 레이아웃으로 조립하는 역할을 겸한다.

---

## 3. 현재 채택 범위 (확정)

| 대상 | 결정 |
| --- | --- |
| button, icon-button, text-input, text-area, toggle-switch, loading, pagination, badge(author/category/status) | **HeroUI 어댑터로 교체** (Button, Input, TextArea, Switch, Spinner, Pagination, Chip) |
| dropdown → Select, modal → Modal, side-modal → Drawer | **HeroUI 어댑터로 교체** |
| **table** | **현행 유지** (HeroUI 교체 안 함 — 커스텀 fetch adapter/columnDef 표면 큼) |
| 날짜 선택(calendar-picker) | HeroUI **DateRangePicker/DatePicker** 로. **week-from-click 기능 제거**, behavior 주입 추상화 수준을 낮춘다(단순 range 중심). |
| fade-in, image-upload, image-modal, no-results, form(어댑터), reason-prompt, search-state-bar | **커스텀 유지** (HeroUI 등가물 없음/합성) |

---

## 금지

- feature/entities/widgets/pages/app에서 `@heroui/react`·`react-aria*` 직접 import
- 어댑터 없이 HeroUI 컴포넌트를 화면에 직접 사용
- 사용자 confirm 없이 UI 컴포넌트 신규 구현/교체
- HeroUI API(compound/naming/CalendarDate)를 소비처로 노출
- table을 HeroUI로 교체(현행 유지)
- week-from-click 등 제거 대상 날짜 정책을 다시 도입
