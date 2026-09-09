# 최종 요약 — STEP06 예약 상세 모바일 UI

## 결과

예약 상세 화면을 controlled 컴포넌트로 신규 구현하고, 목록 카드가 갖고 있던 예약 상태 표시 계약을 공용 모듈로 분리했다.

- 신규: `parts/reservationStatus.ts`, `parts/ReservationDetailSection.tsx`, `ui/MeetingReservationDetailPage.tsx`, `ui/MeetingReservationDetailPage.test.tsx`
- 수정: `parts/ReservationCard.tsx`, `parts/meeting-reservation-parts.css`, `index.ts`

## 화면 구조

`ReservationScreen`
→ `ReservationHeader`(제목 "예약 상세", `onBack`이 있을 때만 뒤로가기)
→ 오류 `role="alert"` / 로딩 `Loading` / 본문 중 하나
→ 본문: 상태 배지 + 회의명 → `NoticeBox`(선택) → "예약 정보" `<dl>` → "회의 정보" `<dl>` → "참여 코드"(선택)
→ `canCancel`일 때만 `BottomActionBar`의 "예약 취소"(danger)

## 후속 Logic 계약

| props | 기대 값 |
| --- | --- |
| `status`, `statusLabel?` | 서버 상태 코드와 표시 라벨 |
| `themeLabel`, `dateLabel`, `timeRangeLabel`, `usageTypeLabel`, `organizationLabel`, `reserverName`, `participantsLabel`, `agenda` | 이미 서식이 적용된 표시 문자열 |
| `inviteCode` | 발급된 경우에만 전달 |
| `noticeTitle`/`noticeDescription` | 반려 사유·승인만료 안내 등 |
| `canCancel`, `isCanceling` | 취소 가능 판정과 진행 상태 |
| `onCancel`, `onCopyInviteCode`, `onBack` | 실행 위임 |

## 검증

`npm run lint` 통과, `tsc -b`/`npm run build` 통과, feature 테스트 24 passed(신규 9 포함).
전체 `npm run test`는 533 passed / 6 failed이며 실패는 모두 이번 변경과 무관한 `citizen-participation` MSW 기존 실패다.

## 남은 일

- Figma `10:3828` 대조(채널 재연결 필요)
- 라우팅·데이터 연결(Logic 역할)
- evaluation-log의 5개 개선 항목
