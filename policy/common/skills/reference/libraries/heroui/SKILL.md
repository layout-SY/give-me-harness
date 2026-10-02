---
name: reference-ui-library-heroui
description: admin-ui의 HeroUI v3 기반 shared/ui 어댑터를 재사용하거나 수정할 때 확인할 버전·스타일·입출력 계약.
---

# HeroUI

이 문서의 구현 근거는 `asan-metaverse-admin-ui`에 한정한다.

## 목적과 확인 범위

버튼·선택·모달 등 기본 UI를 기존 디자인·입출력 계약으로 제공한다. 2026-09-30 관리자 프로젝트 `feature/ec-seller-ui`의 선언은 `@heroui/react ^3.2.3`, package-lock.json과 설치본은 **3.2.4**다. 사용자 프로젝트 또는 다른 major 버전에 그대로 적용하지 않는다.

기존 `src/shared/ui` 어댑터를 사용한다. `src/app/styles/heroui.css`에서 `tailwindcss`와 `@heroui/react/styles`를 import한다. 확인한 프로젝트 구성은 HeroUI Provider를 추가하지 않는다. 다른 버전의 초기화 코드를 혼합하지 않는다.

## 어댑터 계약

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

## 변경·검증

어댑터에서 의존을 관리하고 기존 호출 계약을 유지한다. 버전 갱신 시 lockfile, export, 스타일 순서, 선택·disabled·pending·모달 닫힘·키보드 접근성을 확인한다. 포맷 후 lint·build를 실행하며 빌드 통과만으로 화면·접근성 검증을 완료 처리하지 않는다.
