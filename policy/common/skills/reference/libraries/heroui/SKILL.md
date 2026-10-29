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
| `category/category-badge.tsx` | `category`(대문자로 정규화해 `title`·`data-category`), `color?`(`purple/gray/green/blue` → Chip `accent/default/success/accent`), `label?`, `imageUrl?`. 빈 `category`는 `null`. 아래 `### Chip` 참조 |
| `status/status-badge.tsx` | `status?`, `label`, `variant?`(`default/compact` → Chip `size` `md/sm`), `color?`. `status`가 없으면 Chip 없이 `-`를 표시 |

페이지·기능은 라이브러리를 직접 import하지 않고 공용 어댑터를 사용한다. EC의 key 기반 계약은 `widgets/ec-seller/ui/ec-select.tsx`가 index 기반 Dropdown을 감싼다. API key·DTO를 라이브러리 선택 상태로 직접 노출하지 않는다.

```tsx
import Button from "~/shared/ui/button/button";

<Button className="primary" fullWidth={false} onClick={onSubmit}>저장</Button>
```

모달 내용의 제목·접근성 이름, 선택 입력의 `ariaLabel`·label은 소비처에서 확인한다. 모달 닫힘은 위 callback에 연결되며 버전 변경 시 ESC·백드롭 동작도 검증한다. Pagination·TextInput 등은 해당 컴포넌트 스킬과 실제 props를 별도로 읽는다. Table·KpiCard·FilterTabs는 이 문서만으로 HeroUI 컴포넌트라고 판단하지 않는다.

### Chip

2026-10-27 `feature/ec-admin-ui` `d101e48`(sy-main 미병합)의 `CategoryBadge`·`StatusBadge`와 설치본 3.2.4를 확인했다. 알약 안 왼쪽에 원형 이미지를 넣는 사용법이 이 절의 대상이다.

- HeroUI `Chip`(`dist/components/chip/chip.js`)은 `children`이 문자열·숫자일 때만 `ChipLabel`(`span[data-slot="chip-label"]`, `.chip__label`)로 감싼다. fragment·요소·배열은 그대로 렌더한다. `Chip`은 `Chip.Root`·`Chip.Label`을 가진 compound다.
- 문자열 라벨은 그대로 넘긴다. `Chip.Label`로 다시 감싸면 `.chip__label`이 이중으로 생긴다.
- 이미지와 라벨을 함께 넣을 때는 자동 감싸기가 없다. `<img>`를 Chip의 직계 자식으로 두고 라벨만 `<Chip.Label>`로 감싼다. 이미지는 `.chip`의 flex 정렬과 gap을 그대로 받는다.
- 이미지는 옆 라벨과 같은 정보이므로 장식 이미지(`alt=""`)로 두고 `loading="lazy"`를 준다. 의미는 텍스트 라벨이 전달한다.
- `.chip`·`.chip__label`과 수정자는 `layer(components)` 안에 있다. layer 밖의 어댑터 CSS가 명시도와 관계없이 우선하므로 `.category-badge--with-image .chip__label { padding-left: 0 }`, `.status-badge .chip__label { padding-inline: 0 }`이 HeroUI 기본 여백을 덮는다. 어댑터 CSS를 `@layer` 안으로 옮기거나 HeroUI 스타일 import 방식을 바꾸면 이 우선순위가 바뀌므로 알약 여백과 색을 다시 확인한다.
- `Chip`은 `shared/ui` 어댑터(`category-badge`, `status-badge`, `author/author-badge`) 안에서만 import한다. 기능·페이지는 어댑터를 쓰고 `Chip`·`.chip*` class를 직접 쓰지 않는다. 색·라벨·이미지 URL은 호출부가 정해 넘기며 어댑터는 API·상태를 모른다.

```tsx
// CategoryBadge 내부: imageUrl이 공백이 아닌 문자열일 때만 이미지를 그린다.
<Chip className={`category-badge category-badge--${color} category-badge--with-image`} color="accent">
  <img className="category-badge__image" src={imageUrl} alt="" loading="lazy" />
  <Chip.Label>{label}</Chip.Label>
</Chip>

// 사용처
<CategoryBadge category="POLICY" color="blue" label="정책" />
<CategoryBadge category={item.label} label={item.label} imageUrl={item.iconUrl} color={item.color} />
```

### 변경·검증

어댑터에서 의존을 관리하고 기존 호출 계약을 유지한다. 버전 갱신 시 lockfile, export, 스타일 순서, 선택·disabled·pending·모달 닫힘·키보드 접근성을 확인한다. 포맷 후 lint·build를 실행하며 빌드 통과만으로 화면·접근성 검증을 완료 처리하지 않는다.

## user-ui

### 확인 범위

2026-10-23 사용자 프로젝트 `sy-main` `fe49b87`을 확인했다. 선언은 `@heroui/react ^3.2.3`, package-lock.json과 설치본은 `@heroui/react`·`@heroui/styles` 모두 **3.2.3**이다. `src/index.css`에서 `@heroui/react/styles`를 import한다. 화면(feature·page)은 HeroUI를 직접 import하지 않는다. `src/shared/ui/`의 어댑터가 HeroUI를 감싼다. 이 문서는 `button`·`icon-button`(`fe49b87`)과 `text-area`(2026-10-27 `5db3f5b`) 어댑터를 확인했다. 그 밖의 어댑터(`dropdown`, `text-input`, `date-picker`, `chip-group`, `toggle-switch` 등)는 실제 파일을 읽고 판단한다.

### 어댑터 계약

| 어댑터 | 프로젝트 입력 → 라이브러리 연결 |
| --- | --- |
| `button/button.tsx` | `onClick()` → `onPress`; `disabled` → `isDisabled`; `isLoading` → `isPending`; `title` → `aria-label`. `fullWidth` 기본 true |
| Button의 `className` | 공백으로 나눈 토큰 중 처음 일치하는 `primary/secondary/outline/cancel(→secondary)/ghost/danger`로 variant를 고르고 전체 className은 그대로 전달한다. 미일치 기본은 primary. admin-ui와 해석 방식이 다르다(`button.test.tsx`) |
| `icon-button/icon-button.tsx` | `isIconOnly`; 접근 가능한 이름은 `aria-label`, 없으면 `title`. 토큰 `primary/primary-light(→secondary)/secondary/ghost/danger`, 미일치 기본은 secondary |
| `text-area/text-area.tsx` | `className="text-area-component"`를 붙이고 나머지 props(`color` 제외)를 HeroUI `TextArea`에 그대로 넘긴다. `forwardRef`로 `HTMLTextAreaElement`를 노출한다. 아래 `### TextArea` 참조 |

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

### TextArea

- HeroUI `TextArea`(3.2.3, `dist/components/textarea/textarea.js`)는 react-aria-components `TextArea`를 감싼 스타일 래퍼다. 받은 props를 `<textarea>`에 그대로 펼치고 `className`도 textarea 자신에 붙는다. 래퍼 요소가 없으므로 `.<scope> .text-area-component textarea` 같은 자손 선택자는 어떤 요소에도 맞지 않는다. `.<scope> .text-area-component`로 직접 선택한다.
- `maxLength`, `aria-invalid`, `aria-describedby`, `aria-required`는 DOM에 그대로 붙는다. react-aria는 `aria-invalid`가 참이고 `"false"`가 아니면 `data-invalid="true"`를 더한다(`react-aria-components/dist/private/TextArea.mjs`).
- 글자 수·설명·오류 slot은 없다. 라벨·필수 표시·오류 문단·글자 수는 `src/shared/ui/field-group/field-group.tsx`(`FieldGroup`)를 쓴다. 오류 문단 id는 `${htmlFor}-error`, 글자 수 id는 `counter.id`다. 입력의 `aria-describedby`는 호출처가 오류 id, 글자 수 id 순으로 붙인다.
- HeroUI의 `.textarea[data-invalid=true]`(`status-invalid-field`) 규칙은 `@layer components` 안에 있다. layer 밖의 `src/shared/ui/text-area/text-area.css` 1행 `border` 단축 속성이 이를 덮으므로 HeroUI 기본 invalid 테두리는 보이지 않는다.
- 공용 `text-area.css`에는 invalid 테두리가 없다. `5db3f5b` 기준 invalid 테두리는 신고 팝업 범위의 `src/features/citizen-participation/ui/report/citizen-report.css:46`(`.cp-field--report .text-area-component[aria-invalid="true"]`)에만 있다. 다른 화면에 필요하면 화면 범위 CSS에 둔다. 공용 `text-area.css`에 두면 모든 사용처가 바뀐다.
- 포커스 시 `text-area.css`가 `min-height: 8.5rem`과 `box-shadow`를 준다. 화면 범위 invalid 규칙(클래스 3개)은 `:focus`보다 명시도가 높아 포커스 중에도 유지된다.

```tsx
import FieldGroup from "~/shared/ui/field-group/field-group";
import TextArea from "~/shared/ui/text-area/text-area";

<FieldGroup label="상세 사유" htmlFor="report-detail" required {...(error === null ? {} : { error })} counter={{ id: "report-detail-count", current: value.length, max: 500 }}>
  <TextArea
    id="report-detail"
    value={value}
    maxLength={500}
    aria-invalid={error !== null}
    aria-required
    aria-describedby={error === null ? "report-detail-count" : "report-detail-error report-detail-count"}
    onChange={(event) => onChange(event.target.value)}
  />
</FieldGroup>
```

- `tsconfig.app.json`이 `exactOptionalPropertyTypes: true`라 선택 prop은 값이 있을 때만 spread로 넘긴다.
- 폼 제출이 없는 화면에서 네이티브 `required`는 브라우저 검증 문구만 만들므로 쓰지 않고 `aria-required`로 알린다.
- props 전달·`aria-*`·글자 수 텍스트는 `src/shared/ui/field-group/field-group.test.tsx`, `src/pages/citizen-participation/ui/CitizenCommentRoutes.test.tsx`처럼 jsdom으로 확인한다. 테두리 색과 layer 우선순위는 jsdom이 계산하지 않으므로 화면에서 확인한다.

### 적용되지 않는 선택자

`fe49b87` 기준 `.heroui-button`을 대상으로 한 다음 규칙은 적용되지 않는다. 정리는 별도 작업이며 정리 후 이 목록을 갱신한다.

- `src/features/ec/ui/cart/ec-cart.css:33`
- `src/features/ec/ui/checkout/ec-checkout.css:22`
- `src/shared/ui/screen/screen.css:110`, `:148`
- `src/shared/ui/load-error/load-error.css:17`
- `src/features/citizen-participation/ui/parts/citizen-parts.css:105`, `:245`
- `src/features/meeting-reservation/ui/layout/meeting-reservation.css:33`

`5db3f5b` 기준 TextArea 안의 `textarea`를 대상으로 한 다음 규칙은 적용되지 않는다(위 `### TextArea` 참조). 정리는 별도 작업이다.

- `src/features/citizen-participation/ui/parts/citizen-form.css:1`, `:4`, `:7`, `:10`, `:13`, `:16`(`.cp-field--title`·`--background`·`--detail`·`--effect`·`--reference`·`--report` `.text-area-component textarea`)

### 변경·검증

버전 갱신 시 생성 클래스 이름, 크기 utility, layer 순서와 disabled·pending·접근 가능한 이름을 확인한다. 크기 덮어쓰기는 640px·768px 경계 양쪽 화면에서 확인하며 빌드 통과만으로 화면 검증을 완료 처리하지 않는다.
