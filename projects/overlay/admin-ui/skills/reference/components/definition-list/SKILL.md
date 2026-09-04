---
name: component-definition-list
description: {{PROJECT_NAME}}의 정의 목록(src/shared/ui/definition-list) 사용 및 수정 가이드. 상세 패널의 라벨-값 배치와 layout 선택을 다룰 때 사용.
---

# DefinitionList

## 대상

- `src/shared/ui/definition-list/definition-list.tsx`
- `src/shared/ui/definition-list/definition-list.css`

## 계약

시맨틱 `<dl>`로 라벨-값 쌍을 렌더링한다.

| prop | 기본값 | 설명 |
| --- | --- | --- |
| `items` | 필수 | `{ label: string; value: ReactNode }[]` |
| `layout` | `"inline"` | `inline \| rows \| stack \| grid` |
| `columns` | `2` | `1 \| 2 \| 3 \| 4`. `grid`·`rows`에서만 쓰인다 |
| `labelWidth` | `"6rem"` | 라벨 폭. `grid`·`rows`에서만 쓰인다 |

layout 의미는 다음과 같다.

- `inline`: 한 줄 나열. 기본 정보 요약용
- `rows`: 한 행에 "라벨 값". **상세 패널 기본형**
- `stack`: 라벨 위, 값 아래
- `grid`: 라벨 폭 고정 n열 정렬

`grid`와 `rows`일 때만 CSS 변수 `--definition-columns`, `--definition-label-w`를 인라인 style로 내린다. 다른 layout에서 `columns`·`labelWidth`를 넘겨도 반영되지 않는다.

## 사용 기준

- 상세 패널의 속성 나열은 이 컴포넌트를 사용한다. 표나 div 조합으로 만들지 않는다.
- 상세 패널 기본형은 `layout="rows"`다.
- `value`는 `ReactNode`이므로 `StatusBadge`나 링크를 그대로 넣을 수 있다.
- 항목 키는 `label + index` 조합이다. 같은 라벨이 반복돼도 안전하다.

## 수정 규칙

- `<dl>/<dt>/<dd>` 시맨틱 구조를 `div`로 바꾸지 않는다.
- `is-{layout}` 클래스와 두 CSS 변수는 CSS 계약이다. layout을 추가하면 CSS도 함께 추가한다.
- `columns`·`labelWidth`가 일부 layout에서만 유효한 현재 동작을 바꾸려면 CSS를 함께 확인한다.
