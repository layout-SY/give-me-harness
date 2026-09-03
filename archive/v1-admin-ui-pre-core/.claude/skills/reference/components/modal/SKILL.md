---
name: component-modal
description: synthoria-admin-ui의 중앙형 CustomModal 사용 가이드. 일반 팝업/업로더/설정 모달 요구사항에서 사용.
---

# Modal Component

## 대상

- `src/components/modal/modal.tsx`

## 언제 선택하나

- 화면 중앙에 뜨는 기본 모달이 필요한 경우

## 사용 핵심

- `open`, `close`, `children` 계약을 준수한다.
- 배경 클릭/ESC 닫힘 동작을 전제로 흐름을 설계한다.

## 주의

- 복잡한 폼 / 상세 편집은 `side-modal` 사용을 우선 검토한다.
