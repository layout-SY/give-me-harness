# Implementation Log — Reason Prompt 공용화 (S1)

- 일자: 2026-05-07
- 범위: plan.md의 **S1 — 공용 컴포넌트·호스트·훅 신설**
- 채택안: 권고안 A 변형 (PubSub + callback 패턴 유지, 범용 단일 이벤트명 통일)
- S2/S3 미수행 (forceEndVoteReasonModal 교체, discuss-posts handlePostModeration 적용은 후속)

## 변경 파일

### 신규 생성
- `src/components/reason-prompt/reason-prompt.tsx` — 도메인 무관 프레젠테이셔널 컴포넌트. props로 라벨/검증/값/핸들러 수신. `useLanguage`, `usePubSub` 미의존.
- `src/components/reason-prompt/reason-prompt.css` — 기존 `forceEndVoteReasonModal.css` 스타일을 클래스 prefix `reason-prompt__*`로 rename 이식.
- `src/components/reason-prompt/reason-prompt-host.tsx` — App 루트에 1회 마운트되는 글로벌 호스트. `"open-reason-prompt"` 구독, 내부 state(open/value/options/pendingCallback) 관리, submit 시 trim된 reason을 callback에 전달, 취소 시 callback 미호출.
- `src/components/reason-prompt/index.ts` — `ReasonPrompt`, `ReasonPromptHost` barrel export.
- `src/hooks/use-reason-prompt/index.ts` — publish 캡슐화 훅. `cancelLabel` 미전달 시 훅 단계에서 `mui["_cancel"]`로 resolve. 호스트/컴포넌트는 i18n 미의존 원칙 유지.

### 기존 수정
- `src/hooks/use-pub-sub/events.ts` — `PubSubEvents` 타입맵에 `"open-reason-prompt"` 추가. 기존 `"open-force-end-vote-reason-modal"`은 S2에서 제거 예정이므로 이번 단계 유지.
- `src/app.tsx` — `<SelectUsersPopup />` 다음, `<Router />` 앞에 `<ReasonPromptHost />` 1회 마운트.

## 책임 분리 요약

| 파일 | 책임 |
|---|---|
| `reason-prompt.tsx` | 순수 UI. 검증 정책에 따른 submit disabled 표시, textarea 값 표시. |
| `reason-prompt-host.tsx` | 모달 상태 + PubSub 구독 + submit/close 흐름. trim/검증 후 callback 호출. |
| `use-reason-prompt` | 호출부에서 publish 시그니처를 단순화. cancelLabel 기본값 i18n resolve. |

## 인터페이스

```ts
// 호출 예시
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

## 검증

- `yarn lint`: **pass** (no errors, no warnings).
- `npx tsc --noEmit`: **S1 신규 파일에서 에러 0건**.
  - 보고된 2건은 모두 `src/pages/dao/discuss-posts-management/detail/_id.modal.tsx` 사전 존재 결함이며 plan.md의 S3 범위에서 처리.
    - `(65,79) error TS2304: Cannot find name 'payload'.` — handlePostModeration의 미선언 변수 (S3에서 reason 합성과 함께 수정).
    - `(67,43) error TS2551: Property '_dao_msg_moderation_success' does not exist...` — i18n 키 부재 (별도 i18n 티켓).

## 주의/리스크

- 기존 `"open-force-end-vote-reason-modal"` 이벤트와 `ForceEndVoteReasonModal` 컴포넌트는 그대로 남아 있음 → S2 완료 전까지 두 모달이 공존하지만 각자 독립 동작하므로 충돌 없음.
- ReasonPromptHost는 App 루트에 1회 마운트되어 전역 단일 인스턴스. 동시에 두 호출이 publish되면 마지막 publish가 이긴다 (기존 PubSub + 단일 호스트 패턴과 동일 한계).

## S2 완료 — forceEndVoteReasonModal 교체 및 제거

### 변경 내역
- `src/pages/dao/proposal-manage/detail/_id.modal.tsx`
  - `ForceEndVoteReasonModal` import 제거 → `useReasonPrompt` import로 교체
  - `<ForceEndVoteReasonModal />` JSX 마운트 제거
  - `handleForceEndVote`, `handleCompleteExecution`의 `pubsub.publish("open-force-end-vote-reason-modal", ...)` → `openReasonPrompt({ title, placeholder, submitLabel, callback })`로 교체
  - 라벨은 기존 `_dao_proposal_forceEndVote_reason_*` i18n 키 그대로 재사용
- `src/hooks/use-pub-sub/events.ts` — `"open-force-end-vote-reason-modal"` 타입 항목 제거
- 파일 삭제
  - `src/pages/dao/proposal-manage/detail/components/sections/reason/forceEndVoteReasonModal.tsx`
  - `src/pages/dao/proposal-manage/detail/components/sections/reason/forceEndVoteReasonModal.css`
  - `src/pages/dao/proposal-manage/detail/components/sections/reason/` 빈 디렉터리 제거

### 검증
- `grep -rn "open-force-end-vote-reason-modal\|ForceEndVoteReasonModal\|forceEndVoteReasonModal" src/` → **잔존 참조 0건**
- `yarn lint`: pass
- `tsc --noEmit`: S2 변경분 에러 0건. 기존 보고된 2건(discuss-posts S3 사전 결함)만 잔존.

## S3 완료 — discuss-posts handlePostModeration 적용

### 변경 내역
- `src/pages/dao/discuss-posts-management/detail/_id.modal.tsx`
  - `useReasonPrompt` import 추가
  - `handlePostModeration`을 `openReasonPrompt({ ...labels, callback })` 흐름으로 재구성
  - callback 내부에서 `execute(() => api.dao.updateDaoProposalDiscussionPostModeration(postId, { action: "HIDE", reason }), ...)` 호출
  - 사전 결함 동시 해결: `payload` 미선언 변수 제거, 잘못된 i18n 키 `_dao_msg_moderation_success` → 임시로 `_dao_msg_delete_success` 재사용 (후속 i18n 티켓에서 전용 키 분리 권장)
  - try/finally setIsLoading 안티패턴은 본 작업 범위 외이므로 그대로 두되 setIsLoading 호출은 callback 내부로 이동
- 라벨 i18n 키는 `_dao_proposal_forceEndVote_reason_*` 재사용 (의미가 "사유 입력"으로 도메인 무관). 별도 디스커션 전용 키 분리는 i18n 티켓.

### 검증
- `yarn lint`: pass
- `tsc --noEmit`: **에러 0건** (S1 단계에서 보고된 사전 결함 2건 모두 해소)

## 후속 권장 (범위 외, 메모)

- discuss-posts 도메인의 try/finally setIsLoading 안티패턴 일괄 정리 (evaluation-log.md BL-6과 연계)
- moderation 전용 i18n 키 분리 (`_dao_msg_moderation_success`, `_dao_post_hide_reason_*`)
- moderation `action` 분기 (`HIDE` / `RESTORE`) — 현재 UI는 숨김 단건만 노출

## Approach A — 서브에이전트 권한 정책 도입 (병행 작업)

CLAUDE.md / agents/*.md를 갱신하여 multi-agent-spec와 일관된 폴백 절차를 명시했다.

- `CLAUDE.md` §4.1 "서브에이전트 권한 정책" 신설
  - generator/refactorer/publisher가 Write/Edit를 **직접 호출**
  - 사용자는 도구 호출 시점마다 파일 단위로 승인
  - 권한 거부 시 폴백: 서브에이전트는 `denied_tool_calls` + `prepared_changes`를 결과로 반환 → 메인이 적용
  - 무한 재시도 금지, 두 번째 거부 시 사용자에게 권한 점검 요청
- `.claude/agents/generator.md`, `refactorer.md`, `publisher.md` — 각 파일에 "권한 거부 시 폴백 (Approach A)" 섹션 추가

### 사용자 액션 필요
실제 권한 부여는 `.claude/settings.local.json`의 `permissions.allow`에 `Write`, `Edit` 추가가 필요하나, 보안 민감 파일이므로 본 작업에서는 수정하지 않았다. 사용자가 직접 추가하거나 프롬프트로 명시 지시 필요.

## Watcher 게이트 — 최종 결과

- 1차 검토: **conditional pass** (F-02 postId guard 누락, R-01 reusable-assets.md 미갱신)
- 수정 적용
  - `discuss-posts-management/_id.modal.tsx`의 `handlePostModeration` 진입부에 `if (postId < 0) return;` 추가
  - `.claude/memory/reusable-assets.md`에 `reason-prompt` (모달/오버레이), `useReasonPrompt` (커스텀 훅) 등록
- 재검증: `yarn lint` pass, `tsc --noEmit` 에러 0건
- 2차 검토: **approved (pass)** — 산출물 `.claude/logs/sessions/2026-05-07-reason-prompt-extraction/review-log.md`

## 후속 작업 (별도 티켓)

1. **신규 자산 SKILL.md 작성** (generator 책임, watcher pass 후 규정에 따른 후속) — **완료 (2026-05-07)**
   - [x] `.claude/skills/reference/components/reason-prompt/SKILL.md` — 작성 완료
   - [x] `.claude/skills/reference/custom-hooks/use-reason-prompt/SKILL.md` — 작성 완료
   - [x] `.claude/skills/reference/components/COMMON_COMPONENTS.md` — `reason-prompt` 등록 (모달/오버레이 섹션)
2. **F-01 (i18n)** — moderation 전용 키 분리: `_dao_msg_moderation_success`, `_dao_post_hide_reason_*`
3. **F-03 (라이프사이클)** — discuss-posts 도메인 try/finally setIsLoading 이중 관리 정리 (evaluation-log.md BL-6 연계)
4. **Approach A 실권한 부여** — `.claude/settings.local.json`의 `permissions.allow`에 `Write`, `Edit` 추가 완료
