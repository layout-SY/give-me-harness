# Grill Me 리뷰

## 사용자 요청

- 요청 요약: shared 공용 리소스는 후순위로 두고 CP 도메인별 책임 분리를 순차 진행한다.
- 승인된 현재 범위: Discussion 목록·상세와 Vote 목록 완료 후 Vote 상세 한 섹션

## Method Guardrails

- neutral question-first 적용 여부: 예
- 결론 도출 순서: 질문 → 분기 → 답변 → 리스크
- 기능·시각 변경을 리팩터링에 섞지 않았는가: 예

## 의사결정 트리

| 의사결정 | 현재 가정 | 근거 | 리스크 | 권장안 |
| --- | --- | --- | --- | --- |
| 공용 controller를 만들 것인가 | Discussion과 Proposal이 유사하다 | 소비자별 query·process 불변식이 다름 | generic 계약 팽창 | 도메인 전용 유지 |
| 하나의 controller hook만 만들 것인가 | 파일 수를 줄일 수 있다 | query/search/process가 독립 lifecycle을 가짐 | controller 재비대화 | data/search/process 분리 후 controller 조합 |
| DOM ref를 controller에 노출할 것인가 | 기간 invalid 검사에 필요하다 | React refs lint가 controller 객체 접근을 차단 | render 계약 오염 | view 이벤트에서 boolean만 전달 |
| fixture/shared도 함께 정리할 것인가 | 전체 구조가 더 균일해진다 | 사용자 명시적 deferred 범위 | 범위 확장 | 현재 섹션에서 제외 |
| 상세도 목록과 같은 수의 hook으로 나눌 것인가 | 구조 모양을 통일할 수 있다 | 상세에는 검색·선택 lifecycle이 없음 | 단일 사용 계층과 파일 증가 | controller/process/model/view만 사용 |
| detail 도착 시 effect로 종료일을 복사할 것인가 | state 초기화가 직관적이다 | effect 동기화는 추가 render와 stale 전환 가능성 발생 | route/detail 전환 시 이전 값 노출 | detail ID 기반 selection으로 현재 값을 계산 |
| 종료일 validation과 payload를 hook에 둘 것인가 | 파일 수를 줄일 수 있다 | React와 무관한 순수 도메인 규칙 | mutation lifecycle과 규칙 변경 이유 결합 | 순수 model 함수로 분리 |
| Discussion 검색 validation을 Vote에 복제할 것인가 | query shape가 유사하다 | Vote는 기존 `DateRangeField` native invalid/form 차단만 사용 | 새 오류 문구·state로 observable 변경 | Vote 기존 submit 계약 유지 |
| Discussion·Vote process를 공용화할 것인가 | status/disclosure UI가 유사하다 | ID·status·DTO·dialog·disclosure vocabulary가 다름 | generic parameter와 domain leak 증가 | Vote 전용 process 유지 |
| Vote invalid 종료일에 Discussion 오류 UI를 추가할 것인가 | 접근성 피드백을 강화할 수 있다 | 사용자 승인 범위는 observable 보존이며 기존 Vote에는 문구·오류 ARIA가 없음 | 구조 리팩터링에 기능 변경 혼입 | 저장 비활성화만 유지 |
| Vote 상세 status 계약을 string으로 노출할 것인가 | shared Select callback과 맞추기 쉽다 | process와 DTO의 closed vocabulary는 `CpVoteStatus` | 타입 경계에서 invalid status 허용 | 저장 상태 계약은 `CpVoteStatus \| null` 유지 |

## Neutral Question Flow

| QID | 중립 질문 | 분기 | 답변 | 근거 | Recommended Answer |
| --- | --- | --- | --- | --- | --- |
| Q1 | 기존 observable을 바꾸지 않고 책임만 이동할 수 있는가? | 예 | 기존 query/mutation/JSX를 그대로 재사용했다. | build 및 브라우저 흐름 | 기능 보존형 분리를 유지한다. |
| Q2 | 공용 추상화가 현재 필요하다고 입증됐는가? | 아니오 | 두 도메인의 계약이 아직 동일하다고 증명되지 않았다. | abstraction strategy | Discussion 전용 경계를 유지한다. |
| Q3 | invalid 검색이 선택 상태를 초기화해야 하는가? | 아니오 | 기존 코드는 validation return 뒤 reset을 실행하지 않았다. | 이전 page handler | 기존 validation return 순서를 보존한다. |
| Q4 | 현재 Closure 가능한가? | 아니오 | Watcher `confirmed`가 없다. | pipeline rules | `paused_after_generator`로 보류한다. |
| Q5 | detail이 비동기로 도착해도 종료일 입력이 최신 detail과 일치하는가? | 예 | `{ detailId, value }`가 현재 detail ID와 일치할 때만 draft를 사용한다. | process hook과 브라우저 detail 조회 | effect 없이 server `periodTo`를 기본값으로 사용한다. |
| Q6 | status만 바꿀 때 종료일이 payload에 포함되는가? | 아니오 | 기존 값과 같은 normalized 종료일은 `undefined`로 매핑된다. | 브라우저 POST body `{"status":"CLOSED"}` | 조건부 DTO mapping을 유지한다. |
| Q7 | 잘못된 종료일이 mutation 경계까지 도달하는가? | 아니오 | alert·ARIA invalid·button disabled·save guard가 함께 적용된다. | 실제 브라우저 invalid flow | view와 process의 이중 guard를 유지한다. |
| Q8 | Vote 검색 submit/reset/page 전환이 selection을 초기화하는가? | 예 | controller가 search 변경 직후 process reset을 호출한다. | VT-011 page fallback 브라우저 검증 | 기존 reset 순서를 유지한다. |
| Q9 | placeholder data에서 이전 row를 조작할 수 있는가? | 아니오 | `isCurrentData`가 false이면 selected row와 onRowClick을 노출하지 않고 save도 guard한다. | data/process/controller 계약 | stale row 조작 금지를 유지한다. |
| Q10 | status-only 저장에 다른 필드가 섞이는가? | 아니오 | 변경 없는 disclosure는 `undefined`이며 실제 POST body는 `{"status":"COMPLETED"}`다. | browser network request | 조건부 Vote DTO mapping을 유지한다. |
| Q11 | 역전 기간에서 새 page validation이 추가됐는가? | 아니오 | 기존 DateRangeField native invalid와 form submit 차단만 동작한다. | 브라우저 invalid DOM과 추가 GET 0건 | Discussion 오류 state를 복제하지 않는다. |
| Q12 | Vote 상세 invalid 종료일에서 새 오류 문구나 ARIA가 추가됐는가? | 아니오 | 입력은 유지되고 저장만 disabled이며 오류 text·ARIA count는 0이다. | VT-001 실제 브라우저 DOM | 기존 Vote observable을 유지한다. |
| Q13 | Vote 상세 status-only 저장에 종료일이 섞이는가? | 아니오 | normalized 종료일이 기존값이면 payload에서 생략된다. | 실제 POST body `{"status":"COMPLETED"}` | 조건부 DTO mapping을 유지한다. |
| Q14 | route detail이 바뀌면 이전 종료일 draft가 노출되는가? | 아니오 | 현재 detail ID와 selection ID가 일치할 때만 draft를 사용한다. | process 계약과 `resetKey` | keyed remount와 동등한 reset을 유지한다. |
| Q15 | 현재 Closure 가능한가? | 아니오 | 최종 Oracle은 PASS지만 Watcher `confirmed`가 없다. | pipeline rules | `paused_after_generator`로 보류한다. |

## 코드베이스로 해결된 질문

| 질문 | 근거 | 답변 |
| --- | --- | --- |
| 기준 구조는 무엇인가 | Proposal 목록 page/controller/view | 동일한 도메인 전용 구조 사용 |
| query/mutation을 이동해야 하는가 | entity hooks의 책임이 이미 명확함 | 호출 위치만 data/process hook으로 이동 |
| UI를 다시 설계해야 하는가 | 사용자 요구가 책임 분리임 | JSX·CSS·문자열 유지 |
| 상세 query를 새 hook으로 감쌀 것인가 | entity detail query가 이미 cache/parser/refetch 계약을 소유함 | controller에서 기존 hook을 직접 조합 |
| process payload shape를 바꿀 것인가 | entity mutation DTO와 API 계약이 이미 존재함 | 기존 optional status/closedAt shape 유지 |
| Vote config를 수정해야 하는가 | columns/filter/disclosure vocabulary가 이미 분리됨 | 기존 config를 그대로 재사용 |
| Table keyboard 처리를 controller로 옮겨야 하는가 | Table이 Enter/Space와 aria-selected를 이미 소유함 | view에서 기존 Table callback 계약만 전달 |
| Vote 상세 결과 UI를 Discussion과 공용화해야 하는가 | Vote는 2분할·choices·stance 없는 의견이고 Discussion은 3분할·stance가 있음 | 기존 shared primitives만 재사용하고 domain view는 분리 |

## 사용자에게 확인할 질문

- 없음. 현재 섹션의 승인 범위와 보류 범위가 명확하다.

## 통과/실패 영향

- 차단 이슈: Watcher 비가용
- 비차단 리스크: 기존 반응형 shared navigation·TimelineList 음절 분리, test script 부재
- 최종 권고: local verification 결과를 보존하고 `paused_after_generator`로 대기
