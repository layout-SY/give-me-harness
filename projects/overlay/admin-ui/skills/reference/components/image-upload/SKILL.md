---
name: component-image-upload
description: {{PROJECT_NAME}}의 이미지 업로드 팝업(src/shared/ui/image-upload) 사용 및 수정 가이드. pub-sub로 열리는 전역 업로드 팝업과 파일 형식 제한을 다룰 때 사용.
---

# ImageUploadPopup

## 대상

- `src/shared/ui/image-upload/image-upload.tsx`
- `src/shared/ui/image-upload/image-upload.css`

## 계약

**props가 없다.** `image-modal`과 같이 pub-sub으로 열리는 전역 싱글턴이며 내부적으로 `popup`을 사용한다.

- 열기: `pubsub.publish("open-image-upload-popup", { instructions, callback })`
- 닫기: `pubsub.publish("close-image-upload-popup")`
- payload 타입은 `~/shared/lib/pub-sub/events`의 `PubSubEvents["open-image-upload-popup"]`다.
- `callback: (file: File) => void`가 선택된 파일을 받는다. `instructions: string[]`는 팝업에 안내 목록으로 표시된다.

파일 처리 규칙은 다음과 같다.

- 허용 형식은 `image/jpg`, `image/jpeg`, `image/png`뿐이다. 그 외에는 `Dialog.alert`로 안내하고 입력을 비운다.
- 첫 번째 파일만 사용한다. 다중 선택을 지원하지 않는다.
- 처리 후 항상 `e.target.value = ""`로 초기화한다. 같은 파일 재선택이 가능하도록 하기 위함이다.

`callback`을 상태에 넣을 때 `setCallback(() => callback)` 형태를 쓴다. 함수를 상태 업데이터로 오해하지 않게 하려는 의도다.

## 사용 기준

- 앱 상단에 한 번만 마운트한다.
- 업로드 UI를 새로 만들지 말고 `open-image-upload-popup`을 발행한다.
- 업로드 이후 처리(전송, 미리보기 갱신)는 `callback` 안에서 소비처가 수행한다.

## 수정 규칙

- 두 이벤트 이름은 발행 측과의 계약이다. 바꾸면 발행 지점을 모두 함께 고친다.
- 허용 MIME 목록을 넓히는 변경은 서버 검증과 함께 결정한다. 임의로 확장하지 않는다.
- `setCallback(() => callback)` 형태를 단순화하지 않는다.
