# 구현 로그 — 예약 상세 UI

## 변경 파일

| 경로 | 변경 |
| --- | --- |
| `src/features/meeting-reservation/ui/parts/reservationStatus.ts` | 신규. `ReservationStatus` 유니온 6종, `RESERVATION_STATUS_TONE`, `RESERVATION_STATUS_LABEL`, `resolveReservationStatusLabel` |
| `src/features/meeting-reservation/ui/parts/ReservationCard.tsx` | 상태 정의 제거 후 `reservationStatus`를 import. `ReservationListStatus`는 `ReservationStatus` 별칭으로 re-export해 목록 import 경로를 유지 |
| `src/features/meeting-reservation/ui/parts/ReservationDetailSection.tsx` | 신규. `제목 + <dl>` 표시 파츠. 항목이 없으면 섹션을 렌더하지 않음 |
| `src/features/meeting-reservation/ui/MeetingReservationDetailPage.tsx` | 신규. controlled 상세 화면 |
| `src/features/meeting-reservation/ui/parts/meeting-reservation-parts.css` | `.vo-detail`, `.vo-detail-section`, `.vo-detail-list`, `.vo-detail__code` 규칙 추가 |
| `src/features/meeting-reservation/index.ts` | `MeetingReservationDetailPage`, `ReservationStatus` export |
| `src/features/meeting-reservation/ui/MeetingReservationDetailPage.test.tsx` | 신규. 9개 케이스 |

## props 계약

표시 문자열: `status`, `statusLabel?`, `meetingName?`, `usageTypeLabel?`, `organizationLabel?`, `themeLabel?`, `dateLabel?`, `timeRangeLabel?`, `reserverName?`, `participantsLabel?`, `agenda?`, `inviteCode?`, `noticeTitle?`, `noticeDescription?`
상태 플래그: `canCancel`, `isLoading`, `isCanceling`, `errorMessage?`
콜백: `onBack?`, `onCancel?`, `onCopyInviteCode?`

## 판단 근거

- 취소 가능 여부는 `canCancel` boolean만 받는다. 상태별 취소 규칙과 승인만료 전이는 Logic 소유.
- 빈 값 항목은 `<dl>` 줄 자체를 만들지 않고, 항목이 전부 비면 섹션 제목도 그리지 않는다.
- 로딩·오류 화면에서는 하단 고정 바를 만들지 않아 조작 불가 상태에서 버튼이 남지 않게 했다.
- 참여자·안건이 길어도 480px 셸을 넘지 않도록 `overflow-wrap: anywhere`, `white-space: pre-wrap`을 적용했다.
- `resolveReservationStatusLabel`은 공백뿐인 `statusLabel`도 기본 라벨로 대체한다. 기존 카드는 `??`만 썼으므로 공백 라벨 처리만 달라진다(배지가 `-`로 비던 사례가 기본 라벨로 표시됨).

## 검증

| 명령 | 결과 |
| --- | --- |
| `npx vitest run .../MeetingReservationDetailPage.test.tsx` | 9 passed |
| `npm run lint` | 통과 |
| `npm run test` | 533 passed / 6 failed — 실패는 모두 `citizen-participation`의 MSW `onUnhandledRequest` 관련 기존 실패이며 이번 변경과 무관 |
| `npm run build` | 통과 (tsc -b + vite build) |

## 2차 작업 — Figma 프레임 정렬 (사용자 승인: 프레임 기준, 충돌 시 DESIGN.md 우선)

Figma 채널 `hgkguilr`에 연결해 STEP02~STEP08 프레임을 읽고 상세 화면을 프레임 구조에 맞췄다.

### 구조 변경

| 항목 | 변경 |
| --- | --- |
| 헤더 | `ReservationHeader`("예약 상세" + 아이콘 뒤로가기) 제거 → `‹ 예약 목록` 텍스트 링크(`.vo-detail__back`) + 스크린리더용 `h1.vo-sr-only` |
| 메타 | 테마·예약일·이용시간을 `<dl>` 3줄에서 회의명 아래 한 줄(`캠핑 · 2026.09.03 · 14:00 ~ 15:00`)로 이동 |
| 예약 정보 섹션 | 이용유형 · 팀명/기업명 · Agenda로 재구성(프레임 03행) |
| 참여자 섹션 | `회의 정보` → `참여자`. 예약자 · 지정 참여자 · 참여 예정으로 재구성(04행) |
| 입장 코드 | `참여 코드` → `입장 코드`. 복사 버튼 제거(프레임에 없음), 발급 안내 문구와 입장 가능시간 안내 추가(05·06행) |
| 승인만료 | `승인만료 시 코드 없음 · No-show 없음 · 예약제한 없음` 문구 추가(08행) |

### props 계약 변경

- 추가: `attendanceLabel`(참여 예정 인원), `usageType`, `organizationName`
- 제거: `usageTypeLabel`, `organizationLabel`(→ `usageType`에서 UI가 라벨과 소속 용어를 파생), `onCopyInviteCode`, `themeLabel`/`dateLabel`/`timeRangeLabel`은 유지하되 메타 한 줄로 합쳐 표시
- 이용유형 라벨(개인·팀·기업)과 소속 용어(팀명·기업명)는 UI가 소유한다. 예약 폼의 `USAGE_TYPE_OPTIONS`와 같은 문구이며, 개인 이용은 소속 줄을 만들지 않는다(03행 "조건부 표시")

### DESIGN.md 우선 적용 지점

프레임 값과 DESIGN.md가 충돌한 곳은 DESIGN.md를 따랐다.

| 요소 | Figma | 적용값 | 근거 |
| --- | --- | --- | --- |
| 코드 도움말·입장 안내·승인만료 문구 | 11px | 12px | "본문에 14px 미만을 새로 도입하지 않는다. 기존 12px는 대비가 충분한 메타데이터에만" |
| 정의 목록 설명 | 13px | 14px | 본문 최소 크기 |
| 회의명 | 20px | 18px | DESIGN.md 크기 체계에 20px 본문 단계가 없고 기존 `.vo-complete__title`과 동일 단계 사용 |
| 색 | 프레임 고유값 | `--text-strong`/`--text`/`--text-muted` | 신규 색 토큰 금지 |

레이아웃도 고정 480px 셸을 유지했고 뷰포트 미디어 쿼리를 추가하지 않았다.

### 2차 검증

| 명령 | 결과 |
| --- | --- |
| `npx vitest run src/features/meeting-reservation/` | 45 passed (상세 14케이스로 재작성) |
| `npm run lint` | 통과 |
| `npm run build` | 통과 |

## 3차 작업 — 취소 확인·완료 팝업 (사용자 승인: 이어서 구현)

| 경로 | 내용 |
| --- | --- |
| `ui/ReservationCancelConfirmPopup.tsx` | 신규. STEP07. 제목·대상 회의·취소 조건 안내·`닫기`/`예약 취소` 2버튼 |
| `ui/ReservationCancelCompletePopup.tsx` | 신규. STEP08. 제목·대상 회의·상태 변경 안내·`확인` |
| `ui/parts/reservationMeta.ts` | 신규. `joinReservationTokens` — 카드·상세·팝업 4곳에 흩어지던 ` · ` 조합을 한곳으로 |
| `ui/MeetingReservationDetailPage.tsx` | `inviteCodeRevoked` 추가. 취소된 예약은 코드 자리에 `취소된 예약` + 폐기 안내(STEP08 프레임 배경 화면) |
| `ui/parts/ReservationCard.tsx` | 자체 `joinTokens` 제거하고 공용 util 사용 |
| `ui/parts/meeting-reservation-parts.css` | `.vo-cancel*` 규칙 |
| `index.ts` | 팝업 2종 export |
| 테스트 2종 | 확인 팝업 3케이스, 완료 팝업 3케이스 |

### 판단 근거

- 확인 팝업의 두 버튼은 프레임대로 가로 배치가 필요한데 공용 `.popup-actions`가 세로 고정이라 `.vo-cancel__actions`로 2열 그리드를 따로 뒀다.
- 완료 팝업의 `승인완료 건의 기존 코드는 폐기되었습니다.` 줄은 `inviteCodeRevoked`로 분기했다. STEP08 정의서 02행이 승인대기 취소에는 폐기할 코드가 없다고 명시한다.
- 취소 흐름 배선(확인 → API → 완료)은 호출부 책임으로 남겼다. UI는 팝업 open 상태와 콜백만 노출한다.

### 3차 검증

| 명령 | 결과 |
| --- | --- |
| `npx vitest run src/features/meeting-reservation/` | 52 passed |
| `npm run lint` | 통과 |
| `npm run build` | 통과 |

## 남은 제한

- Figma node `10:3828` 대조 미실행(채널 만료). 항목 순서·라벨·하단 액션 구성은 채널 재연결 후 확인이 필요하다.
- 상세 화면 라우팅과 데이터 연결(Logic)은 이번 범위 밖이다.
