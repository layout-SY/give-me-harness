---
name: component-ratio-bar
description: {{PROJECT_NAME}}의 비율 막대(src/shared/ui/ratio-bar) 사용 및 수정 가이드. 백분율 세그먼트와 범례 표시를 다룰 때 사용.
---

# RatioBar

## 대상

- `src/shared/ui/ratio-bar/ratio-bar.tsx`
- `src/shared/ui/ratio-bar/ratio-bar.css`

## 계약

| prop | 설명 |
| --- | --- |
| `segments` | `{ label: string; percent: number; tone: RatioSegmentTone }[]` |
| `caption` | 있을 때만 렌더링된다 |

`RatioSegmentTone`은 `primary | neutral | danger` 세 가지다. `StatusBadge`나 `KpiCard`의 tone 타입과 값 집합이 다르다.

동작은 다음과 같다.

- `percent`는 **0~100 백분율**이며 세그먼트 `width`에 그대로 들어간다. 합이 100이 아니면 막대가 비거나 넘친다. **정규화는 소비처 책임이다.**
- 막대 세그먼트는 `aria-hidden="true"`다. 의미 전달은 아래 범례 목록이 담당한다.
- 범례에는 `label`과 `percent`가 함께 표시된다.
- 키가 `label`이다. **같은 라벨이 둘 이상이면 React 키가 충돌한다.**
- `caption`의 클래스는 `cp-caption`이다. 다른 요소의 `ratio-bar__*` 규칙과 접두가 다르다.

## 사용 기준

- 찬반 비율, 처리 상태 분포처럼 합이 100인 지표에 사용한다.
- 백분율 계산과 반올림 보정은 넘기기 전에 끝낸다.
- 라벨은 세그먼트마다 고유해야 한다.

## 수정 규칙

- 세그먼트의 `aria-hidden`과 범례 구조는 접근성 계약이다. 범례를 제거하면 값이 보조기기에 전달되지 않는다.
- `is-{tone}` 클래스는 CSS 계약이다. tone을 추가하면 CSS도 추가한다.
- 컴포넌트 안에서 백분율을 정규화하도록 바꾸면 기존 호출부의 표시 값이 달라진다. 사용자 승인을 받는다.
- `cp-caption` 클래스는 이 컴포넌트 밖의 전역 규칙을 참조한다. 이름을 바꾸기 전에 전역 CSS를 확인한다.
