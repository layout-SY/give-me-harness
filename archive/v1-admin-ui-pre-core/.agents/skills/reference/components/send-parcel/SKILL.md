---
name: component-send-parcel
description: synthoria-admin-ui의 SendParcelModal 사용 가이드. 유저/아이템 선택 후 발송 액션을 수행하는 요구사항에서 사용.
---

# Send Parcel Modal

## 대상
- 현재 `src/`에 SendParcel 구현 파일이 없다. 이 문서는 legacy reference이며 신규 사용 전 실제 대체 자산을 다시 탐색한다.
- 이벤트: `open-send-parcel-popup`, `close-send-parcel-popup`

## 언제 선택하나
- 발송 대상과 아이템을 조합해 전송하는 운영 액션이 필요할 때

## 사용 핵심
- 이벤트 payload로 초기 `users`/`items`를 전달한다.
- 내부 검증/confirm/success 흐름을 기존 패턴에 맞춘다.

## 주의
- 발송 로직은 운영 영향이 크므로 validation 메시지(i18n)와 confirm 단계를 유지한다.
