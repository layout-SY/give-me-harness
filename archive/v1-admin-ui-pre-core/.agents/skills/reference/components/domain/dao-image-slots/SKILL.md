---
name: domain-component-dao-image-slots
description: DAO 제안용 ImageSlots 컴포넌트 사용 가이드. 제안 이미지 목록 조회/편집(추가/삭제/미리보기) 요구사항에서 사용.
---

# DAO ImageSlots

## 대상
- `src/pages/dao/proposal-manage/detail/components/sections/imagesSection.tsx`
- `src/pages/dao/proposal-manage/hooks/useDaoProposalImageBridge.ts`
- 관련 도메인 자산: `src/features/image-manager/ui/ImageManager.tsx`

## 언제 선택하나
- DAO proposal 이미지를 편집 모드와 조회 모드로 나눠 렌더해야 할 때

## 사용 핵심
- `variant`를 `urls` 또는 `dtos`로 선택한다.
- `onPreviewImage`, `onAddClick`, `onChange`를 반드시 연결한다.
- `isEditing`/`disabled`/`maxImages`로 동작을 제어한다.

## 주의
- 내부는 `ImageSlotItem` + DAO 이미지 유틸에 의존하므로 계약을 유지한다.
- 슬롯 레이아웃 디테일은 페이지 CSS에서 보강 가능하다.
