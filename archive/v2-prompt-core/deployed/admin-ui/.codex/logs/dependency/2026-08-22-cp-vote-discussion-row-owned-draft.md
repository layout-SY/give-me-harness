# Vote·Discussion row-owned draft 의존성 결정

## 결정
- 상태 draft 소유권은 기존 `useStatusTransition.resetKey`를 재사용한다.
- 공개 기준 draft 소유권은 각 page process hook의 로컬 value state로 유지한다.
- controller·View·entity·shared UI 계약은 변경하지 않는다.

## 의존 방향
```text
Vote/Discussion controller
  -> list process
     -> cp-status-transition feature
     -> entity process mutation
  -> list view
     -> shared Dropdown / Button
```

## 공용화 수준
- 각 도메인 process 내부에 제한한다.
- 세 번째 동일 소비자가 등장하고 차이 없는 계약이 확인되기 전에는 공용 row-owned draft abstraction을 만들지 않는다.
