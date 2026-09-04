---
name: component-author-badge
description: {{PROJECT_NAME}}의 작성자 배지(src/shared/ui/author) 사용 및 수정 가이드. 아바타 색상 결정과 결측 계정 표시를 다룰 때 사용.
---

# AuthorBadge

## 대상

- `src/shared/ui/author/author-badge.tsx`
- `src/shared/ui/author/author-badge.css`
- `src/shared/ui/author/types`
- `src/shared/lib/utils/selectColor.ts` (`getAuthorAvatarColorByAuthorId`)

**명명 내보내기 `AuthorBadge`다.**

## 계약

`@heroui/react`의 `Chip`을 사용한다.

| prop | 기본값 | 설명 |
| --- | --- | --- |
| `author` | 없음 | `AuthorCellType["author"]` |
| `showId` | `false` | `true`면 `이름 (#id)` 형태로 표시한다 |
| `className` | 없음 | `author-badge`에 이어 붙는다 |
| `nameClassName` | 없음 | 이름 요소에 이어 붙는다 |

입력 상태별 분기가 네 갈래다.

| 조건 | 결과 |
| --- | --- |
| `author?.name`이 없음 | `<span>이름 없음</span>` |
| `name`은 있고 `id`가 없음 | `<p>미존재 계정</p>` |
| `id > 0` | 아바타 + 이름 `Chip` |
| `id <= 0` | `<span>이름 없음</span>` |

`id`가 없을 때만 `<p>`이고 나머지 결측은 `<span>`이다. 아바타 배경·글자색은 `getAuthorAvatarColorByAuthorId(author.id)`가 결정하므로 **같은 사용자는 항상 같은 색**이다. 이니셜은 이름 첫 글자 대문자다.

## 사용 기준

- 작성자·처리자 표시는 이 배지를 재사용한다. 표에서는 셀에 넣는다.
- 결측 처리를 소비처에서 다시 하지 않는다. 이 컴포넌트가 네 갈래를 모두 처리한다.
- 식별자를 함께 보여야 하는 관리 화면에서만 `showId`를 켠다.

## 수정 규칙

- 색 결정을 `getAuthorAvatarColorByAuthorId`가 아닌 방식으로 바꾸면 사용자별 색 일관성이 깨진다.
- `id <= 0`과 `id` 없음을 다르게 표시하는 현재 동작은 의도된 구분이다. 합치기 전에 데이터 의미를 확인한다.
- 결측 분기에서 `<p>`와 `<span>`이 섞여 있다. 통일하려면 표 셀 레이아웃에 미치는 영향을 확인한다.
