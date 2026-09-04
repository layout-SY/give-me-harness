---
name: component-search-state-bar
description: {{PROJECT_NAME}}의 목록 상단 검색·상태 탭 바(src/shared/ui/search-state-bar) 사용 및 수정 가이드. 상태 탭, 검색 조건, 키워드 검색과 등록 버튼을 다룰 때 사용.
---

# SearchStateBar

## 대상

- `src/shared/ui/search-state-bar/searchStateBar.tsx`
- `src/shared/ui/search-state-bar/searchStateBar.css`
- `src/shared/ui/search-state-bar/TableSortFilter.tsx`
- `src/shared/ui/search-state-bar/TableSortFilter.css`

이 디렉터리만 camelCase 파일명을 쓴다. 다른 `src/shared/ui` 디렉터리는 kebab-case다.

## 계약

`button`, `icon-button`, `text-input`, `dropdown`을 조합한 목록 상단 바다. **명명 내보내기 `SearchStateBar`이며 제네릭 `TValue`를 받는다.**

| prop | 설명 |
| --- | --- |
| `tabs` | `{ label, value, count?, active }[]`. `active`를 소비처가 계산한다 |
| `placeholder` | 키워드 입력 안내 문구 |
| `keyword`, `onChangeKeyword`, `onClearKeyword` | 제어 입력 |
| `searchByItems`, `searchByIndex`, `onSearchByChange` | 검색 조건 드롭다운. 항목이 있을 때만 렌더링된다 |
| `onSubmit` | `form`의 submit 핸들러 |
| `onTabChange` | `(value: TValue) => void` |
| `onCreateClick` | 전달했을 때만 등록 버튼이 렌더링된다 |
| `title` | 인터페이스에 있으나 **구현에서 사용하지 않는다** |

동작에서 알아야 할 점은 다음과 같다.

- 전체가 `<form>`이고 검색 버튼은 `type="submit"`이다. 검색 실행은 `onSubmit`으로 받는다. 버튼 클릭 콜백이 아니다.
- 탭 활성 상태는 컴포넌트가 관리하지 않는다. `tabs[].active`를 소비처가 넣는다.
- 검색 조건 드롭다운은 `dropdown`의 index 계약을 그대로 쓴다. 미선택은 `-1`이다.
- 루트 클래스가 `proposal-search-state-bar`다. 특정 화면 이름이 남아 있지만 공용 컴포넌트다.

## 사용 기준

- 목록 화면 상단은 이 컴포넌트를 재사용한다. 탭·검색·등록을 따로 만들지 않는다.
- 검색 실행은 `onSubmit`에 연결한다. Enter 키 검색이 함께 동작한다.
- 등록 버튼이 필요 없으면 `onCreateClick`을 전달하지 않는다.

## 수정 규칙

- `proposal-` 접두 클래스는 CSS 계약이다. 이름을 정리하려면 CSS와 함께 바꾼다.
- `title` prop은 미사용이다. 제거하려면 전달 중인 호출부를 먼저 확인한다.
- 검색을 버튼 `onClick`으로 바꾸지 않는다. form submit 계약이 깨진다.
