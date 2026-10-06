---
name: reference-ui-library-lucide-react
description: admin-ui에서 lucide-react 라인 아이콘을 공용 어댑터(line-icons)로만 사용하는 계약과 사용법
---

# lucide-react 사용 계약

> 세션 초안 — 중앙 등록 전. 대상 프로젝트: `asan-metaverse-admin-ui` (`feature/ec-seller-ui`).

## 목적과 적용 범위

- 해결할 요구·선택 이유: 기존 `src/shared/assets/icons/*.icon.tsx` SVG 세트에 커머스·지표 아이콘(상자, 지폐, 트럭, 추세 화살표 등)이 없다. lucide-react는 이미 의존성에 있고 `src/features/meeting/ui/*`에서 사용 중이라 신규 의존성 없이 사용한다.
- 적용 UI: EC 판매자 사이드바 메뉴 아이콘(`_navigation8.ts`), KPI 카드 아이콘, 증감 뱃지(`TrendBadge`), EC 화면 버튼·카드 제목 아이콘.
- 제외: 기존 화면의 `*.icon.tsx` 교체(범위 밖), meeting feature의 직접 import 정리(범위 밖).
- 문서 상태: 구현 확인

## 버전과 근거

- 패키지: `lucide-react`, 선언 `^1.25.0`, lockfile 설치 `1.25.0`.
- 확인: 설치본에서 사용 아이콘 export 존재를 node로 확인(`LayoutDashboard`, `Package`, `TrendingUp` 등 누락 0건). 1.x에서는 `CheckCircle` → `CircleCheck`, `AlertCircle` → `CircleAlert`, `BarChart` 계열 → `ChartColumn` 등 새 이름을 쓴다.

## 구현 방식과 계약

- 어댑터: `src/shared/assets/icons/line-icons.ts`. lucide 컴포넌트를 `<이름>LineIcon` 별칭으로 named re-export한다. 기능 코드는 `lucide-react`를 직접 import하지 않는다.
- props: lucide 컴포넌트 props 그대로(`className`, `size`, `aria-hidden` 등). 색은 `currentColor`, 크기는 호출부 CSS의 `width/height`로 제어한다.
- 접근성: 장식용은 `aria-hidden="true"`. 의미가 있으면 인접 텍스트나 부모의 `aria-label`로 이름을 준다.
- 새 아이콘이 필요하면 어댑터에 named export를 추가한다(`import *` 금지, tree-shaking 유지).

## 사용법

```tsx
import { PackageLineIcon } from "~/shared/assets/icons/line-icons";

<span className="nav-link__icon"><PackageLineIcon aria-hidden="true" /></span>
```

- 메뉴 모델처럼 ReactNode가 필요한 곳은 `createElement(PackageLineIcon)`으로 만든다(`_navigation8.ts`).

## 제약과 검증

- 번들: named import라 사용 아이콘만 포함된다. 신규 의존성 없음.
- 검증: `npm run lint`, `npm run build` 통과(2026-09-30, `feature/ec-seller-ui`).
- 미확정: meeting feature의 직접 import를 어댑터로 옮길지 여부.

## 중앙 등록·갱신

- 세션 초안: `.claude/logs/sessions/ec-seller-ui/unknown/ui-library-skills/lucide-react/SKILL.md`, 자산 계획 `unknown/ui-asset-plan.md`.
- 대상 중앙 경로: `policy/common/skills/reference/libraries/lucide-react/SKILL.md` (기존 정본 없음).
- 상태: 미등록 — 중앙 저장소 작업으로 인계.
