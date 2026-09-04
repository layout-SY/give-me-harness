---
name: component-timeline-list
description: {{PROJECT_NAME}}의 이력 목록(src/shared/ui/timeline-list) 사용 및 수정 가이드. 처리 이력 나열과 빈 상태 표시를 다룰 때 사용.
---

# TimelineList

## 대상

- `src/shared/ui/timeline-list/timeline-list.tsx`
- `src/shared/ui/timeline-list/timeline-list.css`

## 계약

시맨틱 `<ol>`로 시간순 항목을 렌더링한다.

| prop | 기본값 | 설명 |
| --- | --- | --- |
| `entries` | 필수 | `{ at: string; title: string; description?: ReactNode }[]` |
| `variant` | `"plain"` | `plain`은 한 줄 나열, `marker`는 좌측 점 + 세로선 |
| `emptyText` | `"이력이 없습니다."` | 빈 상태 문구 |

- `entries`가 비면 목록 대신 `<p class="cp-caption">{emptyText}</p>`만 렌더링한다. `NoResults`를 쓰지 않는다.
- `at`은 컴포넌트가 포맷하지 않는다. **표시할 문자열 그대로 넘긴다.**
- 키는 `at + index` 조합이라 같은 시각이 중복돼도 안전하다.
- `description`은 있을 때만 렌더링되며 `ReactNode`다.

## 사용 기준

- 처리 이력·상태 변경 내역 표시에 사용한다.
- 날짜 포맷은 소비처에서 끝내고 `at`에 넣는다.
- 정렬 순서도 소비처 책임이다. 컴포넌트는 받은 순서대로 렌더링한다.
- 상세 패널 안에서는 `section-card`와 함께 쓴다.

## 수정 규칙

- `<ol>` 시맨틱을 `div`로 바꾸지 않는다. 순서 있는 목록이라는 의미가 사라진다.
- 빈 상태에서 `cp-caption` 전역 클래스를 사용한다. 이름을 바꾸기 전에 전역 CSS를 확인한다.
- `is-{variant}` 클래스는 CSS 계약이다. variant를 추가하면 CSS도 추가한다.
- 컴포넌트 안에서 날짜를 포맷하도록 바꾸면 기존 호출부의 표시가 달라진다.
