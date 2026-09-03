# CP Comment stale-row 의존성 결정

## 결정
- freshness는 `entities` query가 제공하는 `isPlaceholderData`를 `pages/cp-comment` data hook에서 `isCurrentData`로 변환한다.
- process hook이 stale 선택·변경·저장 차단을 소유하고 controller는 View 계약을 조립한다.
- shared `Table`과 entity query의 공개 계약은 변경하지 않는다.

## 의존 방향
```text
cp-comment controller
  -> cp-comment data -> cp-comment entity query
  -> cp-comment process -> cp-comment mutation
  -> cp-comment view -> shared Table
```

## 공용화 수준
- Comment 페이지 내부 적용으로 제한한다.
- 기존 Proposal/Vote/Discussion 패턴은 참조하지만 신규 공용 추상화는 만들지 않는다.
