---
name: reference-ui-library-lucide-react
description: admin-ui에서 lucide-react 아이콘을 선택하거나 line-icons 어댑터를 사용할 때 확인할 버전·접근성·import 계약.
---

# lucide-react

이 문서의 구현 근거는 `asan-metaverse-admin-ui`에 한정한다.

## 목적과 확인 범위

관리자 프로젝트의 기존 SVG 세트에 없는 커머스·지표 아이콘을 기존 의존성으로 제공한다. 2026-09-30 `feature/ec-seller-ui`의 package.json(`^1.25.0`), package-lock.json·설치본(`1.25.0`), `src/shared/assets/icons/line-icons.ts`를 확인했다. 다른 프로젝트나 버전에는 현재 계약을 재확인한다.

2026-10-02 어댑터가 판매자 브랜치의 `b6fc92d2eed80a4920cc4681bda7f44a3565a8f5`에 커밋된 상태를 재확인했다. 현재 worktree에 없으면 UI 자산 계획에서 재사용·인계 범위를 확인한다. 신규 설치가 필요한 프로젝트에는 기존 의존성이라는 설명을 적용하지 않는다.

## 구현 계약과 사용법

- 새 소비처는 직접 패키지 import 대신 `~/shared/assets/icons/line-icons`의 `<Name>LineIcon`을 사용한다. 기존 meeting 화면의 직접 import 정리는 별도 작업이다.
- 어댑터는 named re-export이며 `size`, `strokeWidth`, `className`, SVG 접근성 속성 등 원래 props를 유지한다. 색은 `currentColor`; 호출부 CSS의 width·height로 크기를 맞출 수 있다.
- 필요한 아이콘만 어댑터에 추가한다. 전체 namespace import나 모든 아이콘의 동적 registry는 만들지 않는다. named export는 미사용 export 제거를 지원하지만 실제 번들 크기 검증을 대신하지 않는다.
- 확인된 이름은 `Package`, `TrendingUp`, `TrendingDown`, `Minus`, `CircleCheck`, `CircleAlert`, `ChartColumn` 등이다. 이름 변경을 추정하지 말고 설치본의 export를 확인한다.
- 장식 아이콘은 `aria-hidden="true"`; 의미는 인접 텍스트나 부모의 접근성 이름으로 전달한다. 아이콘만 있는 버튼은 버튼 자체의 이름을 제공한다.

```tsx
import { PackageLineIcon } from "~/shared/assets/icons/line-icons";

<span className="nav-link__icon"><PackageLineIcon aria-hidden="true" /></span>
```

ReactNode를 받는 `.ts` 메뉴 모델에서는 `createElement(PackageLineIcon)`을 사용한다. EC 사용처는 `_navigation8.ts`, 공용 `TrendBadge`, 판매자 버튼·카드다. 어댑터 수정 후 타입 검사·lint·build에서 export와 사용처를 확인한다.
