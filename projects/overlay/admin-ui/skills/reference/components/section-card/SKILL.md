---
name: component-section-card
description: {{PROJECT_NAME}}의 섹션 카드(src/shared/ui/section-card) 사용 및 수정 가이드. 제목·설명·액션이 있는 영역 래퍼를 다룰 때 사용.
---

# SectionCard

## 대상

- `src/shared/ui/section-card/section-card.tsx`
- `src/shared/ui/section-card/section-card.css`

## 계약

`<section>` 기반의 영역 래퍼다.

| prop | 설명 |
| --- | --- |
| `title` | `ReactNode`. 있으면 `<h3>`로 렌더링된다 |
| `description` | 문자열. **`title` 또는 `actions`가 있을 때만 표시된다** |
| `actions` | 헤더 우측 액션 영역 |
| `className` | `section-card`에 이어 붙는다 |
| `bodyClassName` | `section-card__body`에 이어 붙는다 |
| `children` | 본문 |

헤더는 `title`이나 `actions` 중 하나라도 있을 때만 렌더링된다. **`description`만 넘기면 아무것도 보이지 않는다.**

## 사용 기준

- 상세 화면의 구획을 나눌 때 사용한다. 카드 테두리를 직접 그리지 않는다.
- 구획 제목은 `title`로 넘긴다. 본문에 별도 제목을 두지 않는다.
- 헤더 버튼은 `actions`에 배치한다.
- 본문 레이아웃 조정이 필요하면 `bodyClassName`을 사용한다. `className`은 카드 전체용이다.

## 수정 규칙

- `description`이 헤더 렌더링 조건에 포함되지 않는 현재 동작은 의도와 다를 수 있다. 고치려면 `description`만 넘기는 호출부가 있는지 먼저 확인한다.
- `h3` 레벨을 바꾸면 문서 개요 구조가 흔들린다.
- `section-card__*` 클래스는 CSS 계약이다.
