# Handoff

이 세션은 `owner` assignment로 필수 8종 산출물을 작성했다. 완료 근거는 `final-summary.md`와 `review-log.md`를 본다. 이 문서는 **Logic 역할 인계 계약**을 정리한다.

## From
- Claude Code, inject `--role ui`, 2026-09-04, branch `task/meeting-reserve-ui` (parent `sy-main@d0b462904a48`)

## To
- `next_role`: logic — 예약 API·검증·옵션 지연 로딩 구현 (제안이며 권한 부여가 아니다. 인계자는 현재 사용자 요청과 저장소 상태를 다시 확인한다.)

## Current Status
- `requested_roles`: ui / `confirmed_roles`: ui / `completed_roles`: ui
- UI 구현·검증·문서화 완료. merge 미승인.
- 미해결: 전역 팝업 폭(A)과 드롭다운 어댑터 확장(B)은 `src/shared/ui`가 현재 branch scope 밖이라 별도 계약이 필요하다.

## What Was Done
- 화면정의서 STEP02·STEP03을 `src/features/meeting-reservation` 신규 슬라이스로 구현 (커밋 `bd3c35a`)
- `/meeting/reserve` 최소 라우트 연결
- 이용유형별 소속명 필드 분기 추가: `personal`은 필드 자체를 렌더하지 않고, `team`은 "팀명", `company`는 "기업명" 라벨을 쓴다
- 상세: `implementation-log.md`

## Logic 역할 인계 계약

### 1. 옵션 지연 로딩 (사용자 요구, 2026-09-04)
사용자 요구: "사용자가 해당 입력폼에 입력을 원할 때(select라면 select 목록이 뜰 때, 1시간 슬롯인 경우 슬롯들이 나타날 때) API 요청으로 현재 사용 가능한 데이터들이 뜨게끔 할 것."

- 대상 필드: `테마`, `예약 날짜`, `1시간 시간 슬롯`, `지정 참여자`(닉네임 검색)
- 현재 제약: `src/shared/ui/dropdown/dropdown.tsx`가 HeroUI `Select`를 감싸면서 **열림 이벤트를 노출하지 않는다**(`onOpenChange` 없음). 따라서 feature에서 "목록이 열리는 시점"을 알 수 없고, 지금은 목록을 props로 미리 받는 구조다.
- 필요한 선행 변경(B): 어댑터에 `onOpenChange?: (isOpen: boolean) => void`, `isLoading?: boolean`, `emptyLabel?: string`을 추가한다. `src/shared/ui`는 현재 branch scope 밖이므로 scope를 포함한 별도 branch 계약과 승인이 필요하다.
- 그 다음 `MeetingReservePage`에 추가할 props 계약(C):
  - `onThemeOptionsOpen?: () => void`
  - `onDateOptionsOpen?: () => void`
  - `onTimeSlotOptionsOpen?: () => void`
  - `loadingFields?: readonly ("theme" | "reservationDate" | "timeSlot")[]`
  - 빈 목록 문구(예: "선택 가능한 시간 슬롯이 없습니다.")
- 슬롯 목록은 **예약 날짜에 의존**한다. 날짜가 바뀌면 이전 슬롯 목록과 선택값을 무효화해야 한다. 이 무효화는 UI가 아니라 hook·query 계층의 책임이다.
- 시간 슬롯 목록에 이미 점유된 슬롯이 포함되는지, 아니면 서버가 가용 슬롯만 내려주는지 API 계약에서 확정해야 한다. 전자라면 `ReservationOption`에 `disabled` 필드 추가가 필요하다.
- 지정 참여자 검색은 현재 `검색` 버튼 클릭만 트리거다. 입력 중 자동 조회가 필요하면 디바운스와 요청 취소는 hook에서 처리한다.

### 2. 이용유형 분기의 데이터 책임
- UI는 `usageType === "personal"`일 때 소속명 필드를 렌더하지 않는다.
- `organizationName` 값의 초기화와 검증 제외는 **Logic 책임**이다. 유형을 팀→개인으로 바꾼 뒤 제출하면 이전 입력값이 남은 채 전송될 수 있다.
- 개인 이용 시 지정 참여자 허용 여부, 최대 인원(이용안내의 10명)이 유형별로 다른지는 미확정이다.

### 3. TEMPORARY 미리보기 코드 교체
`src/pages/meeting-reservation/ui/MeetingReserveRoute.tsx`의 `THEME_OPTIONS`, `DATE_OPTIONS`, `TIME_SLOT_OPTIONS`(현재 13:00~16:00 3건), `PARTICIPANT_SAMPLES`와 `useState` 5개는 화면 확인용이다. 실제 API·hook으로 교체하지 않으면 하드코딩 목록이 운영에 노출된다.

### 4. 검증 계약 (화면정의서 "이용안내" 기준)
- 1회 1시간, 최대 10명, 회의 시작 5분 전까지 신규 신청 가능
- 필수 항목: 이용유형, 소속명(개인 제외), 테마, 예약 날짜, 시간 슬롯, 회의명
- 제출 성공 시 `ReserveCompletePopup`을 열고 `statusLabel`에 서버 상태를 전달한다(기본 `"승인대기"`).

## What Must Be Done Next
1. 사용자 확인: 지정 참여자 칩의 "제외" 버튼 유지 여부(화면정의서에 없는 추가 요소)
2. 사용자 확인: `npm run test`의 기존 실패 6건이 `sy-main`에서도 재현되는지
3. `src/shared/ui/popup`·`src/shared/ui/dropdown`를 포함한 branch 계약 승인 후 A(팝업 폭)·B(어댑터 확장)·C(지연 로딩 props) 처리
4. merge 승인 → `finish-proposal` → `finish` / `verify` / `close`
5. Logic 역할: 위 인계 계약 구현

## Constraints
- `DESIGN.md` 고정 모바일 셸 계약: 뷰포트 분기 금지, 새 색 토큰은 문서 기록 후 사용
- 전역 `dialog.custom-popup`이 `width: min(600px, …)`이라 480px 셸을 벗어난다(`src/shared/ui/popup/popup.css:2`). 예약 팝업만 우회 수정하지 않고 전역에서 고치는 것을 권한다.
- `@heroui/react` 직접 import는 `src/shared/ui` 어댑터 내부에서만
- UI 파일에 API 호출·파싱·도메인 상태 전이를 두지 않는다

## Relevant Files / Skills
- `src/features/meeting-reservation/**`, `src/pages/meeting-reservation/**`, `src/shared/config/meetingReservationRoutes.ts`, `src/app/routing.ts`
- `src/shared/ui/dropdown/dropdown.tsx`, `src/shared/ui/popup/popup.css` (변경 필요, 현재 scope 밖)
- `docs/design/가상오피스/가상오피스/` (화면정의서 17종, STEP04~STEP24 미구현)
- `DESIGN.md`, `docs/meeting-api-contract.md`
- 스킬: `policy/task-role-routing`, `policy/git-branch-strategy`, `policy/documentation`
