---
name: component-text-area
description: synthoria-admin-ui의 공용 TextArea 사용 가이드. 긴 문자열 입력(사유/설명/메모) 요구사항에서 사용.
---

# TextArea Component

## 대상
- `src/components/text-area/text-area.tsx`

## 언제 선택하나
- 다중 줄 텍스트 입력이 필요한 경우

## 사용 핵심
- `value`, `onChange`, `placeholder`, `disabled`를 명시적으로 연결한다.
- 페이지 validation은 별도 메시지 영역으로 처리한다.

## 주의
- 높이/리사이즈 정책은 페이지 스타일로 보강 가능
- 사용자 문구는 한글로 직접 작성
