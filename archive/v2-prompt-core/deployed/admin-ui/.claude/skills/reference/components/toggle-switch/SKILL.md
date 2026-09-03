---
name: component-toggle-switch
description: synthoria-admin-ui의 공용 ToggleSwitch 사용 가이드. ON/OFF 상태 전환 UI 요구사항에서 사용.
---

# Toggle Switch Component

## 대상
- `src/components/toggle-switch/toggle-switch.tsx`

## 언제 선택하나
- boolean 상태를 즉시 전환해야 하는 경우

## 사용 핵심
- `checked`/`onChange` 또는 프로젝트 기존 계약에 맞춰 상태를 연결한다.
- 저장형 화면이면 토글 변경 후 confirm/save 플로우를 분리한다.

## 주의
- 상태 라벨은 별도 텍스트(`ACTIVE/INACTIVE`)와 함께 제공하는 것을 권장
