---
name: component-image-slot-item
description: synthoria-admin-ui의 ImageSlotItem 사용 가이드. 다중 이미지 슬롯 UI(미리보기/삭제/추가)를 구성할 때 사용.
---

# Image Slot Item

## 대상

- `src/features/image-manager/ui/components/ImageSlotItem.tsx`

## 언제 선택하나

- 여러 장 이미지 목록을 슬롯 형태로 보여줄 때

## 사용 핵심

- 이미지 데이터 배열과 삭제/추가 핸들러를 상위에서 관리한다.
- 클릭 시 미리보기 이벤트(`open-image`) 연계를 고려한다.

## 주의

- 레이아웃/정렬 디테일은 페이지 CSS로 조정하는 것을 허용한다.

## 리팩토링 내용

- 현재 onPreviewImage를 props로 받고 있는데 image-modal 컴포넌트를 사용하는 방법밖에 없기 때문에 부모 컴포넌트에서의 사용처가 고정된다. 따라서 해당 컴포넌트 내부에서 고정적으로 사용하도록 변경해도 된다.
