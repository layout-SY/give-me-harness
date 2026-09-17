# Query 캐시와 명령형 요청

## 조회

- TanStack Query가 있는 서버 데이터 조회는 도메인 query hook / query options에 로딩·오류·취소·캐시를 맡긴다. Query 바깥에서 동일 데이터의 loading state를 추가하거나 `useApi`로 감싸지 않는다.
- query key에는 실제 결과를 바꾸는 ID·filter·search·sort·page를 모두 넣는다. 정규화된 요청 값과 key 값이 일치해야 한다. `enabled`로 선택 전 ID를 제어하고, 존재하지 않는 ID를 기본값으로 만들어 요청하지 않는다.
- `queryFn`의 signal을 전송까지 전달하고 실패 ApiResult는 throw한다. retry·staleTime·gcTime·focus refetch는 앱 정책과 데이터 수명에 맞춘다. 두 앱의 숫자가 다르다는 이유만으로 통일하지 않는다.
- 오류 표시는 앱의 QueryCache / MutationCache reporter와 meta 정책을 확인한다. page·hook·전역 reporter가 같은 오류를 중복 표시하지 않도록 책임을 정한다.

## mutation별 캐시 결정

| 변경      | 최소 영향 범위               | 처리 기준                                                                            |
| --------- | ---------------------------- | ------------------------------------------------------------------------------------ |
| 생성      | 목록, 집계, 필요하면 최신 ID | 생성 응답만으로 모든 필터 목록을 정확히 갱신할 수 없으면 invalidate                  |
| 수정      | 해당 상세, 영향받는 목록     | 완전한 상세 응답이면 setQueryData, 부분 응답이면 병합 규칙 또는 invalidate           |
| 삭제      | 해당 상세 제거, 목록·집계    | 삭제 상세의 진행 중 조회를 취소한 뒤 removeQueries; 목록 invalidate                  |
| 관계 변경 | 양쪽 관계를 보여주는 key     | category 이름 변경 → item 목록, video 변경 → playlist 상세처럼 실제 의존성 근거 명시 |

`setQueryData` 전에 같은 key의 오래된 조회가 진행 중인지 확인한다. 캐시를 직접 덮어쓰는 변경은 `await cancelQueries(영향 key) → setQueryData / removeQueries → invalidateQueries(필요 범위)` 순서를 사용한다. signal을 소비하지 않는 전송도 함께 점검한다. 모든 mutation을 전역 `invalidateQueries()`로 처리하지 않는다.

낙관적 갱신은 `onMutate`에서 관련 조회 취소·snapshot·patch, `onError`에서 rollback, `onSettled`에서 재검증한다. 이전 mutation의 rollback이 새 mutation을 덮지 않는지도 확인한다. 서버 응답 이후의 확정 갱신을 낙관적 갱신이라고 부르지 않는다.

추출한 query/mutation options는 hook과 계약 테스트가 같은 정의를 사용하게 할 때 유용하다. 반복이 없는 작은 hook에 파일 개수를 맞추기 위한 options 계층을 강제하지 않는다.

## useApi: 최신 호출 우선

서버 캐시보다 명령·화면 lifecycle 조정이 중심인 기존 소비처에서 사용한다. user-ui의 동시 호출 정책은 admin-ui의 다음 방향을 따른다.

1. 한 hook 인스턴스에서 호출마다 sequence를 증가시킨다.
2. 최신 호출만 성공 콜백·오류 보고·반환 결과에 반영한다. 늦은 이전 성공과 실패는 취소로 취급한다.
3. **최신 호출이 끝나면 loading을 종료한다.** 이전 호출이 아직 남아 있어도 기다리지 않는다. 이전 호출의 finally는 최신 호출의 loading을 종료하지 않는다.
4. unmount에서 보관한 controller를 모두 abort하고, 해제 이후 상태 갱신과 콜백을 막는다.

| 항목             | user-ui                          | admin-ui 기존 계약                                                     |
| ---------------- | -------------------------------- | ---------------------------------------------------------------------- |
| 정상 결과        | `{ status: "completed", value }` | ApiResult 또는 원시 값                                                 |
| throw 실패       | `{ status: "failed", error }`    | undefined                                                              |
| 이전 결과 / 취소 | `{ status: "canceled" }`         | 이전 ApiResult는 `{ canceled: true }`; 원시 값·throw·abort는 undefined |

동시 요청 정책을 맞추기 위해 앱의 공개 반환 타입·오류 표시 기본값을 함께 변경하지 않는다. 이 정책은 이전 HTTP 작업을 즉시 중단하거나 서버 mutation을 되돌리는 기능이 아니다. 모든 결과가 필요한 독립 명령은 hook 인스턴스나 도메인 orchestration을 분리한다. 하나의 execute 내부에서 Promise.all로 묶을 경우에도 각 실패·취소 의미를 먼저 정의한다.

최신 응답 판정은 debounce와 목적이 다르다. 검색 요청량을 줄이는 debounce는 별도로 선택할 수 있다. 검증에는 이전/최신 요청의 두 완료 순서, 이전 업무 실패·throw 억제, 최신 실패 시 loading 종료, unmount 취소를 포함한다.
