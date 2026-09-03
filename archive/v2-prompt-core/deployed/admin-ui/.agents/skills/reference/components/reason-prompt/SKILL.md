---
name: component-reason-prompt
description: synthoria-admin-ui의 사유(reason) 입력 모달 — 도메인 무관 콜백형. 강제 종료/모더레이션/숨김 등 "사유를 입력 받고 callback으로 넘기는" 모든 흐름에 사용.
---

# Reason Prompt Component

## 대상

- `src/shared/ui/reason-prompt/reason-prompt.tsx` — 프레젠테이셔널
- `src/shared/ui/reason-prompt/reason-prompt-host.tsx` — 글로벌 호스트
- `src/shared/ui/reason-prompt/reason-prompt.css`
- `src/shared/ui/reason-prompt/index.ts` — barrel export

## 언제 선택하나

- 도메인 액션 진입 시 **사유 텍스트 1건**을 입력 받고 결과를 callback으로 넘겨야 할 때.
- 대표 사용처
  - `proposal-manage/detail`의 `handleForceEndVote`, `handleCompleteExecution`
  - `discuss-posts-management/detail`의 `handlePostModeration`
- 도메인 전용 reason 모달(예: 과거 `ForceEndVoteReasonModal`)을 신규 작성하지 말 것 — 본 컴포넌트로 통합한다.

## 책임 분리

| 파일 | 책임 |
|---|---|
| `reason-prompt.tsx` (`ReasonPrompt`) | 순수 UI. props로 라벨/값/검증/핸들러 수신. `useLanguage`/`usePubSub` **미의존**. |
| `reason-prompt-host.tsx` (`ReasonPromptHost`) | App 루트 1회 마운트. `"open-reason-prompt"` PubSub 구독, 내부 state(open/value/options/pendingCallback) 관리, submit 시 trim된 reason을 callback에 전달. |

App 루트(`src/app.tsx`)에서 이미 `<ReasonPromptHost />`가 한 번 마운트되어 있으므로 도메인은 **추가 마운트 불필요**.

## 사용 패턴

도메인 코드에서는 본 컴포넌트를 직접 import하지 않는다. [useReasonPrompt 훅](../../custom-hooks/use-reason-prompt/SKILL.md)을 통해 publish 한다.

```tsx
const { open: openReasonPrompt } = useReasonPrompt();

openReasonPrompt({
  title: mui["_dao_proposal_forceEndVote_reason_title"],
  placeholder: mui["_dao_proposal_forceEndVote_reason_placeholder"],
  submitLabel: mui["_dao_proposal_forceEndVote_reason_submit"],
  validation: { minLength: 1, maxLength: 500 },
  callback: (reason) => {
    // 도메인 측에서 payload 합성 + API 호출
  },
});
```

## Props 시그니처

### `ReasonPrompt` (프레젠테이셔널)

```ts
interface ReasonPromptProps {
  open: boolean;
  title: string;
  placeholder: string;
  submitLabel: string;
  cancelLabel: string;
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  onClose: () => void;
  validation?: { minLength?: number; maxLength?: number };
}
```

- `minLength` 기본값 1 — `value.trim().length < minLength` 면 submit 버튼 disabled.
- `maxLength` — textarea의 HTML `maxLength` 속성에 직접 바인딩.

### `ReasonPromptHost`

- props 없음. App 루트에 1회 마운트만 한다.

## 스타일/디자인

- 클래스 prefix: `reason-prompt__*` (`reason-prompt-dialog`, `reason-prompt__header`, `reason-prompt__title`, `reason-prompt__close`, `reason-prompt__body`, `reason-prompt__textarea`, `reason-prompt__actions`, `reason-prompt__btn`, `reason-prompt__btn--cancel`, `reason-prompt__btn--submit`).
- 디자인 토큰 사용: `--clr-primary-500`, `--clr-primary-600`. 하드코딩 색상 추가 금지.
- 내부적으로 [CustomModal](../modal/SKILL.md)을 래핑한다 — 배경 클릭/ESC 닫힘 동작은 modal 계약을 그대로 상속.

## 주의/제약

- **전역 단일 호스트**: `ReasonPromptHost`는 App 루트에 한 번만 마운트된다. 동시에 두 곳에서 publish하면 마지막 publish가 이긴다 (PubSub 단일 호스트 패턴 한계).
- **i18n은 호출부 책임**: 호스트/컴포넌트는 `useLanguage` 미의존. 라벨 텍스트는 호출부에서 `mui[...]`로 resolve해 전달한다.
- **취소 시 callback 미호출**: 닫기(✕/cancel/배경 클릭/ESC) 시 `pendingCallback`은 폐기되며 호출되지 않는다. 도메인은 "callback 호출 = 확정"으로 간주해도 된다.
- **submit value는 trim된 값**: callback에 전달되는 reason은 `value.trim()` 결과다. 호스트가 trim을 보장하므로 호출부에서 재 trim 불필요.
- **검증 실패 시 submit 무시**: `trimmed.length < minLength`이면 submit 핸들러는 조용히 return (UI에서 버튼이 disabled).
- **신규 도메인 reason 모달 신설 금지**: 라벨/검증만 다르면 본 컴포넌트로 충분하다. 별도 모달을 만들기 전에 한계 사유를 명확히 적고 검토.

## 관련 자산

- [modal](../modal/SKILL.md) — 내부에서 사용하는 중앙형 모달 베이스
- [usePubSub](../../custom-hooks/use-pub-sub/SKILL.md) — `"open-reason-prompt"` 이벤트 채널
- [useReasonPrompt](../../custom-hooks/use-reason-prompt/SKILL.md) — 도메인 호출용 publish 캡슐화 훅 (도메인은 이걸 사용한다)
