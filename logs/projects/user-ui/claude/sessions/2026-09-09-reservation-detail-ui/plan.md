# 계획 — STEP06 예약 상세 모바일 UI

- 세션 역할: ui (inject role)
- 브랜치: `task/reservation-detail-ui` (분기 기준 `sy-main`, Git 통합 담당 claude)
- 승인: 사용자 "진행해" (2026-09-09)

## 범위

1. `ui/parts/reservationStatus.ts` — 예약 상태 6종 유니온과 tone·label 맵을 `ReservationCard`에서 추출해 목록·상세가 공유한다.
2. `ui/parts/ReservationDetailSection.tsx` — 제목 + `<dl>` 구조의 표시 전용 파츠.
3. `ui/MeetingReservationDetailPage.tsx` — controlled 상세 화면.
4. `ui/parts/meeting-reservation-parts.css` — `.vo-detail*` 스타일 추가.
5. `index.ts` — 상세 페이지와 `ReservationStatus` 타입 export.
6. `ui/MeetingReservationDetailPage.test.tsx` — 표시·분기·콜백 테스트.

## 역할 경계

취소 권한 판정, 승인만료 상태 전이, 참여 코드 발급은 Logic 경계다. UI는 `canCancel: boolean`과 이미 가공된 표시 문자열만 props로 받고, 사용자 조작은 `onCancel`·`onCopyInviteCode`·`onBack` 콜백으로 위임한다.

## 제약

- DESIGN.md 고정 480px 셸 — 뷰포트 미디어 쿼리 추가 금지, 신규 색 토큰 금지.
- Figma node `10:3828`의 채널이 만료되어 이번 세션에서는 디자인을 직접 읽지 못했다. 기존 예약 폼·목록 카드의 필드 구성을 기준으로 구현했고, 채널을 다시 받으면 항목 순서·라벨·하단 버튼 구성을 대조해야 한다.

## 검증

`npm run test`, `npm run lint`, `npm run build`.
