---
name: component-fade-in
description: {{PROJECT_NAME}}의 FadeIn 래퍼(src/shared/ui/fade-in) 사용 및 수정 가이드. 지연 표시와 페이드 전환을 다룰 때 사용.
---

# FadeInComponent

## 대상

- `src/shared/ui/fade-in/fade-in.tsx`
- `src/shared/ui/fade-in/fade-in.css`

## 계약

HeroUI를 쓰지 않고 인라인 스타일 전환으로 구현한 래퍼다.

| prop | 기본값 | 설명 |
| --- | --- | --- |
| `delay` | `0` | 마운트 후 렌더링까지 지연(ms) |
| `duration` | `150` | 전환 시간(ms) |
| `children` | 필수 | 전환 대상 |

나머지 `React.HTMLAttributes<HTMLDivElement>` 속성은 그대로 전달되고, `style`은 계산된 페이드 스타일 뒤에 병합되어 덮어쓸 수 있다.

동작은 다음과 같다.

- `delay` 경과 전에는 **아무것도 렌더링하지 않는다**(`null`). 레이아웃 자리도 차지하지 않는다.
- 이중 `requestAnimationFrame` 후 `show`를 켠다. 첫 페인트에서 전환이 시작되도록 보장하기 위함이다.
- 전환은 `opacity 0 → 1`과 `translateY(10px) → 0`이다.
- 언마운트 시 타이머와 두 애니메이션 프레임을 모두 정리한다.

## 사용 기준

- 목록 항목을 순차 노출할 때 `delay`를 인덱스로 계산해 전달한다.
- `delay` 동안 자리 비움이 문제라면 이 컴포넌트를 쓰지 않고 CSS 전환을 직접 적용한다.

## 수정 규칙

- 이중 `requestAnimationFrame`을 한 번으로 줄이지 않는다. 초기 전환이 건너뛰어진다.
- `delay` 이전 `null` 반환은 의도된 계약이다. 빈 div로 바꾸지 않는다.
- 정리 함수에서 타이머와 프레임을 모두 해제하는 형태를 유지한다.
