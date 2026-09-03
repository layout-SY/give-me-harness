---
name: component-select-users
description: synthoria-admin-ui의 SelectUsersPopup 사용 가이드. 사용자 선택 팝업이 필요한 요구사항에서 pubsub 기반으로 사용.
---

# Select Users Popup

## 대상

- `src/features/select-users/ui/select-users.tsx`
- pbusub 이벤트: `open-select-users-popup`

## 언제 선택하나

- 여러 유저를 선택해 상위 폼/모달에 반영해야 할 때

## 사용 핵심

- 이벤트 payload의 `userIds`, `callback` 계약을 지킨다.
- 선택 결과는 callback으로 상위 state에 반영한다.

## 주의

- 선택 대상 필터/검색 로직은 팝업 내부 기존 패턴을 우선 재사용한다.
