---
name: reference-ui-library-heroui
description: admin-ui·user-ui의 HeroUI v3 기반 shared/ui 어댑터를 재사용하거나 수정할 때 확인할 프로젝트별 버전·스타일·입출력 계약.
---

# HeroUI

이 문서의 구현 근거는 프로젝트별 절에 한정한다. 한 프로젝트의 어댑터 계약을 다른 프로젝트에 적용하지 않는다.

## admin-ui

### 목적과 확인 범위

버튼·선택·모달 등 기본 UI를 기존 디자인·입출력 계약으로 제공한다. 2026-09-30 관리자 프로젝트 `feature/ec-seller-ui`의 선언은 `@heroui/react ^3.2.3`, package-lock.json과 설치본은 **3.2.4**다. 사용자 프로젝트 또는 다른 major 버전에 그대로 적용하지 않는다.

기존 `src/shared/ui` 어댑터를 사용한다. `src/app/styles/heroui.css`에서 `tailwindcss`와 `@heroui/react/styles`를 import한다. 확인한 프로젝트 구성은 HeroUI Provider를 추가하지 않는다. 다른 버전의 초기화 코드를 혼합하지 않는다.

### 어댑터 계약

| 어댑터 | 프로젝트 입력 → 라이브러리 연결 |
| --- | --- |
| `button/button.tsx` | `onClick()` → `onPress`; `disabled` → `isDisabled`; `isLoading` → `isPending` |
| Button의 `className` | 전체 문자열이 `primary/secondary/outline/cancel/ghost/danger` 중 하나일 때 variant 매핑. 여러 클래스를 토큰별로 해석하지 않는다. 미일치 기본은 primary |
| Button의 `fullWidth` | 기본 true. 인라인 버튼에는 false 명시 |
| `dropdown/dropdown.tsx` | `index` → `Select.selectedKey`; `onSelect(type, index)`에 인덱스 전달. null 또는 같은 인덱스 재선택은 -1. 빈 items는 disabled |
| `modal/modal.tsx` | `open` → `Modal.Root.isOpen`; `onOpenChange(false)` → `close()` |

페이지·기능은 라이브러리를 직접 import하지 않고 공용 어댑터를 사용한다. EC의 key 기반 계약은 `widgets/ec-seller/ui/ec-select.tsx`가 index 기반 Dropdown을 감싼다. API key·DTO를 라이브러리 선택 상태로 직접 노출하지 않는다.

```tsx
import Button from "~/shared/ui/button/button";

<Button className="primary" fullWidth={false} onClick={onSubmit}>저장</Button>
```

모달 내용의 제목·접근성 이름, 선택 입력의 `ariaLabel`·label은 소비처에서 확인한다. 모달 닫힘은 위 callback에 연결되며 버전 변경 시 ESC·백드롭 동작도 검증한다. StatusBadge·Pagination·TextInput 등은 해당 컴포넌트 스킬과 실제 props를 별도로 읽는다. Table·KpiCard·FilterTabs는 이 문서만으로 HeroUI 컴포넌트라고 판단하지 않는다.

### 변경·검증

어댑터에서 의존을 관리하고 기존 호출 계약을 유지한다. 버전 갱신 시 lockfile, export, 스타일 순서, 선택·disabled·pending·모달 닫힘·키보드 접근성을 확인한다. 포맷 후 lint·build를 실행하며 빌드 통과만으로 화면·접근성 검증을 완료 처리하지 않는다.

## user-ui

### 확인 범위

2026-10-23 사용자 프로젝트 `sy-main` `fe49b87`을 확인했다. 선언은 `@heroui/react ^3.2.3`, package-lock.json과 설치본은 `@heroui/react`·`@heroui/styles` 모두 **3.2.3**이다. `src/index.css`에서 `@heroui/react/styles`를 import한다. 화면(feature·page)은 HeroUI를 직접 import하지 않고 `src/shared/ui/button`·`src/shared/ui/icon-button` 어댑터만 HeroUI `Button`을 감싼다.

### 어댑터 계약

| 어댑터 | 프로젝트 입력 → 라이브러리 연결 |
| --- | --- |
| `button/button.tsx` | `onClick()` → `onPress`; `disabled` → `isDisabled`; `isLoading` → `isPending`; `title` → `aria-label`. `fullWidth` 기본 true |
| Button의 `className` | 공백으로 나눈 토큰 중 처음 일치하는 `primary/secondary/outline/cancel(→secondary)/ghost/danger`로 variant를 고르고 전체 className은 그대로 전달한다. 미일치 기본은 primary. admin-ui와 해석 방식이 다르다(`button.test.tsx`) |
| `icon-button/icon-button.tsx` | `isIconOnly`; 접근 가능한 이름은 `aria-label`, 없으면 `title`. 토큰 `primary/primary-light(→secondary)/secondary/ghost/danger`, 미일치 기본은 secondary |

```tsx
import Button from "~/shared/ui/button/button";

<Button className="outline ec-order-card__detail" fullWidth={false} onClick={onOpen}>상세보기</Button>
```

### 생성 클래스와 크기 덮어쓰기

- HeroUI `Button`이 만드는 클래스는 `button`, `button--<size>`, `button--<variant>`, `button--icon-only` 등이다. 설치본에 `heroui-button` 클래스는 없으므로 `.heroui-button` 선택자는 어떤 요소에도 적용되지 않는다.
- 기본 크기는 `.button`의 `h-10 md:h-9`, `.button--icon-only`의 `w-10 p-0 md:w-9`로 768px 미만 40px, 이상 36px이다.
- 버튼 안 svg는 `.button svg`의 `size-5 sm:size-4`로 640px 미만 20px, 이상 16px이다. CSS가 SVG `width`·`height` 속성보다 우선하므로 lucide `size` prop만 바꾸면 표시 크기가 바뀌지 않는다. 크기를 바꾸려면 화면 CSS에서 `.<scope> .button svg`를 지정하고 `size` prop도 같은 값으로 맞춘다.
- HeroUI 스타일은 `@layer components` 안에 있어 layer 없이 import되는 화면 CSS가 specificity와 관계없이 우선한다.
- 덮어쓰기는 `src/shared/ui/search-state-bar/searchStateBar.css:26`처럼 화면 범위 클래스 아래의 `.button`을 대상으로 한다.

### 적용되지 않는 선택자

`fe49b87` 기준 `.heroui-button`을 대상으로 한 다음 규칙은 적용되지 않는다. 정리는 별도 작업이며 정리 후 이 목록을 갱신한다.

- `src/features/ec/ui/cart/ec-cart.css:33`
- `src/features/ec/ui/checkout/ec-checkout.css:22`
- `src/shared/ui/screen/screen.css:110`, `:148`
- `src/shared/ui/load-error/load-error.css:17`
- `src/features/citizen-participation/ui/parts/citizen-parts.css:105`, `:245`
- `src/features/meeting-reservation/ui/layout/meeting-reservation.css:33`

### 변경·검증

버전 갱신 시 생성 클래스 이름, 크기 utility, layer 순서와 disabled·pending·접근 가능한 이름을 확인한다. 크기 덮어쓰기는 640px·768px 경계 양쪽 화면에서 확인하며 빌드 통과만으로 화면 검증을 완료 처리하지 않는다.
