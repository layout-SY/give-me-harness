---
name: domain-component-dao-category-badge
description: DAO 도메인 공용 CategoryBadge 사용 가이드. 제안 카테고리(POLICY/BUSINESS/ECONOMY/ETC) 표시에 사용.
---

# DAO CategoryBadge

## 대상
- `src/pages/dao/components/category/category-badge.tsx`

## 언제 선택하나
- DAO proposal category를 색상 배지로 표기할 때

## 사용 핵심
- `category: DaoProposalCategory`를 전달한다.
- 내부 라벨 키 매핑(`_dao_proposal_category_*`)을 유지한다.

## 주의
- 카테고리별 색상 정책 변경은 DAO 화면 전체 영향이 있으므로 신중히 수정한다.
