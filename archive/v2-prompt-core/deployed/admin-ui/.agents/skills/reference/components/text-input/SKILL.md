---
name: component-text-input
description: synthoria-admin-ui의 공용 TextInput 사용 가이드. 클리어 버튼, 비밀번호 표시 토글, 입력 일관성을 유지해야 하는 요구사항에서 사용.
---

# TextInput Component

## 대상
- `src/shared/ui/text-input/text-input.tsx`

## 언제 선택하나
- 단일 텍스트 입력이 필요할 때 기본 선택

## 사용 핵심
- 클리어 필요: `enableClear`, `onClear`
- 비밀번호 표시 토글: `enableShow`
- 표준 input props(`value`, `onChange`, `disabled`)를 그대로 전달

## 주의
- 페이지별 validation 스타일은 래퍼 class로 보강
- placeholder/라벨/에러 메시지는 `mui` 키 사용
