---
name: component-side-modal
description: synthoria-admin-ui의 SideModal 사용 가이드. 상세 조회/수정 패널형 모달 요구사항에서 사용.
---

# Side Modal Component

## 대상
- `src/shared/ui/side-modal/side-modal.tsx`

## 언제 선택하나
- 우측 슬라이드형 상세 편집/조회 UX가 필요한 경우

## 사용 핵심
- `open`, `close` 상태를 모달 상태 머신(`READ/UPDATE` 등)과 함께 관리한다.
- 내부에서 `Loading`, `dirty-check`, 저장/취소 액션 버튼 패턴을 맞춘다.

## 주의
- 리사이즈 핸들/애니메이션이 내장되어 있으므로 구조를 크게 바꾸지 않는다.
