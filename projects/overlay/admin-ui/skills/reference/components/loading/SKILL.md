---
name: component-loading
description: {{PROJECT_NAME}}의 공용 Loading 인디케이터(src/shared/ui/loading) 사용 및 수정 가이드. 로딩 표시와 오버레이 배치를 다룰 때 사용.
---

# Loading

## 대상

- `src/shared/ui/loading/loading.tsx`
- `src/shared/ui/loading/loading.css`
- `src/shared/ui/loading/loading.custom.css`
- `src/shared/ui/loading/index.ts`

## 계약

`@heroui/react`의 `Spinner`를 `size="lg"`, `color="accent"`로 고정해 감싼다.

| prop | 기본값 | 설명 |
| --- | --- | --- |
| `isOverlay` | `false` | `true`면 `is-overlay` 클래스를 추가해 부모 영역 위에 겹쳐 표시한다 |

`isOverlay`를 사용하려면 **부모에 `position` 지정이 필요하다.** 이 전제가 없으면 화면 전체를 기준으로 배치된다.

## 사용 기준

- 버튼 내부 로딩에는 사용하지 않는다. `button`의 `isLoading`을 사용한다.
- 영역 단위 로딩에 `isOverlay`를 사용하고, 그 영역에 `position: relative`를 부여한다.
- 크기와 색은 고정이다. 화면마다 다른 스피너를 만들지 않는다.

## 수정 규칙

- `loading.css`와 `loading.custom.css` 두 파일이 함께 적용된다. 한쪽만 보고 판단하지 않는다.
- `size`와 `color` 고정값을 prop으로 여는 변경은 사용자 승인을 받는다.
- `index.ts` 배럴을 통해 import된다. 내부 파일 경로를 직접 참조하도록 바꾸지 않는다.
