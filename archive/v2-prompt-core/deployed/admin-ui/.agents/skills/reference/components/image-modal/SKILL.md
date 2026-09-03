---
name: component-image-modal
description: synthoria-admin-ui의 ImageModal 사용 가이드. 이미지 미리보기/확대 보기 요구사항에서 pubsub 기반으로 사용.
---

# Image Modal Component

## 대상

- `src/shared/ui/image-modal/image-modal.tsx`
- 이벤트: `open-image`

## 언제 선택하나

- 썸네일 클릭 후 원본 이미지를 크게 보여줘야 할 때

## 사용 핵심

- 클릭 지점에서 `pubsub.publish("open-image", imageUrl)`을 호출한다.
- 이미지 소스 유효성은 호출부에서 보장한다.

### 사용 예시

<div onClick={() => pubsub.publish('open-imange', imageUrl)}></div>

## 주의

- 확대 뷰 전용이므로 업로드/편집 로직을 포함시키지 않는다.
