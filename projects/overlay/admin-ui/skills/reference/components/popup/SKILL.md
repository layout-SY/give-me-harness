---
name: component-popup
description: {{PROJECT_NAME}}의 공용 Popup(src/shared/ui/popup) 사용 및 수정 가이드. 네이티브 dialog 기반 열기·닫기 애니메이션을 다룰 때 사용.
---

# Popup

## 대상

- `src/shared/ui/popup/popup.tsx`
- `src/shared/ui/popup/popup.css`
- `src/shared/ui/popup/popup.responsive.css`
- `src/shared/ui/popup/index.ts`

## 계약

HeroUI를 쓰지 않고 **네이티브 `<dialog>`를 직접 제어하는 유일한 오버레이 컴포넌트**다.

| prop | 설명 |
| --- | --- |
| `open` | `true`면 `showModal()`, `false`면 닫힘 애니메이션 후 `close()` |
| `close` | ESC 또는 백드롭 클릭 시 호출된다 |
| `children` | dialog 내용이다 |

나머지 `React.HTMLAttributes<HTMLDialogElement>` 속성은 그대로 전달된다.

동작의 핵심은 다음과 같다.

- 클래스로 상태를 표현한다. 열림은 `active`, 닫힘 진행은 `closing`이며 `animationend`에서 실제 `close()`가 실행된다. **닫힘이 즉시가 아니다.**
- 고정 클래스 `custom-popup`에 소비처 `className`이 이어 붙는다.
- ESC는 `keyup`에서 직접 처리하고 `onCancel`은 `preventDefault`로 막는다. 네이티브 즉시 닫힘을 막아 애니메이션을 보장하기 위함이다.
- 백드롭 판정은 `e.target === dialog` 비교다. 내용 영역 클릭은 닫히지 않는다.

## 사용 기준

- 열기·닫기 애니메이션이 필요한 오버레이에 사용한다. 애니메이션이 불필요하면 `modal`을 사용한다.
- 닫힘 완료 시점에 의존하는 후처리는 `close` 콜백이 아니라 소비처 상태 전이로 처리한다.

## 수정 규칙

- `active`/`closing` 클래스 이름은 CSS 애니메이션의 계약이다. 바꾸지 않는다.
- `onCancel`의 `preventDefault`를 제거하지 않는다. 제거하면 닫힘 애니메이션이 사라진다.
- `animationend` 리스너 정리 로직을 단순화하지 않는다. 중복 등록 방지가 목적이다.
- HeroUI `Modal`로 대체하는 변경은 애니메이션 계약이 달라지므로 사용자 승인을 받는다.
