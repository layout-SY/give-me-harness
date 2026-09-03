---
name: domain-component-dao-author-badge
description: DAO 도메인 공용 AuthorBadge 사용 가이드. 제안/토론 작성자 표시가 필요한 요구사항에서 사용.
---

# DAO AuthorBadge

## 대상
- `src/pages/dao/components/author/author-badge.tsx`

## 언제 선택하나
- DAO 작성자 정보를 아바타+이름(+ID) 형태로 표시할 때

## 사용 핵심
- `author`, `showId`, `className`/`nameClassName`를 상황에 맞게 전달한다.
- 작성자 누락/익명 상태 처리(`_dao_author_not_found`, `_dao_author_anonymous`)를 유지한다.

## 주의
- 색상 로직(`getAuthorAvatarColorByAuthorId`)은 유지하고, 스타일은 호출부에서 보강한다.
