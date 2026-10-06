---
name: reference-ui-library-heroui
description: admin-ui에서 HeroUI v3를 src/shared/ui 어댑터로만 사용하는 계약(EC 판매자 화면 기준 확인분)
---

# HeroUI 사용 계약

> 세션 초안 — 중앙 등록 전. 대상 프로젝트: `asan-metaverse-admin-ui`. 이번 작업은 새 HeroUI 컴포넌트를 추가하지 않고 기존 어댑터만 사용했다.

## 목적과 적용 범위

- 요구: EC 판매자 화면의 버튼·선택·모달·상태 칩·페이지네이션·스위치·텍스트 영역을 기존 디자인과 같은 컴포넌트로 구성한다.
- 적용: `Button`, `IconButton`, `Dropdown`(Select), `Modal`, `StatusBadge`(Chip), `Pagination`, `TextInput`(InputGroup), `TextArea`, `DateRangePicker`, `Tabs` 어댑터.
- 제외: 새 탭 필터는 HeroUI `Tabs`(패널 결합)를 쓰지 않고 `shared/ui/filter-tabs`를 새로 만들었다.
- 문서 상태: 구현 확인(기존 어댑터 사용처 기준)

## 버전과 근거

- 패키지: `@heroui/react` 선언 `^3.2.3`. 전역 스타일 `src/app/styles/heroui.css`(`@import "tailwindcss"; @import "@heroui/react/styles";`), Provider 불필요.

## 구현 방식과 계약

- 어댑터 경로: `src/shared/ui/*`. 기능·페이지 코드는 `@heroui/react`를 직접 import하지 않는다.
- `Button`: `className` 토큰(`primary|secondary|outline|ghost|danger|cancel`) → HeroUI `variant`. `fullWidth` 기본 true이므로 인라인 버튼은 `fullWidth={false}`를 준다. `onClick`은 `onPress`로 매핑된다.
- `Dropdown`: index 기반(`index`, `onSelect(type, index)`), 같은 항목 재선택은 -1(해제). EC에서는 `widgets/ec-seller/ui/ec-select.tsx`가 key 기반 계약으로 감싼다.
- `Modal`: `open`, `close`. ESC·백드롭 닫힘은 HeroUI 기본 동작.
- `StatusBadge`: `color`(positive|neutral|warning|danger|info|deleted)를 호출부가 지정하면 코드 기반 기본 매핑을 쓰지 않는다.
- `Table`(HeroUI 아님)은 항상 `Pagination`을 렌더링한다. 짧은 표는 호출부 CSS에서 숨긴다(`.ec-table-static`).

## 사용법

```tsx
import Button from "~/shared/ui/button/button";

<Button className="primary" fullWidth={false} onClick={onSubmit}>저장</Button>
```

## 제약과 검증

- 검증: `npm run lint`, `npm run build` 통과(2026-09-30).
- 미확정: 기존 어댑터 전체의 props 문서화는 이번 범위 밖.

## 중앙 등록·갱신

- 세션 초안: `.claude/logs/sessions/ec-seller-ui/unknown/ui-library-skills/heroui/SKILL.md`
- 대상 중앙 경로: `policy/common/skills/reference/libraries/heroui/SKILL.md` (주입 번들에서 기존 정본 미확인)
- 상태: 미등록 — 중앙 저장소 작업으로 인계.
