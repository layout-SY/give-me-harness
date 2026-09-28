# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부 — 아래는 주 에이전트의 검토 질문과 코드·실행 근거에 따른 답변이다. 사용자에게 아래 질문을 모두 직접 물었다는 의미는 아니다.
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부 — 확인할 동작과 제약을 먼저 묻고 관찰 결과 및 권고를 분리했다.
- 명세 부재 상황의 구현 기준은 사용자가 지정한 UI handoff의 추정 요청·응답이다.
- 실제 서버 계약으로 추정값을 오인하지 않도록 DTO·기록에 추정 계약임을 표시했다.

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 계약 근거 | 서버 명세가 없는 상황에서 무엇을 기준으로 구현하는가? | UI handoff의 추정 요청·응답을 사용한다 | 사용자의 명시 지시, 최신 UI handoff DTO 표 | 추정 계약임을 표시하고 서버 명세가 확정되면 대조한다 |
| 상태 소유권 | 취소 버튼을 본 뒤 시간이 지나면 어떻게 되는가? | 최종 요청에서 권한·상태·T-5를 재검증하고 실패 시 최신 상태를 다시 조회한다 | mocks/handlers.ts, useMeetingReservationDetail.ts, reservationRead.test.ts의 경계 검증 | 표시용 cancelable만 신뢰하지 않고 요청 시 재검증한다 |
| 응답 해석 | 알림 실패가 취소를 되돌리는가? | participantNotified=false여도 취소 성공으로 처리한다 | UI handoff STEP08, reservationRead.test.ts의 알림 실패 응답 검사 | 취소 상태와 알림 결과를 분리한다 |
| 데이터 갱신 | 취소·신청이 다른 화면에 언제 반영되는가? | 저장소 갱신 후 목록·상세·슬롯 query를 무효화한다 | 신청·취소 hook, Axios→MSW 생성·조회·취소 테스트 | 같은 예약 저장소를 사용하고 관련 캐시를 갱신한다 |
| 제한 처리 | 폼 진입 후 새 제한이 생기면 어떻게 되는가? | 제출의 RESERVATION_RESTRICTED 응답에서 제한을 재조회하고 gate를 표시한다 | useMeetingReservationRestriction.test.tsx의 2개 테스트 | 제한 실패와 일반 제출 실패의 흐름을 구분한다 |
| 시간 재현 | 날짜가 바뀌면 mock이 유효한가? | 기본 fixture는 실행 시각 기준이며 테스트는 now 함수를 주입한다 | mocks/fixtures.ts, reservationRead.test.ts | 고정 과거 날짜를 제거하고 마감 경계를 시각 주입으로 확인한다 |
| 검증 한계 | 전체 테스트는 모두 통과했는가? | 예약 72개는 통과했고 전체 565개 통과·기존 시민참여 6개 실패다 | 최종 npm run test 실행 결과, 구현 로그 | 범위 통과와 저장소 전체 실패를 함께 보고한다 |

## 결론

승인된 추정 계약의 기능은 예약 테스트 72개로 확인했고, 최종 lint와 TypeScript·Vite 빌드도 통과했다. 실제 서버 계약 대조와 별도 Git 통합은 아직 수행하지 않았다.
