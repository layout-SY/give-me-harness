# 1차 — Reason 모달 공용화 설계 논의 (verbatim)

- 일자: 2026-05-07
- 참여: 사용자, evaluator 에이전트, 메인 에이전트
- 추가 정리 없이 원문 그대로 보존

---

## [사용자]

@src/pages/dao/discuss-posts-management/detail/_id.modal.tsx 에서 지금 새롭게 "게시글 숨김"에 대한 기능을 추가하는데, 사유를 작성하는 모달과 요청 body에 reason이라는 이름으로 사유를 추가하여 요청해야 돼. 따라서 사유 작성 모달을 넣으려고 하는데 @src/pages/dao/proposal-manage/detail/components/sections/reason/forceEndVoteReasonModal.tsx 다른 도메인에서 해당 도메인에 대한 사유를 작성하는 모달이 이미 존재해. 다만 이 모달은 해당 도메인 자체에 종속되어 있는 구조야.

따라서 이 모달을 공용 컴포넌트화 하고, 이 공용 컴포넌트에서 작성된 사유 문자열 return하는 reason 모달 전용 hook도 생성해줘. 이 때 이 hook을 책임 범위는 내가 생각했을 땐 각 도메인에서 payload 전체를 hook에 제공하면, hook에서 reason과 혹여나 필요한 기타 정보들을 payload에 담아 return하고, 이를 해당 도메인에서 받아 가공 혹은 사용하는 방식, 각 도메인에선 그냥 해당 hook과 공용 컴포넌트를 사용하고, hook을 사용자가 작성한 reason 문자열을 return하면 해당 도메인에서 알아서 가공 혹은 사용하는 방식. 이렇게 두 가지를 생각했는데  책임(관심사) 분리 관점과 추상화 작업 관점에서 이 두 가지 방식이 적절한 지 판단하고, 적절하다면 두 가지 방식 중 추천하는 방식을 근거와 함께 채택하고, 적절하지 않다면 다른 어떤 방식으로 작업하면 좋은 지 마찬가지로 근거와 함께 제공해줘.

evaluator 에이전트에게 위임

---

## [메인 에이전트 → evaluator 위임 프롬프트]

DAO 도메인에서 "사유(reason) 작성 모달"을 공용 컴포넌트 + 전용 훅으로 추출하려 합니다. 두 가지 후보 설계가 있고, 책임(관심사) 분리와 추상화 관점에서 어떤 방식이 적절한지, 또는 더 나은 제3의 방식이 있는지 평가해 주세요.

## 배경

현재 `src/pages/dao/proposal-manage/detail/components/sections/reason/forceEndVoteReasonModal.tsx`에 도메인 종속 사유 모달이 있습니다. 핵심 동작:
- `usePubSub`의 `"open-force-end-vote-reason-modal"` 이벤트로 열림
- 이벤트 payload에 `callback: (reason: string) => void` 전달
- 모달은 textarea로 reason 입력 → submit 시 callback(reason) 호출 → 닫힘
- 사용 측은 callback 안에서 자기 도메인의 API 호출(예: 강제 종료 요청 body에 reason 포함)

이제 동일한 패턴이 `src/pages/dao/discuss-posts-management/detail/_id.modal.tsx`의 "게시글 숨김(handlePostModeration)" 기능에도 필요합니다. body에 `reason`이 추가되어야 합니다. 즉 같은 사유 입력 UI를 다른 도메인에서도 재사용해야 합니다.

## 후보 1 — payload 위임형 훅
- 호출 측이 hook에 "최종 payload(또는 partial payload)"를 넘김
- hook은 모달을 띄우고 reason을 받은 뒤, payload에 reason과 기타 메타(작성 시각 등)를 합쳐서 도메인에 반환
- 호출 측은 반환된 완성 payload로 API 호출

## 후보 2 — reason 문자열만 반환하는 훅
- 호출 측은 hook을 호출하면 모달이 뜸
- 사용자가 작성한 reason 문자열만 Promise/콜백으로 반환
- payload 합성·가공·API 호출은 전적으로 호출 도메인 책임

## 평가해 줄 것
1. 두 방식 각각이 책임 분리와 추상화 관점에서 적절한지
2. 적절하다면 둘 중 어느 쪽을 추천하는지 (근거 명확히)
3. 부적절하다면 어떤 방식이 더 나은지 (예: 컨테이너 + 컨텐츠 분리, props 기반 모달 + open API 훅, render prop, Promise 반환 기반 imperative API 등)
4. 공용 컴포넌트 위치/네이밍, 훅 시그니처(예시 한 줄) 권고
5. 기존 `usePubSub` 기반 글로벌 모달 패턴과의 정합성 고려

프로젝트는 한국어 응답이 강제이고, evaluator 역할대로 결론·근거 중심으로 간결하게 정리해 주세요. 코드 작성/수정은 하지 말고 평가만 해주세요. 필요한 경우 `src/components/`와 `src/hooks/` 구조, 기존 모달 패턴(`src/components/modal`, `src/modules/dialog`)을 빠르게 살펴보고 권고에 반영해 주세요.

---

## [evaluator 응답]

평가를 정리합니다.

---

```yaml
summary: 사유(reason) 입력 모달은 "입력 UI" 책임만 갖는 공용 컴포넌트로 추출하고, 호출 측은 reason 문자열만 비동기로 받는 imperative 훅(Promise 기반)을 사용하는 것이 책임 분리·재사용성 양면에서 가장 적절하다. 후보 1(payload 위임형)은 추상화 누수로 부적절, 후보 2(reason만 반환)가 옳은 방향이며 다만 "콜백 기반 PubSub" 대신 "Promise 반환 imperative API"로 다듬는 것을 권고.
decision: recommendation_ready
diagnosis_report: |
  현행 ForceEndVoteReasonModal은 PubSub의 "open-force-end-vote-reason-modal" 이벤트 + callback(reason) payload로 동작한다. 모달 자체는 reason 입력/검증/닫힘만 책임지므로 도메인 종속 부분은 사실상 i18n 키와 이벤트 이름뿐이다. 즉 본질은 이미 "도메인 무관 reason prompt"이며, 현재 forceEndVote 네이밍은 이름의 종속성일 뿐이다.

  두 가지 신규 사용처(강제 종료, 게시글 숨김)는 동일한 입력 UI를 필요로 하지만 "payload 형태/엔드포인트/메타필드"가 서로 다르다. 따라서 모달이 payload 합성에 개입하면 도메인 수만큼 분기가 생긴다.

  후보 1(payload 위임형)의 문제:
    - 모달/훅이 도메인 payload 스키마를 알아야 한다 → 도메인 추가 시 제네릭 폭발 또는 any 추상화로 회귀
    - "reason 입력"이라는 단일 책임 위반(입력 + payload 가공 + 메타 주입 혼재)
    - 작성 시각 같은 메타는 호출 도메인이 직접 부여하는 편이 테스트/검증에 유리
    - 결과적으로 모달 추출의 효용(도메인 무관 재사용)이 사라짐

  후보 2(reason 문자열만 반환)의 강점:
    - 모달/훅 책임은 "유효한 reason 문자열을 비동기로 산출"로 명확
    - 호출 도메인은 자기 API 시그니처/메타 주입을 자기 영역에서 처리(레이어 정합)
    - 도메인 추가 시 모달은 무변경, props로 라벨·placeholder·검증 정책만 주입

  단, 후보 2를 "PubSub + callback 그대로"로 구현하면 다음 부채가 남는다:
    - 이벤트 문자열 분기 + payload 콜백 패턴은 타입 안전성·취소(close 시)·중복 호출 처리가 약함
    - 동일 모달을 도메인별로 새 이벤트명 만들어 부풀리는 안티패턴 위험(open-force-end-vote-reason-modal 같은 명명이 그 신호)
    - usePubSub은 유지하되, "reason prompt"는 Promise 반환형 imperative API로 가져가는 편이 호출부 가독성·취소 처리(reject 또는 resolve(null))가 깔끔
architectural_risks:
  - 도메인별로 별도 PubSub 이벤트 이름을 만드는 패턴이 누적되면 글로벌 이벤트 네임스페이스 오염 및 검색성 저하
  - 모달이 payload를 합성하면 API 스키마 변경이 공용 모듈로 전파되어 변경 영향도 확산
  - PubSub callback 방식은 "사용자가 닫음(취소)" 시그널이 명시적이지 않아 호출부가 로딩 상태 정리에 실수하기 쉽다
  - i18n 키가 모달 내부에 하드코딩되어 있어, 다른 도메인에서 재사용 시 라벨 차이를 흡수하기 어렵다(현행 forceEndVote 키 종속)
  - 동일 모달이 동시에 두 번 열릴 가능성, validation 정책(최소 글자 수 등) 도메인별 차이 미반영 위험
improvement_options:
  - 권고안 A (1순위, 컨테이너+컨텐츠 분리 + Promise imperative 훅):
      구조:
        1) 프레젠테이셔널 컴포넌트: src/components/reason-prompt/reason-prompt.tsx
           - props: open, title, placeholder, submitLabel, minLength, maxLength, initialReason, onSubmit(reason), onClose
           - 도메인/이벤트 무관, 재사용 컴포넌트로만 동작
        2) 글로벌 호스트: src/components/reason-prompt/reason-prompt-host.tsx (App 루트에 1회 마운트)
           - 내부 state(open, options, resolver) 관리
        3) 호출 훅: src/hooks/use-reason-prompt/index.ts
           - 시그니처: const { promptReason } = useReasonPrompt();
                      const reason = await promptReason({ title, placeholder, submitLabel, minLength });
                      // 사용자가 취소 시 reason === null
           - 내부 구현은 PubSub 또는 jotai/Context 어떤 것으로도 가능. 외부 인터페이스는 Promise 고정.
      호출 예 (개념):
          const reason = await promptReason({ title: mui["_dao_post_hide_reason_title"] });
          if (!reason) return;
          await hidePost({ postId, reason, moderatedAt: Date.now() });
      장점: 후보 2의 책임 분리 + Promise로 취소/완료가 명시적, 도메인 라벨은 props로 외주화, 호스트는 단일.

  - 권고안 B (차선, 후보 2의 직변형):
      현행 PubSub 패턴 유지 + 이벤트 이름을 도메인 무관으로 일반화("open-reason-prompt")
      payload: { options, callback, onCancel? }
      모달 내부에서 i18n 키를 props로 받도록 일반화
      장점: 변경 폭 작음. 단점: 취소 시그널 누락 위험 잔존, 외부 API가 여전히 callback 기반.

  - 비권고 (후보 1):
      payload 위임형은 도메인 결합이 모달로 침투 → 추출 효용 저하. 채택 시 제네릭 + 변환 함수(transform: (reason) => Payload)로 우회해도 결국 호출부가 transform을 작성하므로, 차라리 reason만 받아 호출부에서 합성하는 권고안 A/B와 동치이거나 더 복잡.
recommended_backlog:
  - [P0] src/components/reason-prompt/* 신설(프레젠테이셔널 + 호스트), 도메인 i18n/검증 정책 props화
  - [P0] src/hooks/use-reason-prompt 신설(Promise 반환 imperative API). 취소 시 null resolve 규약 문서화
  - [P0] App 루트에 ReasonPromptHost 1회 마운트(전역 모달 정합성 유지)
  - [P1] ForceEndVoteReasonModal 제거 및 호출부(proposal force-end) 마이그레이션
  - [P1] discuss-posts-management _id.modal.tsx 의 handlePostModeration에 promptReason 적용(body.reason 합성은 호출부 책임)
  - [P2] PubSub 이벤트 명명 가이드 SKILL 보강 — "도메인명+동작" 대신 "범용 동작명" 권고, 도메인 라벨은 payload로
  - [P2] 동일 패턴(공지 비공개 사유, 댓글 삭제 사유 등) 재사용 자산을 .codex/memory/reusable-assets.md에 등재
  - [P3] 검증 정책(min/max length, 금칙어) 표준화 옵션을 props 스키마에 반영
handoff_to_planner_optional: true
reasons:
  - 후보 1은 모달이 도메인 payload 스키마를 알게 만들어 단일 책임/재사용성을 모두 훼손
  - 후보 2 방향(=reason만 반환)이 옳으나, 인터페이스를 Promise 기반 imperative API로 다듬으면 취소·완료·타입 안전성이 향상
  - 컨테이너(호스트)+컨텐츠(프레젠테이셔널) 분리는 기존 src/components/modal, src/modules/dialog 패턴과도 일관
  - 도메인별 PubSub 이벤트 신설을 막아 글로벌 네임스페이스 오염을 예방
artifacts:
  - evaluation-log.md
next_action: 사용자가 권고안 A로 합의하면 planner에게 이관하여 plan.md(컴포넌트/훅 시그니처 확정, 호출부 마이그레이션 순서, 호스트 마운트 위치) 작성 단계로 진행
log:
  - 현행 ForceEndVoteReasonModal 구조 확인(도메인 종속은 i18n 키/이벤트명에 한정)
  - usePubSub 구현 확인(타입드 이벤트맵 기반, 취소 시그널 별도 없음)
  - src/components, src/hooks 디렉토리 패턴 확인(컴포넌트 단위 폴더 + index/css 패턴 일관)
status: recommendation_ready
```

참고 파일 경로:
- /Users/okand/SynologyDrive/synthoria-admin-ui/src/pages/dao/proposal-manage/detail/components/sections/reason/forceEndVoteReasonModal.tsx
- /Users/okand/SynologyDrive/synthoria-admin-ui/src/hooks/use-pub-sub/index.ts
- /Users/okand/SynologyDrive/synthoria-admin-ui/src/components/modal/modal.tsx
- /Users/okand/SynologyDrive/synthoria-admin-ui/src/modules/dialog/dialog.tsx
- /Users/okand/SynologyDrive/synthoria-admin-ui/src/pages/dao/discuss-posts-management/detail/_id.modal.tsx

권고안 A로 진행할지, 권고안 B(최소 변경)로 진행할지 결정해 주시면 planner 이관 가능합니다.

---

## [메인 에이전트 요약 응답]

## evaluator 평가 결론

**두 후보의 적절성**
- **후보 1 (payload 위임형)**: 부적절. 모달/훅이 도메인 payload 스키마를 알아야 하므로 "reason 입력"이라는 단일 책임을 위반하고, 추출 효용(도메인 무관 재사용)이 사라집니다.
- **후보 2 (reason 문자열만 반환)**: 방향은 옳음. 다만 현행 PubSub + callback 그대로는 취소 시그널·타입 안전성이 약하다는 부채가 남습니다.

**권고안 A (1순위) — 컨테이너+컨텐츠 분리 + Promise imperative 훅**

구조:
1. **프레젠테이셔널 컴포넌트** `src/components/reason-prompt/reason-prompt.tsx`
   - props: `open, title, placeholder, submitLabel, minLength, maxLength, initialReason, onSubmit, onClose`
2. **글로벌 호스트** `src/components/reason-prompt/reason-prompt-host.tsx` (App 루트에 1회 마운트)
3. **호출 훅** `src/hooks/use-reason-prompt`
   - 시그니처: `const reason = await promptReason({ title, placeholder, ... })`
   - 취소 시 `reason === null` 규약

호출 예시:
```ts
const reason = await promptReason({ title: mui["_dao_post_hide_reason_title"] });
if (!reason) return;
await api.dao.updateDaoProposalDiscussionPostModeration(postId, { reason });
```

**채택 근거**
- 모달은 "유효한 reason 문자열을 비동기로 산출"하는 단일 책임만 가짐
- payload 합성·메타 주입·API 호출은 도메인 영역에 남아 레이어 정합성 유지
- Promise 기반이라 취소/완료가 명시적, 도메인별 PubSub 이벤트 신설로 인한 글로벌 네임스페이스 오염 방지
- 기존 `src/components/modal`, `src/modules/dialog`의 컨테이너+컨텐츠 분리 패턴과 일관

**차선 (권고안 B)**: 현행 PubSub 유지하되 이벤트명을 `open-reason-prompt`로 일반화하고 i18n 키를 props화. 변경 폭은 작지만 취소 시그널 부재 부채는 잔존.

---

권고안 A로 진행할지, B(최소 변경)로 갈지 결정해 주시면 planner로 이관해 `plan.md`(컴포넌트/훅 시그니처 확정, 호출부 마이그레이션 순서, 호스트 마운트 위치) 작성 단계로 넘어가겠습니다.

이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?

---

## [사용자 결정]

일단은 권고안 A로 진행하되, pubsub + callback 형태를 그대로 유지 하며 작업하고, planner에게 위임해. 그리고 넌 나랑 추가적으로 할 얘기가 있어.
