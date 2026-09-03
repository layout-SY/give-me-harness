---
name: component-fade-in
description: synthoria-admin-ui의 FadeIn 컴포넌트 사용 가이드. 점진적 등장 애니메이션이 필요한 요구사항에서 사용.
---

# Fade In Component

## 대상

- `src/components/fade-in/fade-in.tsx`

## 언제 선택하나

- 요소 등장 시 시각적 완화가 필요한 경우
- 대시보드에서 시각적 효과가 필요한 경우

## 사용 핵심

- 콘텐츠를 `FadeIn`으로 감싸고 타이밍/지연은 기존 props 계약 범위에서 조정한다.

## 주의

- 과도한 애니메이션 중첩을 피하고 핵심 UX 요소에만 제한적으로 사용한다.
