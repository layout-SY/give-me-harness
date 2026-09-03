---
name: hook-use-reason-prompt
description: synthoria-admin-ui의 useReasonPrompt 훅. ReasonPromptHost를 호출해 사유 입력 모달을 띄우는 publish 캡슐화. 강제 종료/모더레이션/숨김 등 "사유 + callback" 흐름에 사용.
---

# useReasonPrompt Hook (synthoria-admin-ui)

## 대상

- `src/hooks/use-reason-prompt/index.ts`

## 언제 이 스킬을 사용하나요?

- 도메인 액션 진입 직전에 **사유 텍스트 1건**을 받아서 callback으로 처리해야 할 때.
- 사유 입력 UI를 도메인별로 신규 작성하지 않고 공용 [ReasonPrompt](../../components/reason-prompt/SKILL.md) 호스트를 재사용한다.
- `pubsub.publish("open-reason-prompt", ...)`를 직접 호출하지 말 것 — 본 훅으로 캡슐화되어 있다.

## 시그니처

```ts
interface OpenReasonPromptOptions {
  title: string;
  placeholder: string;
  submitLabel: string;
  cancelLabel?: string;
  validation?: { minLength?: number; maxLength?: number };
  callback: (reason: string) => void;
}

const { open } = useReasonPrompt();
```

- 반환값은 `{ open }` 단일. `open`은 안정 참조(`useCallback`).

## 동작

1. `cancelLabel`이 미전달이면 훅 내부에서 기본값 `"취소"`로 publish.
   - 호스트(`ReasonPromptHost`)는 문자열을 모르는 원칙을 유지하기 위함이다.
2. `pubsub.publish("open-reason-prompt", { title, placeholder, submitLabel, cancelLabel, validation, callback })` 호출.
3. 호스트가 모달을 열고 사용자 입력을 받는다.
4. submit 시 호스트는 `value.trim()`을 검증(`minLength` 충족) 후 `callback(trimmedReason)` 호출.
5. 취소(닫기/배경/ESC) 시 callback 미호출.

## 검증 규칙

- `validation.minLength` — default `1`. 호스트의 submit 핸들러와 ReasonPrompt 컴포넌트 둘 다 동일 정책으로 `value.trim().length < minLength`면 submit 비활성화/무시.
- `validation.maxLength` — textarea의 HTML `maxLength` 속성에 바인딩. 입력 단계에서 절단된다.

## 사용 예시

### 1) 강제 종료 / 집행 완료 (proposal-manage)

```ts
// src/pages/dao/proposal-manage/detail/_id.modal.tsx
const { open: openReasonPrompt } = useReasonPrompt();

const handleForceEndVote = () => {
  openReasonPrompt({
    title: "투표 강제 종료 사유",
    placeholder: "사유를 입력하세요",
    submitLabel: "종료",
    validation: { minLength: 1, maxLength: 500 },
    callback: (reason) => {
      execute(() => api.dao.forceEndVote(proposalId, { reason }), { /* ... */ });
    },
  });
};

const handleCompleteExecution = () => {
  openReasonPrompt({
    title: "투표 강제 종료 사유",
    placeholder: "사유를 입력하세요",
    submitLabel: "종료",
    callback: (reason) => {
      execute(() => api.dao.completeExecution(proposalId, { reason }), { /* ... */ });
    },
  });
};
```

### 2) 게시글 모더레이션 (discuss-posts)

```ts
// src/pages/dao/discuss-posts-management/detail/_id.modal.tsx
const { open: openReasonPrompt } = useReasonPrompt();

const handlePostModeration = () => {
  if (postId < 0) return;
  openReasonPrompt({
    title: "투표 강제 종료 사유",
    placeholder: "사유를 입력하세요",
    submitLabel: "종료",
    callback: (reason) => {
      setIsLoading(true);
      execute(
        () => api.dao.updateDaoProposalDiscussionPostModeration(postId, { action: "HIDE", reason }),
        { /* ... */ },
      );
    },
  });
};
```

## 주의사항

- **호스트 마운트 필수**: 본 훅은 단독으로 동작하지 않는다. App 루트에 `<ReasonPromptHost />`가 마운트되어 있어야 한다 — `src/app.tsx`에 이미 마운트되어 있으므로 도메인 측에서 추가 작업 불필요.
- **callback은 확정 핸들러**: 취소 시 호출되지 않는다. "callback 진입 = 사용자가 확정"으로 간주해도 안전.
- **reason은 trim 후 전달**: callback의 `reason` 인자는 이미 `String.prototype.trim()` 적용된 값이다. 재 trim 불필요.
- **라벨 책임**: title/placeholder/submitLabel은 호출부에서 한글 문자열로 직접 전달한다.
- **cancelLabel 의도적 미전달 권장**: 대부분 기본값 `"취소"`로 충분하므로 미전달하면 훅이 알아서 처리한다. 도메인 특화 텍스트가 필요한 경우에만 명시 전달.
- **동시 호출 한계**: 호스트가 전역 단일이므로 동시에 두 번 publish하면 마지막이 이긴다. 짧은 시간 내 중복 트리거를 막을 책임은 호출부에 있다.

## 관련 자산

- [reason-prompt](../../components/reason-prompt/SKILL.md) — 본 훅이 publish하는 이벤트를 수신하는 컴포넌트/호스트
- [usePubSub](../use-pub-sub/SKILL.md) — `"open-reason-prompt"` 이벤트 채널 (`events.ts`에 등록됨)
