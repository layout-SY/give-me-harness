# Review Log — Reason Prompt 공용화 (S1 + S2 + S3)

- 일자: 2026-05-07
- 검토자: Watcher
- 기준선: implementation-log.md, plan.md 요청 범위, policy-review-checklist SKILL.md, policy-coding-convention SKILL.md
- 판정: **conditional pass**

---

## pass/fail: conditional pass

---

## 판정 근거 요약

S1/S2/S3 핵심 설계 목표(책임 분리, PubSub 인터페이스 통일, 구 모달 제거, 사전 결함 해소)는 모두 달성됨.
tsc/lint 에러 0건, 구 이벤트 및 파일 잔존 0건 확인.
단, 아래 3개 결함이 잔존하며, 그 중 하나(F-02)는 기능 정확성에 직결되므로 다음 수정 사이클에서 반드시 해소해야 함.

---

## 항목별 검토 결과

### 1. 책임 분리 (ReasonPrompt / ReasonPromptHost / useReasonPrompt)

판정: pass

- `reason-prompt.tsx`: `useLanguage`, `usePubSub` 미의존. props만으로 동작. 순수 프레젠테이셔널 원칙 충족.
- `reason-prompt-host.tsx`: PubSub 구독, 내부 상태(isOpen / value / options / pendingCallback) 관리, submit/close 흐름 담당. 컨테이너 역할 명확.
- `useReasonPrompt`: publish 캡슐화 + `cancelLabel` 기본값 i18n resolve 전담. 호출부는 i18n 키만 넘기면 되는 인터페이스 달성.
- `_initOptions` 상수로 초기값 분리, `handleClose`가 모든 상태를 일괄 초기화하는 패턴 적절.

주의 (non-blocking): `reason-prompt-host.tsx`의 `PromptOptions` 인터페이스가 `cancelLabel: string`을 required로 선언하나, `useReasonPrompt`에서 항상 채워 보내므로 런타임 안전. 단, Host가 직접 구독할 때 cancelLabel 누락 시 빈 문자열이 되는 잠재적 위험은 `cancelLabel?: string` + Host 내 fallback 처리로 보강 가능 (권고 수준, 현재 사용 패턴 기준 무해).

### 2. PubSub callback 패턴 일관성

판정: pass

- `"open-reason-prompt"` 타입이 `PubSubEvents`에 정확히 등록됨. `callback: (reason: string) => void`로 타입이 명시되어 기존 `callback: Function` 방식보다 타입 안전성이 높음.
- `useEffect` → `pubsub.subscribe` → cleanup `unsubscribe()` 패턴이 기존 이벤트 패턴(`calendar-picker`, `image-upload-popup` 등)과 동일.
- `setPendingCallback(() => callback)` 는 React의 functional updater 시그니처(`(prev) => next`)와 충돌 없이 함수를 state에 저장하는 표준 관용구. 정확히 사용됨.
- `handleSubmit`의 `useCallback` 의존성 배열 `[value, options.validation, pendingCallback, handleClose]` 완전함.

### 3. 호출부 마이그레이션 정합성

판정: pass

- `proposal-manage/detail/_id.modal.tsx`: `handleForceEndVote`, `handleCompleteExecution` 2건 모두 동일 인터페이스(`openReasonPrompt({ title, placeholder, submitLabel, callback })`)로 교체 완료.
- `discuss-posts-management/detail/_id.modal.tsx`: `handlePostModeration` 1건 동일 인터페이스 적용 완료.
- 구 `ForceEndVoteReasonModal` JSX 마운트 제거 확인, `open-force-end-vote-reason-modal` 이벤트 타입 제거 확인, 파일/디렉터리 삭제 확인.
- 잔존 참조 grep 결과 CLEAN.

### 4. 사전 결함 처리

판정: conditional pass

**F-01 (low): i18n 키 임시 재사용**

- `handlePostModeration` 성공 시 `mui["_dao_msg_delete_success"]`를 노출. 의미적으로 "숨김 처리 성공"과 "삭제 성공"은 다름.
- implementation-log.md에 i18n 티켓으로 명시 완료. 허용 가능한 임시 대응이나 티켓 번호 또는 TODO 코드 주석 부재.
- 권고: 코드 내 `// TODO(i18n): moderation 전용 키 분리 - _dao_msg_moderation_success` 주석 1줄 추가.

**F-02 (medium, 수정 필요): handlePostModeration guard 누락**

- `handleDeletePost`는 `if (fetchedData.postId < 0) return;` guard 존재.
- `handlePostModeration`은 `_initState.postId = -1` 상태에서도 버튼 클릭이 가능하며, callback 내에서 `postId = -1`로 API를 호출할 수 있음.
- `_initState`가 postId: -1로 초기화되고, 모달이 열린 직후 requestGet이 비동기이므로 데이터 미수신 상태에서 버튼 클릭 시 postId: -1로 moderation API가 호출됨.
- `handleDeletePost`와 동일하게 `if (fetchedData.postId < 0) return;` guard를 콜백 내부 또는 `handlePostModeration` 진입부에 추가해야 함.

**F-03 (low): requestGet의 try/finally setIsLoading 안티패턴**

- `execute()`가 내부적으로 `finally { setIsLoading(false); }`를 처리함 (use-api.tsx:60-62 확인).
- `requestGet`의 `try/finally setIsLoading(false)`와 `handleDeletePost`의 동일 패턴은 `execute` 내부 setIsLoading과 이중으로 호출됨.
- `handlePostModeration` callback의 `setIsLoading(true)` 단독 호출도 같은 이중 관리 패턴. execute가 완료되면 execute 내부에서 false로 설정되나, 로컬 state와의 동기화 타이밍에 따라 깜빡임 가능성 있음.
- implementation-log.md에 "본 작업 범위 외"로 명시되어 있고 기존 파일의 사전 안티패턴이므로 이번 작업 범위에서 반려 사유로 삼지 않음. 단, S3에서 callback 내 `setIsLoading(true)` 추가 시 기존 안티패턴을 확산한 부분은 권고로 기록.

### 5. 잔존 리스크 및 누락 항목

**R-01 (blocking): memory/reusable-assets.md 미갱신**

- policy-review-checklist SKILL.md 규정: "신규 공용 컴포넌트/훅이 추가된 경우 `memory/reusable-assets.md`에 항목 추가 완료 여부".
- `ReasonPrompt`, `ReasonPromptHost` (모달/오버레이 공용 컴포넌트), `useReasonPrompt` (커스텀 훅)이 추가되었으나 `memory/reusable-assets.md`에 미등록.
- 다음 사이클 또는 현재 사이클 내에서 반드시 추가 필요. 이 항목이 누락되면 동일 패턴이 재발명될 위험이 있음.

**R-02 (low): discuss-posts useEffect 빈 의존성 배열**

- `useEffect(() => { ... }, [])` — `handleOpen`이 의존성에서 누락됨.
- `handleOpen`이 `useCallback`으로 감싸지지 않아 매 렌더마다 새 참조를 생성하지만, 빈 배열로 인해 초기 마운트에만 subscribe됨.
- 현재 동작상 문제는 없으나(subscribe 한 번으로 충분), eslint-plugin-react-hooks `exhaustive-deps` 규칙 위반 패턴. S3 변경 범위 외이므로 blocking으로 삼지 않음.

**R-03 (low): handleCompleteExecution의 forceEndVote 전용 i18n 키 재사용**

- `handleForceEndVote`와 `handleCompleteExecution` 둘 다 `_dao_proposal_forceEndVote_reason_*` 키를 사용.
- "투표 강제 종료"와 "실행 완료" 액션은 의미가 다를 수 있음. 기존 forceEndVoteReasonModal도 동일 키를 사용했으므로 기존 동작 유지이며, i18n 분리는 별도 티켓 범위.

---

## violations

- F-02: handlePostModeration guard 누락 — postId < 0 상태에서 API 호출 가능
- R-01: memory/reusable-assets.md 미갱신 — 신규 공용 컴포넌트/훅 등록 누락 (policy-review-checklist SKILL.md 위반)

## required_fixes

1. `src/pages/dao/discuss-posts-management/detail/_id.modal.tsx`
   - `handlePostModeration` 함수 진입부에 `if (postId < 0) return;` guard 추가
   (또는 JSX 호출부에서 `fetchedData.postId >= 0` 조건부로 버튼 활성화)

2. `.claude/memory/reusable-assets.md`
   - 모달/오버레이 섹션에 `reason-prompt` + `ReasonPromptHost` 항목 추가
   - 커스텀 훅 섹션에 `useReasonPrompt` 항목 추가

3. (권고) `src/pages/dao/discuss-posts-management/detail/_id.modal.tsx`
   - `handlePostModeration` callback 내 `// TODO(i18n): moderation 전용 키 분리` 주석 추가

---

## repeat_issue_detected: false

## escalation_needed: false

---

## 후속 권고 (범위 외)

- `requestGet`, `handleDeletePost`의 try/finally setIsLoading 이중 관리 패턴 — evaluation-log.md BL-6 연계 정리 권장
- moderation `action` 분기(`HIDE` / `RESTORE`) UI — 현재 숨김 단건만 노출, 복구 버튼 없음
- `useEffect` 빈 의존성 배열 패턴 (`handleOpen`) — discuss-posts 도메인 전반 정리 권장

---

## 산출물

- review-log.md (본 파일)

## next_action

F-02 (postId guard) 와 R-01 (reusable-assets 갱신) 수정 후 재제출.
수정 범위가 2건으로 소규모이므로 별도 S4 없이 hotfix 단위로 처리 권장.

---

## Re-review — 2026-05-07 (F-02 / R-01 수정 검증)

- 검토 대상: F-02 handlePostModeration postId guard, R-01 reusable-assets.md 갱신
- 판정: **pass**

### F-02
- `_id.modal.tsx` line 65: `if (postId < 0) return;` 진입부 확인. handleDeletePost와 대칭 구조 충족.
- 인터페이스 정합성 확인: JSX 호출부에서 `handlePostModeration(fetchedData.postId)`로 전달, guard가 정상 차단.

### R-01
- `reusable-assets.md` 모달/오버레이 섹션 `reason-prompt` 행 등록 확인.
- 커스텀 훅 섹션 `useReasonPrompt` 행 등록 확인.
- SKILL.md 링크 미실체는 generator.md §"watcher pass 후 문서화" 규정에 의거 허용.

## 최종 상태: approved

### 후속 작업 (별도 티켓)
1. generator — `reason-prompt` / `use-reason-prompt` SKILL.md 실체 작성 (watcher pass 후 문서화 규정)
2. F-01 — moderation 전용 i18n 키(`_dao_msg_moderation_success`, `_dao_post_hide_reason_*`) 분리
3. F-03 — discuss-posts 도메인의 try/finally setIsLoading 이중 관리 정리 (evaluation-log.md BL-6 연계)
