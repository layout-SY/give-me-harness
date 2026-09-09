# 평가 로그 — 장기 개선 사항

이번 변경의 통과 판정과 별개로, 이후 작업에서 다룰 만한 항목이다.

## 1. 예약 상태 계약의 소유 계층

`ReservationStatus` 6종은 여전히 UI(`ui/parts/reservationStatus.ts`)가 소유한다. `model/reservation.ts`의 `MEETING_RESERVATION_STATUS`는 4종(`REJECTED`, `COMPLETED` 없음)뿐이라 두 정의가 어긋나 있다. 서버 계약이 확정되면 유니온은 model로 옮기고 UI는 tone·label 맵만 유지하는 것이 맞다.

## 2. 목록 페이지 테스트 부재

`MeetingReservationListPage`와 `ReservationCard`에는 테스트가 없다. 이번에 상태 맵을 추출하면서 카드 표시가 회귀했는지 자동으로 확인할 수단이 없었고, 빌드·타입 검사와 수동 확인에 의존했다. 목록 카드 표시 테스트를 추가하면 상태 계약 이전(1번) 작업의 안전망이 된다.

## 3. `citizen-participation` MSW 실패 6건

`npm run test`가 이미 빨간 상태라 새 변경의 회귀 여부를 전체 실행 결과만으로는 판단할 수 없다. MSW `onUnhandledRequest: "error"` 전략과 최신 버전의 bypass 동작 충돌로 보이며, 별도 Logic 작업으로 정리해야 테스트 신호가 회복된다.

## 4. 참여 코드 복사 피드백

UI는 `onCopyInviteCode`만 호출하고 결과 표시가 없다. 복사 성공·실패 문구를 어디가 소유할지(호출부 토스트 vs. 상세 props) 정하지 않으면 화면마다 다르게 구현될 수 있다.

## 5. 화면 정의 근거 문서 부재

`docs/`에 STEP06 화면정의서가 없어 필드 구성을 인접 구현에서 역추론했다. Figma 채널이 세션마다 바뀌는 구조라, 확정된 항목 순서·라벨을 저장소 문서로 남겨 두면 다음 세션이 다시 추론하지 않아도 된다.
