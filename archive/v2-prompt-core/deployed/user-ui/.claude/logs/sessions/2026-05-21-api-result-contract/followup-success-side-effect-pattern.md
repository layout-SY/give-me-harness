# Follow-up — 성공 부수효과(alert + pubsub) 패턴 추상화

- 발의: 2026-05-22 (hook 계층 분리 작업 중)
- 상태: deferred (현 세션의 hook 분리 작업 완료 후 별도 진행)
- 우선순위: 중 (반복 패턴, 도메인 확대 시 비례해 중복 증가)

---

## 문제 인식

거의 모든 도메인의 modal/페이지 hook에서 **"도메인 액션 성공 시 토스트 + 목록 refresh 이벤트 발행"** 패턴이 반복된다. 현재 코드 베이스의 일반 형태:

```ts
const handleX = async () => {
  const result = await someAction();
  if (!result.success) return;
  Dialog.alert({ content: <p>{successMessage}</p> });
  pubsub.publish("refresh-<domain>-list");
  // surface-specific: 모달 닫기, refetch, navigate 등
};
```

이게 N개 도메인 × M개 액션(restore/hide/delete/...) 만큼 반복되는 구조.

## 책임 배치 결정

(2026-05-22 hook 계층 논의 결과)

- 성공 시 **`Dialog.alert(successMessage)` + `pubsub.publish(...)`** → **modal/페이지 hook(Application Service 레이어) 책임**으로 통일
- 기능 hook(Stateful Service / Aggregate) 책임에서 제외 → fetch hook은 도메인 액션의 실행/상태/게이트에 집중
- 실패 시 자동 Dialog는 `useApi`의 `silent: false`로 일원화 (현 구조 유지)

## 후보 추상화 패턴

### Option 1 — 템플릿 함수 (얇은 헬퍼)

```ts
const onActionSuccess = ({ successMessage, refreshEvent }: {
  successMessage: string;
  refreshEvent?: PubSubEvent;
}) => {
  Dialog.alert({ content: <p>{successMessage}</p> });
  if (refreshEvent) pubsub.publish(refreshEvent);
};
```

- 장점: 도입 비용 낮음, 호출부 가독성 즉시 개선
- 단점: 여전히 호출부에서 명시적으로 호출 필요

### Option 2 — `useDomainActionFlow` 훅 (콜백 컴포지션)

```ts
const { run } = useDomainActionFlow({
  refreshEvent: "refresh-dao-proposals-discussion-posts-list",
});

const handleDeletePost = () => run({
  action: () => requestDeletePost(),
  successMessage: mui["_dao_msg_delete_success"],
  onSuccess: () => { handleModalClose(); discussPostListRefetch(); },
});
```

- 장점: 흐름이 데이터처럼 표현됨, 테스트 가능
- 단점: 학습 곡선, 콜백 패턴이 또 들어옴

### Option 3 — TanStack Query mutation `onSuccess` (TQ 도입 시 자연 통합)

```ts
useMutation(api.dao.deleteDaoProposalDiscussionPost, {
  onSuccess: () => {
    Dialog.alert({ content: <p>{successMessage}</p> });
    queryClient.invalidateQueries(["discuss-post-list"]);  // pubsub 대체
  },
});
```

- 장점: 캐시 무효화가 pubsub 대체 → 이벤트명 typo 같은 류 사라짐(이번 PR-3에서 발견된 `-list` 누락 버그가 구조적으로 발생 불가)
- 단점: TQ 도입이 선행 조건
- **권고**: TQ 도입 로드맵이 있다면 Option 3이 종착지. Option 1을 임시 다리로 깔고 TQ 도입 시 일괄 치환.

## 권고 진행 순서

1. **현 세션의 hook 계층 분리 작업 완료** (alert/pubsub을 fetch → modal 이전)
2. Option 1 (얇은 헬퍼)로 modal hook 내부 정리 — 도메인 확대 PR(PR-4~7)에서 동시에 적용
3. TQ 도입 검토 시점에 Option 3로 일괄 치환

## 연관 이슈

- PR-3 watcher 게이트에서 발견된 `useDiscussionCommentDelete`의 pubsub 이벤트명 typo (`-list` 누락) — 이 패턴 자체가 typo 발생 가능 구조라는 증거. Option 3로 가면 구조적 해소.
- `final-summary.md`의 "미해결 이슈" 항목과 묶어 처리 가능.

## 참고 — TanStack Query 도입 시 부수 효과

- `fetchedData` `useState` → query cache로 이전
- pubsub 도메인 이벤트 → `invalidateQueries(['key'])`로 일원화
- fetch hook 책임이 "per-endpoint query/mutation의 도메인 facade"로 명확해짐 (분리 가치 증가)
- silent/dialog 정책은 `MutationCache` 전역 설정 또는 mutation별 `onError`로
