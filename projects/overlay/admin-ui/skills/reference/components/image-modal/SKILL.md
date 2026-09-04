---
name: component-image-modal
description: {{PROJECT_NAME}}의 이미지 미리보기 모달(src/shared/ui/image-modal) 사용 및 수정 가이드. pub-sub로 열리는 전역 이미지 뷰어를 다룰 때 사용.
---

# ImageModal

## 대상

- `src/shared/ui/image-modal/image-modal.tsx`
- `src/shared/ui/image-modal/image-modal.css`

## 계약

**props가 없다.** 다른 오버레이와 달리 소비처가 직접 열지 않고 pub-sub 이벤트로 열리는 전역 싱글턴이다.

- `~/shared/lib/pub-sub`의 `usePubSub`을 구독한다.
- 이벤트 이름은 `open-image`이고 payload는 이미지 URL 문자열이다.
- 열려면 `pubsub.publish("open-image", url)`을 호출한다. 컴포넌트를 직접 렌더링하지 않는다.
- `imageUrl`이 없으면 아무것도 렌더링하지 않는다.
- 닫힘은 백드롭 클릭, 닫기 버튼, `onCancel` 세 경로 모두 `imageUrl`을 `null`로 만든다. 이미지 자체 클릭은 `stopPropagation`으로 닫히지 않는다.

## 사용 기준

- 앱 상단에 한 번만 마운트한다. 화면마다 새로 배치하지 않는다.
- 이미지 미리보기가 필요하면 모달을 만들지 말고 `open-image`를 발행한다.

## 수정 규칙

- 이벤트 이름 `open-image`는 발행 측과의 계약이다. 바꾸면 발행 지점을 모두 찾아 함께 고친다.
- 구독 `useEffect`의 의존성 배열이 비어 있다. 마운트 시 1회 구독이 의도이며 정리 함수로 해제한다. 이 형태를 유지한다.
- props 기반 제어 방식을 추가하면 싱글턴 전제가 깨진다. 필요하면 사용자에게 요청한다.
