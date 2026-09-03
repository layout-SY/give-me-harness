---
name: component-popup
description: synthoria-admin-ui의 Popup 컴포넌트 사용 가이드. 가벼운 선택/확인 팝업 요구사항에서 사용.
---

# Popup Component

## 대상
- `src/components/popup/popup.tsx`

## 언제 선택하나
- 중앙형 경량 팝업이나 선택 목록 팝업이 필요한 경우

## 사용 핵심
- `open`, `close`와 함께 내부 폼/선택 상태를 분리해서 관리한다.
- pubsub 기반 열기/닫기 이벤트를 쓰는 기존 패턴을 우선 따른다.

## 주의
- 상세 편집 폼은 `side-modal`, 일반 대형 모달은 `modal`이 더 적합할 수 있다.
