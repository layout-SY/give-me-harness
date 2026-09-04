---
name: component-dialog
description: {{PROJECT_NAME}}의 전역 Dialog와 useDialog 훅(src/shared/ui/dialog) 사용 및 수정 가이드. alert·confirm 호출, Promise 기반 확인과 store 계약을 다룰 때 사용.
---

# Dialog / useDialog

## 대상

- `src/shared/ui/dialog/index.ts`
- `src/shared/ui/dialog/hook.ts`
- `src/shared/ui/dialog/dialog.tsx`
- `src/shared/ui/dialog/dialog.store.ts`
- `src/shared/ui/dialog/dialog.css`
- `src/shared/ui/dialog/dialog.custom.css`

배럴 `~/shared/ui/dialog`에서 `useDialog`와 `Dialog`를 명명 내보내기로 가져온다.

## 계약

호출부는 훅만 쓴다.

```ts
const Dialog = useDialog();

Dialog.alert({ content: <p>메시지</p>, header?, callback? });
const confirmed: boolean = await Dialog.confirm({ content: <p>진행할까요?</p>, header? });
```

| API | 반환 | 설명 |
| --- | --- | --- |
| `alert(payload)` | `void` | `header` 기본값 `"Alert"`. 닫힐 때 `callback`이 있으면 호출된다 |
| `confirm(payload)` | `Promise<boolean>` | `header` 기본값 `"Confirm"`. 확인 `true`, 취소·ESC `false` |

`content`는 `ReactNode`다. 문자열이 아니라 엘리먼트를 넘긴다.

구조는 zustand store를 매개로 한 전역 싱글턴이다.

- `useDialog`는 store에 payload와 타입을 넣고 열기만 한다.
- `Dialog` 컴포넌트가 실제 `<dialog>`를 렌더링한다. **앱에 한 번 마운트되어 있어야 한다.**
- `confirm`은 `confirmResolve`에 resolver를 저장해 두고 버튼·ESC에서 `resolve`한다. 그래서 `await`이 가능하다.
- ESC는 `confirm`을 `false`로 종료한다. `onCancel`은 `preventDefault`로 막고 닫힘 애니메이션을 태운다.
- 닫힘은 즉시가 아니다. `CustomDialogSlideOutToBottom` 애니메이션이 끝난 뒤 `close()`가 실행된다.
- 닫힌 뒤 payload는 비워진다.

## 사용 기준

- 알림·확인 UI를 직접 만들지 않는다. 이 훅을 사용한다.
- 삭제·반려처럼 되돌릴 수 없는 액션은 `await Dialog.confirm(...)` 결과를 분기한다.
- `alert` 이후 이동·갱신이 필요하면 `callback`에 넣는다. `alert` 호출 직후 코드는 사용자가 닫기 전에 실행된다.
- 사유 입력이 필요한 확인은 이 다이얼로그가 아니라 `reason-prompt`를 사용한다.
- `useApi`가 실패 시 내부적으로 `Dialog.alert`를 사용한다. `silent: false`로 호출하면 이 다이얼로그가 뜬다.

## 수정 규칙

- `Dialog` 컴포넌트 마운트를 제거하면 모든 `alert`·`confirm`이 조용히 사라진다. `useApi`의 오류 표시도 함께 죽는다.
- `confirmResolve`를 정리하지 않으면 이전 확인이 미해결로 남는다. `startClosing`의 resolve → `setConfirmResolve(null)` 순서를 유지한다.
- `setConfirmResolve`가 updater 형태(`() => fn`)를 받는 이유는 함수를 값으로 저장하기 위함이다. 단순화하지 않는다.
- 애니메이션 이름 `CustomDialogSlideOutToBottom`은 CSS와의 계약이다. 한쪽만 바꾸면 다이얼로그가 닫히지 않는다.
- `onCancel`의 `preventDefault`를 제거하지 않는다.
