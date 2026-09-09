# Evaluation Log

## Context
회의 예약 화면의 옵션 조회를 "미리 받은 목록"에서 "목록이 열릴 때 조회"로 바꾸기 위해, 공용 `Dropdown` 어댑터에 열림·로딩·빈 목록 계약을 추가하고 전역 팝업 폭을 셸 토큰에 맞춘 작업. 실제 조회는 Logic 역할로 남았다.

## Structural Risks
1. **어댑터 계약이 늘어나는 방향**
   `Dropdown`은 이제 `type`/`index` 기반 API에 `onOpenChange`/`isLoading`/`emptyLabel`이 더해져 props 8개가 됐다. 값이 아니라 인덱스로 선택을 표현하는 원래 설계 때문에 소비자마다 `findIndex`/`findLabel` 변환이 필요하고, 여기에 로딩 상태 배선이 겹친다. 예약 화면 15종이 같은 패턴을 복제하면 변환 코드가 화면 수만큼 늘어난다.

2. **로딩 상태의 소유 위치가 배열이다**
   `loadingFields: readonly ReservationOptionField[]`는 필드가 늘어날 때마다 유니온과 문구 매핑을 함께 고쳐야 한다. 예약 목록·상세 화면에서도 같은 형태가 필요해지면 화면마다 별도 유니온이 생긴다. 조회 상태를 필드 단위로 들고 다니는 대신 옵션 소스 자체를 `{ items, isLoading, reload }` 형태로 묶는 편이 확장에 강하다.

3. **미리보기 코드가 진짜처럼 자란다**
   직전 세션의 TEMPORARY 상수에 이번에 타이머·로딩 상태·무효화 분기가 더해졌다. 미리보기가 정교해질수록 교체 압력이 줄어드는 역방향 동기가 생긴다. Logic 인계 시 이 블록을 통째로 삭제하는 것을 전제로 유지해야 한다.

4. **요청 경합 처리가 계약에 없다**
   현재 계약은 "열리면 조회하라"까지만 말하고, 빠르게 여닫을 때의 중복 요청·늦은 응답 덮어쓰기를 다루지 않는다. UI가 관여할 문제는 아니지만, hook이 이를 처리하지 않으면 `isLoading`이 영원히 켜지거나 옛 목록이 표시되는 증상이 UI 버그로 보고될 수 있다.

5. **팝업 폭 변경의 검증 공백**
   전역 CSS 한 줄이 두 소비자에게 적용되지만 시각 확인은 하지 않았다. 스타일 회귀는 테스트로 잡히지 않는 유일한 변경 유형이다.

## Why This Matters
예약 흐름에는 화면 15종이 더 붙고, 그 대부분이 서버가 내려주는 옵션을 다룬다. 지금 정한 "열림 → 조회 → 로딩/빈 상태" 계약이 그대로 복제되므로, 어댑터 수준에서 값 기반 API와 옵션 소스 묶음을 정리하면 이후 화면이 자동으로 혜택을 받는다. 반대로 지금 형태를 그대로 두면 화면마다 인덱스 변환 + 로딩 배열 + 문구 상수 3종 세트가 반복된다.

## Improvement Options
1. `shared/ui/dropdown`에 value 기반 API(`value`/`onChange`)를 추가하고 기존 index API를 위임 구현으로 남긴다.
2. 예약 슬라이스에 `ReservationSelectField`를 두어 `findIndex`/`findLabel`/로딩/빈 문구 배선을 한 곳으로 모은다(사용처 4번째 시점).
3. 옵션 소스를 `{ items, isLoading, onOpen }` 한 덩어리로 넘기는 props 형태로 바꿔 `loadingFields` 배열을 없앤다.
4. Logic 인계 계약에 요청 취소·경합 규칙을 명시적으로 넣는다.

## Recommended Backlog
1. (중) 옵션 소스 묶음 props로 전환 — 예약 목록/상세 화면 착수 전
2. (중) `shared/ui/dropdown` value 기반 API — 사용처가 2곳 이상으로 늘기 전
3. (하) `ReservationSelectField` 추출 — 드롭다운 사용처 4번째
4. (하) 팝업 폭 변경의 시각 확인 — 사용자가 시각 QA를 요청할 때 함께

## Suggested Next Step
Logic 역할이 실제 조회 hook을 붙일 때 3번(옵션 소스 묶음)을 함께 정하면 UI 재작업이 한 번으로 끝난다. UI 단독으로 먼저 바꾸면 계약을 두 번 고치게 된다.
