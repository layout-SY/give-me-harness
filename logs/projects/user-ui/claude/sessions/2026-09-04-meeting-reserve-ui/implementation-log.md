# Implementation Log

## Task Summary
화면정의서 STEP02(회의 예약 모바일 폼)과 STEP03(예약 신청 완료 팝업)을 `src/features/meeting-reservation` 신규 슬라이스로 구현하고 `/meeting/reserve` 라우트를 최소 연결했다. 모든 컴포넌트는 controlled props + 선택적 callback으로만 동작하며 API·검증 로직을 포함하지 않는다.

## Reused Assets
- `~/shared/ui/button/button` — 예약 신청 CTA, 검색·추가, 팝업 확인
- `~/shared/ui/text-input/text-input` — 팀/기업명, 회의명, 닉네임 검색
- `~/shared/ui/text-area/text-area` — Agenda
- `~/shared/ui/dropdown/dropdown` — 테마 / 예약 날짜 / 시간 슬롯
- `~/shared/ui/popup` — 예약 완료 팝업 컨테이너
- `~/shared/assets/icons/chevron-left.icon`, `check.icon`
- 구조·토큰 규칙: `src/features/citizen-participation/ui/layout/citizen-layout.css`, `parts/citizen-form.css`, `DESIGN.md`

## New Files / Updated Files
신규
- `src/features/meeting-reservation/model/types.ts`
- `src/features/meeting-reservation/ui/MeetingReservePage.tsx`
- `src/features/meeting-reservation/ui/ReserveCompletePopup.tsx`
- `src/features/meeting-reservation/ui/layout/ReservationScreen.tsx`
- `src/features/meeting-reservation/ui/layout/ReservationHeader.tsx`
- `src/features/meeting-reservation/ui/layout/BottomActionBar.tsx`
- `src/features/meeting-reservation/ui/layout/meeting-reservation.css`
- `src/features/meeting-reservation/ui/parts/ReservationField.tsx`
- `src/features/meeting-reservation/ui/parts/SegmentedChoice.tsx`
- `src/features/meeting-reservation/ui/parts/ParticipantPicker.tsx`
- `src/features/meeting-reservation/ui/parts/NoticeBox.tsx`
- `src/features/meeting-reservation/ui/parts/meeting-reservation-parts.css`
- `src/features/meeting-reservation/ui/MeetingReservePage.test.tsx`
- `src/features/meeting-reservation/ui/ReserveCompletePopup.test.tsx`
- `src/features/meeting-reservation/index.ts`
- `src/pages/meeting-reservation/ui/MeetingReserveRoute.tsx`
- `src/pages/meeting-reservation/index.ts`
- `src/shared/config/meetingReservationRoutes.ts`

수정
- `src/app/routing.ts` — `meetingReservationRoutes.reserve`(`/meeting/reserve`)를 보호 라우트에 추가

## Key Logic
- `MeetingReservePage` props 계약: `values`, `errors`, `themeOptions`, `dateOptions`, `timeSlotOptions`, `participantQuery`, `participantCandidate`, `participantMessage`, `selectedParticipants`, `isSearchingParticipant`, `isSubmitting` / `onChange(field, value)`(제네릭 필드 타입), `onParticipantQueryChange`, `onSearchParticipant`, `onAddParticipant`, `onRemoveParticipant`, `onSubmit`, `onBack`. 모든 prop이 optional이며 기본값이 있어 단독 렌더가 가능하다.
- `ReserveCompletePopup` props 계약: `open`, `statusLabel`(기본 `"승인대기"`), `close`, `onConfirm`.
- `shared/ui/dropdown`이 index 기반 API이므로 페이지에서 `findIndex`/`findLabel`로 value↔index를 변환한다. `exactOptionalPropertyTypes: true` 때문에 라벨은 지역 상수로 좁힌 뒤 조건부 스프레드로 전달한다.
- 접근성: 세그먼트는 `role="radiogroup"`/`role="radio"` + roving `tabIndex`, Select·세그먼트·참여자 선택처럼 라벨을 직접 연결할 수 없는 컨트롤은 `ReservationField control="group"`이 `aria-labelledby`로 묶는다. 오류는 `role="alert"` + `aria-describedby`, 팝업은 `aria-labelledby="reserve-complete-title"`, 뒤로가기는 `aria-label="이전 화면으로"`.
- 스타일: `DESIGN.md` 계약대로 뷰포트 분기를 추가하지 않고 고정 모바일 셸(`--app-mobile-max`)만 사용한다. 새 전역 색 토큰 없이 tint는 `color-mix(in srgb, var(--accent) 6~7%, var(--surface))`로 파생했다. `prefers-reduced-motion`에서 트랜지션을 끈다.
- 화면정의서에 없는 유일한 추가: 지정 참여자 칩의 제외 버튼(`aria-label="{닉네임} 제외"`). 잘못 추가한 참여자를 되돌릴 수단이 화면정의서에 없어 최소 크기로 넣었고 사용자 확인 대상이다.
- `src/pages/meeting-reservation/ui/MeetingReserveRoute.tsx`는 TEMPORARY 미리보기 연결이다. 옵션 목록과 참여자 검색은 화면 확인용 표시 상태이며 Logic 역할이 hook·API로 교체한다.

## Validation / Request Handling
- `npx vitest run src/features/meeting-reservation` → 2 files / 7 tests 통과
- `npm run build` (`tsc -b && vite build`) → 통과
- `npm run lint` → 통과 (초기 `@typescript-eslint/no-misused-promises` 1건은 `void navigate(-1)`로 수정)
- `npm run test` → 500 passed / 6 failed. 실패는 모두 `src/features/citizen-participation`의 투표 API·MSW 테스트로, 이번 변경 파일과 import 연결이 없다(grep으로 `app/routing`·`meeting-reservation` 참조 없음 확인). 기준 브랜치에서의 재현은 확인하지 않았다.

## Risks
- 실패 6건이 이번 변경 이전부터 존재했는지 `sy-main` 체크아웃으로 직접 확인하지 않았다. 사용자 전용 Git 명령이 필요해 확인을 양도한다.
- 개인/팀/기업 이용유형에 따른 "팀/기업명" 필드의 조건부 표시 여부는 화면정의서에 없어 항상 표시로 구현했다.
- `--app-mobile-max`(480px)보다 팝업 기본 폭이 넓게 정의되어 있으나(`min(600px, calc(100% - 2rem))`) 셸 폭이 상한이라 실제로는 셸 안에서 렌더된다.

## Handoff Note
- Ready for watcher review
