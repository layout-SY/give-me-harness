---
name: component-image-upload
description: synthoria-admin-ui의 ImageUploadPopup 사용 가이드. 이미지 파일 선택 팝업을 열고 callback으로 업로드 로직을 위임해야 하는 요구사항에서 사용.
---

# Image Upload Popup

## 대상

- `src/components/image-upload/image-upload.tsx`
- 이벤트: `open-image-upload-popup`, `close-image-upload-popup`

## 언제 선택하나

- 이미지 파일 선택 UI가 필요하고 실제 업로드 API는 호출부에서 처리할 때

## 사용 핵심

- `open-image-upload-popup`에 `instructions`, `callback({ file })`를 전달한다.
- 파일 검증/업로드/성공 처리(close)는 callback 쪽에서 수행한다.

## 주의

- 이 컴포넌트 자체는 업로드 API를 호출하지 않는다.
- 전반적인 디자인 수정을 허용한다.
