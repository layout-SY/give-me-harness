# 인계

## Assignment 이동

- 보내는 host·session·role: claude / `.claude/logs/sessions/2026-09-09-reservation-detail-ui` / `ui`
- 받는 host·session·제안 role: codex(권장) / 새 세션 / `logic` (`--role logic`으로 새 inject 세션 시작 필요)
- 갱신 시점: Logic 작업 `2184467` merge 후 검토 완료 시점

## 역할 라우팅

- 요청 역할(`requested_roles`): ui
- 확인된 역할(`confirmed_roles`): ui
- 완료 역할(`completed_roles`): ui (STEP06 상세 화면, Figma 정렬, 취소 팝업 2종), logic (목록·상세·취소·제한 API와 MSW·라우트 — `task/reservation-mock-logic`, codex)
- 다음 제안 역할(`next_role`): logic
- 역할 판단 근거: 남은 후속 조치 3건이 전부 `src/pages/meeting-reservation`과 `src/features/meeting-reservation/api` 아래이며 라우팅·데이터 계약 문제다. UI 세션의 승인 scope(`src/features/meeting-reservation` 중 `ui/**`) 밖이다.
- 사용자 확인: 사용자가 "지금 이 내용 다른 세션에서 실행할 수 있게끔 handoff 문서 만들어놔"라고 지시했다. 다음 역할의 실제 확정은 인계받는 세션에서 다시 받는다.

## 목표 및 현재 상태

**UI와 Logic이 모두 연결된 상태다.** 브랜치 `task/reservation-detail-ui` HEAD는 `2184467`이고, Logic 자식 브랜치 `task/reservation-mock-logic`은 ff-only merge 후 `CLOSED`다. 이 브랜치는 아직 `sy-main`에 **미병합**이다.

검토 결과 동작과 품질은 양호하나 **후속 조치 3건**이 남아 있다. 아래 「후속 조치 3건」이 이 인계의 본문이며, 그 아래 섹션들은 배경 자료다.

### 검토에서 확인한 것 (2026-09-09, claude/ui 세션)

| 항목 | 결과 |
| --- | --- |
| `npm run lint` | 통과 |
| `npm run build` | 통과 |
| `npx vitest run` | 565 passed / 6 failed |

6건 실패는 전부 `citizen-participation`의 기존 MSW `onUnhandledRequest` 문제이며 merge 전과 동일한 파일·테스트명이다. 예약 도메인 테스트는 전부 통과하고 신규 테스트 3종(`mocks/reservationRead.test.ts`, `pages/.../MeetingReservationRoutes.test.tsx`, `hook/useMeetingReservationRestriction.test.tsx`)이 추가됐다.

좋았던 점(그대로 유지할 것): MSW `refresh()`가 T-5 도달 시 `EXPIRED`, 종료시각 도달 시 `COMPLETED`로 상태를 전이시키고 `cancelable`을 매 조회 재계산한다(STEP06 07·08행). 취소는 `cancelInFlight` ref로 중복 실행을 막고 성공 시 상세를 `setQueryData`로 갱신한 뒤 목록·슬롯을 무효화한다. 신청 실패 중 `RESERVATION_RESTRICTED`만 제한 쿼리를 무효화하고 나머지는 dialog로 알린다.

## 후속 조치 3건

세 건 모두 Logic 소유 경로다. 우선순위는 2 → 3 → 1 순을 권장한다(2는 기능 누락, 3은 잠재 버그, 1은 명세 불일치).

### 1. 제한 팝업 닫기 동작이 프레임과 다르다

- 위치: `src/pages/meeting-reservation/ui/MeetingReserveRoute.tsx`
- 현재: `close={() => { void navigate(meetingReservationRoutes.list); }}` — 예약 **목록**으로 이동
- 프레임 근거: STEP04(`10:3687`) 정의서 04행 "동작: Popup 닫기 · **추가 화면 이동 없음** / 사용자 영향: 현재 신규 예약 제한 상태 유지"
- 문제: 팝업이 폼 대신 렌더되는 구조라 닫으면 어딘가로 가야 하는데, 목록은 프레임에 없는 이동이다. STEP04 01행이 "로비 NPC에서 회의 예약 선택 시" 진입이라고 하므로 **진입 지점인 로비(`/meeting`)로 복귀**하는 편이 명세에 가깝다.
- 판단 필요: 로비 복귀로 바꿀지, 목록 이동을 의도된 UX로 확정할지. 후자면 그 근거를 문서에 남길 것.

### 2. 반려 사유가 화면에 표시되지 않는다

- 위치: `src/pages/meeting-reservation/ui/MeetingReservationRoutes.tsx`(미연결), `src/features/meeting-reservation/api/meetingReservationRead.dto.ts`(필드 없음)
- 현재: 상세 라우트가 `noticeTitle`/`noticeDescription`을 전달하지 않고, 상세 응답 DTO에도 해당 필드가 없다
- 결과: `REJECTED` 예약을 열면 배지만 `반려`로 뜨고 **사유가 비어 있다**
- UI 계약: 두 props가 **모두** 있어야 `NoticeBox`가 렌더된다. 하나만 주면 표시되지 않는다
- 조치안: 상세 응답에 `noticeTitle: string | null`, `noticeMessage: string | null`을 추가하고 parser에서 `noticeDescription`으로 매핑, MSW fixtures의 `REJECTED` 건에 사유를 채운다. 서버 계약 미확정이라 보류한 것이라면 그 판단을 문서에 남기고, 최소한 상태별 고정 문구(예: 승인만료 안내)를 클라이언트에서 채울지 결정할 것
- 참고: 이 문서 「5. 예약 상세」 DTO 표에 `noticeTitle`/`noticeMessage`가 이미 추정으로 들어가 있다

### 3. 예약 폼이 배경 refetch에 언마운트될 수 있다

- 위치: `src/pages/meeting-reservation/ui/MeetingReserveRoute.tsx`
- 현재: `if (restriction.isPending || restriction.isFetching) return <Loading />;`
- 문제: `isFetching`은 배경 refetch에도 true가 되어 **입력 중이던 폼 전체가 언마운트되고 입력값이 사라진다.** `MeetingReserveContent`가 별도 컴포넌트라 상태가 통째로 초기화된다
- 발생 경로: 제한 쿼리는 `refetchOnWindowFocus: false`라 일상적으로는 안 터진다. 다만 `useMeetingReservationMutation`의 `onError`가 `RESERVATION_RESTRICTED` 응답에서 제한 쿼리를 무효화하므로(`useMeetingReservationMutation.ts:31`), 그 시점 refetch가 폼을 날린다. 제한 상태면 어차피 폼을 못 쓰지만, 다른 무효화 경로가 추가되면 실제 데이터 유실이 된다
- 조치안: 초기 진입만 막도록 `isPending`만 검사한다. 배경 갱신 중 제한 상태가 바뀌면 그때 팝업으로 전환된다
- 검증: 폼 입력 중 `queryClient.invalidateQueries({ queryKey: meetingReservationKeys.restriction() })`를 호출해도 입력값이 유지되는지 확인하는 테스트를 권장한다

## 완료된 작업

## 완료된 작업

| 경로 | 내용 |
| --- | --- |
| `ui/parts/reservationStatus.ts` | `ReservationStatus` 6종, `RESERVATION_STATUS_TONE`, `RESERVATION_STATUS_LABEL`, `resolveReservationStatusLabel` |
| `ui/parts/ReservationDetailSection.tsx` | 제목 + `<dl>` 표시 파츠 |
| `ui/MeetingReservationDetailPage.tsx` | controlled 상세 화면 |
| `ui/parts/ReservationCard.tsx` | 상태 정의를 `reservationStatus`로 이관(`ReservationListStatus`는 별칭 re-export) |
| `ui/parts/meeting-reservation-parts.css` | `.vo-detail*` 규칙 |
| `index.ts` | `MeetingReservationDetailPage`, `ReservationStatus` export |
| `ui/MeetingReservationDetailPage.test.tsx` | 9 케이스 |

## 배경 — 인계 당시의 대기 작업 (현재 모두 구현 완료)

아래 4개 항목은 `2184467`에서 구현됐다. **이력으로만 읽고 다시 착수하지 말 것.** 구현 결과는 각 항목 끝의 「구현됨」 줄을 참고한다.

### 1. 조회 API 부재

`api/meetingReservation.api.ts`에는 옵션 조회 4종과 `POST /meeting-reservations`만 있다. 다음이 없다.

- `GET /meeting-reservations` (목록, 탭·페이지 파라미터)
- `GET /meeting-reservations/{reservationId}` (상세)
- 예약 취소 실행
- 신규 예약 제한 상태 조회

**구현됨**: `api/meetingReservationRead.dto.ts`(목록·상세·취소·제한 4종 스키마), `api/meetingReservationRead.parser.ts`(표시 문자열 조합), `api/meetingReservation.api.ts`에 호출 추가.

### 2. MSW 핸들러 부재

`mocks/handlers.ts`의 목 데이터는 신청 폼 흐름 전용이다.

- 테마 `theme-camping` 1건 / 날짜 `2026-09-08` 1건 / 슬롯 14:00~15:00 1건 / 참여자 2명
- `POST` 응답은 항상 `PENDING_APPROVAL`, `inviteCode: null`
- 목록·상세 응답 없음. 상태 6종 중 `REJECTED`·`COMPLETED`는 목 데이터에 존재하지 않는다
- 워커는 `VITE_API_BASE_URL_STATUS === "dev"`일 때만 시작한다(`src/app/mocks/startMocks.ts`)

**구현됨**: `mocks/fixtures.ts`(상태 6종 전부 포함), `mocks/handlers.ts`에 `GET /restriction`, `GET /`(목록), `GET /:reservationId`(상세), `POST /:reservationId/cancel` 추가. `createMeetingReservationHandlers`가 `now`·`reservations`·`restriction`·`delayMs`·`failReads` 옵션을 받아 테스트에서 시간과 실패를 주입할 수 있다.

### 3. 라우팅 미등록

`src/app/routing.ts`의 보호 라우트에는 `meetingReservationRoutes.reserve` → `MeetingReserveRoute`만 있다. 목록·상세 라우트가 없고, `MeetingReservationListPage`는 feature `index.ts`에서 export되지 않는다(상세만 이번에 추가).

**구현됨**: `meetingReservationRoutes`에 `list`(`/meeting/reservations`), `detailPattern`, `detail(id)` 추가. `MeetingReservationRoutes.tsx`의 `MeetingReservationListRoute`·`MeetingReservationDetailRoute`를 `routing.ts`에 등록. 목록 탭·페이지는 `?scope=&page=` 쿼리로 유지되고 상세에서 뒤로가기 시 그대로 복원된다.

### 4. 상태 계약 불일치

`model/reservation.ts`의 `MEETING_RESERVATION_STATUS`는 4종(`PENDING_APPROVAL`, `APPROVED`, `EXPIRED`, `CANCELED`)이고, UI는 `REJECTED`·`COMPLETED`를 더한 6종을 `ui/parts/reservationStatus.ts`에서 소유한다. Figma STEP05·STEP06 정의서가 6종을 명시하므로 model을 6종으로 확장하는 것이 맞다.

**구현됨**: `model/reservation.ts`에 `REJECTED`·`COMPLETED` 추가, `api/meetingReservation.parser.ts`의 `STATUS_LABELS`에 `반려`·`종료` 추가. UI의 `RESERVATION_STATUS_LABEL`과 값이 일치한다.

## UI가 요구하는 props 계약

`MeetingReservationDetailPage`는 controlled 컴포넌트이며 **모든 값은 이미 서식이 적용된 표시 문자열**로 받는다. UI는 날짜·시간 포맷, 상태 판정, 권한 계산을 하지 않는다.

**Figma 정렬 작업(커밋 `ea4766b`)으로 props가 바뀌었다.** 아래가 현재 계약이다.

| props | 타입 | Logic이 채워야 할 값 |
| --- | --- | --- |
| `status` | `ReservationStatus` | 서버 상태 코드. 기본값 `PENDING_APPROVAL` |
| `statusLabel` | `string?` | 서버 표시 라벨. 비면 UI 기본 라벨 사용 |
| `meetingName` | `string?` | 회의명 |
| `themeLabel` / `dateLabel` / `timeRangeLabel` | `string?` | 예: `캠핑` / `2026.09.03` / `14:00 ~ 15:00`. UI가 ` · `로 합쳐 한 줄 메타로 표시 |
| `usageType` | `"personal" \| "team" \| "company"` | **enum 그대로 전달.** 표시 라벨(개인·팀·기업)과 소속 용어(팀명·기업명)는 UI가 파생하며, 개인이면 소속 줄을 만들지 않음 |
| `organizationName` | `string?` | 팀·기업명 원본 |
| `agenda` | `string?` | `Agenda` 항목으로 표시 |
| `reserverName` | `string?` | 예약자 닉네임 |
| `participantsLabel` | `string?` | 지정 참여자를 합친 문자열. Figma 표기는 `김민수 · 박서연 외 4명` 축약형 |
| `attendanceLabel` | `string?` | 참여 예정 인원. Figma 표기는 `7명 / 최대 10명` |
| `inviteCode` | `string?` | 숫자 10자리. 없으면 입장 코드 섹션 자체가 렌더되지 않음 |
| `noticeTitle` / `noticeDescription` | `string?` | 반려 사유 등 상태 보충 안내. **둘 다 있어야** 표시됨 |
| `canCancel` | `boolean` | **취소 가능 판정 결과**. 상태·시간 조건은 Logic이 계산 |
| `isCanceling` | `boolean` | 취소 진행 중 버튼 로딩 |
| `isLoading` | `boolean` | 조회 중. 본문과 하단 취소 바를 숨김 |
| `errorMessage` | `string?` | 조회 실패 문구. 본문과 하단 취소 바를 숨기고 `role="alert"`로 표시 |
| `onBack` / `onCancel` | `() => void` | 없으면 해당 버튼이 렌더되지 않음 |

동작 규칙(변경하려면 UI 역할과 합의 필요):

- 값이 빈 항목은 `<dl>` 줄을 만들지 않고, 섹션 항목이 전부 비면 섹션 제목도 그리지 않는다.
- 취소 버튼은 `canCancel === true`이고 로딩·오류가 아닐 때만 하단 고정 바에 나타난다.
- 입장 코드 발급 안내, 입장 가능시간 안내, 승인만료 안내는 **UI가 소유한 고정 문구**다. 서버가 내려 줄 필요가 없다.
- 코드 복사 버튼은 Figma에 없어 제거했다. 복사 기능이 필요하면 디자인 변경이 선행되어야 한다.

목록 화면(`MeetingReservationListPage`)의 `ReservationListItem`은 `reservationId`, `meetingName`, `status`, `statusLabel?`, `themeLabel`, `dateLabel`, `timeRangeLabel`, `reserverName?`, `organizationLabel?`, `note?`를 받는다.

## 화면별 API 요청·응답 DTO 추정

Figma 채널 `hgkguilr`에 연결해 STEP02~STEP08 프레임의 UI 요소와 우측 「상세 정의 및 동작」 표를 직접 읽고 정리했다. 각 항목의 근거는 프레임의 텍스트 노드와 정의서 문구다. 서버 계약이 확정되면 이 표를 대조 기준으로 쓰되 실제 스펙이 우선한다.

### 공통 규칙 (기구현 DTO에서 확인)

- 응답 봉투: `{ code, result, success, statusCode, message, msg, data, path, timestamp }` (`ServerResponse<T>`), 실제 페이로드는 `data`
- 목록형 페이로드는 `{ items: [...] }`로 감싼다
- 식별자는 `<대상>Id` (`themeId`, `timeSlotId`, `participantId`, `reservationId`)
- 날짜는 `z.iso.date()`(`2026-09-03`), 일시는 offset 포함 `z.iso.datetime({ offset: true })`(`2026-09-03T14:00:00+09:00`)
- 선택값은 optional이 아니라 **nullable**로 정의한다
- 모든 스키마는 `z.strictObject` — 서버가 필드를 추가하면 파싱이 실패하므로 계약 변경 시 DTO를 함께 갱신해야 한다
- **표시 서식은 parser가 만든다.** UI는 `14:00 ~ 15:00`, `2026.09.03` 같은 완성된 문자열만 받는다
- **개인정보 제약**: STEP05 정의서 01행 "개인정보: 이메일·전화번호 항목 없음", STEP02 정의서 07행 "닉네임만 검색 · 이메일/전화번호 입력 없음". 사용자 식별은 **닉네임만** 사용하며 이메일·전화번호 필드를 DTO에 넣지 않는다

### 1. 회의 예약 신청 폼 — STEP02 `VO_MEETING_RESERVE_MOBILE` — **기구현, 추정 아님**

`api/meetingReservation.dto.ts`에 확정돼 있고 Figma와 일치한다.

| 화면 항목 (Figma 라벨) | 요청/응답 key | Figma 정의서 근거 |
| --- | --- | --- |
| `이용유형 *` 개인/팀/기업 | `usageType: "personal" \| "team" \| "company"` | 02행 "유형별 기능·권한·시간·인원 차등 없음 · 통계 분류에 사용" |
| `팀/기업명 *` | `organizationName: string \| null` | 03행 "팀 또는 기업 선택 시만 노출·필수 · 개인 선택 시 숨김" |
| `테마 *` | `GET /themes` → `items[].themeId`, `items[].name` | 04행 "캠핑/우주/호텔 중 1개 선택" |
| `예약 날짜 *` | `GET /dates?themeId=` → `items[].date` | 05행 |
| `1시간 시간 슬롯 *` | `GET /time-slots?themeId=&date=` → `items[].timeSlotId`, `startsAt`, `endsAt` | 06행 "예약 1건=정확히 1시간 · 승인대기도 슬롯 점유 · 회의 시작 5분 전부터 신규 신청 불가" |
| `지정 참여자` 닉네임 검색 | `GET /participants?nickname=` → `items[].participantId`, `nickname`, `matchLabel` | 07행 "닉네임만 검색 · 예약자 본인은 지정 참여자에 다시 추가하지 않음" |
| 지정 참여자 현황 | `participantIds: string[]` (최대 9) | 08행 "지정 참여자 최대 9명", 09행 "예약자 포함 활성 이용 최대 10명" |
| `회의명 *` | `meetingName: string` | 10행 "공백 포함 미입력 상태에서는 예약 신청 조건 미충족" |
| `Agenda (선택)` | `agenda: string \| null` | 11행 "미입력이어도 예약 신청 가능" |
| `예약 신청` | `POST /meeting-reservations` → `reservationId`, `status`, `slotOccupied`, `inviteCode` | 13행 |

**13행 정의서에서 새로 확인된 계약**: 제출 직전에 서버가 "시간/신규예약 제한/슬롯/중복예약/참여자"를 재검증한다. 실패 분기는 두 갈래다 — No-show 제한이면 `VO_RESERVATION_RESTRICTED_POPUP`, 그 외 검증 실패는 폼에 남는다. 따라서 **POST 오류 응답에 제한 상태를 식별할 코드가 필요**하다(예: `RESERVATION_RESTRICTED` 409). 현재 MSW 핸들러의 오류 코드는 `INVALID_REQUEST`, `TIME_SLOT_OCCUPIED`, `UNAUTHORIZED`뿐이다.

### 2. 예약 신청 완료 팝업 — STEP03 `VO_RESERVE_COMPLETE_POPUP`

별도 API 없이 1번의 POST 응답을 쓴다. 구현과 Figma 문구가 일치한다.

| 화면 항목 | 출처 | Figma 정의서 근거 |
| --- | --- | --- |
| 현재 상태 `승인대기` | `statusLabel` — 응답에 없고 parser가 `STATUS_LABELS[status]`로 생성 | 02행 "표시: 현재 상태 승인대기" |
| "신청 완료 시 선택한 시간 슬롯이 점유됩니다." | `slotOccupied: true` 고정 | 02행 "승인대기 상태도 동일 테마·동일 시간대 슬롯 점유" |
| "숫자 10자리 코드는 관리자 승인 성공 후 발급됩니다." | `inviteCode: null` 고정 | 03행 "관리자 승인 성공 시에만 숫자 10자리 코드 1개 생성" |

**코드 형식이 Figma에서 확정됐다**: 숫자 10자리, 예약당 1개, 수정·재발급 없음(STEP06 05행). DTO에 `z.string().regex(/^\d{10}$/)` 검증을 넣을 근거가 된다.

### 3. 신규 예약 제한 안내 팝업 — STEP04 `VO_RESERVATION_RESTRICTED_POPUP`

**대응 API가 없다.** 현재 팝업 문구는 전부 하드코딩 기본값이다.

Figma 01행: "로비 NPC에서 회의 예약 선택 시 신규예약 제한 상태 **사전 검사** · 제한 상태이면 M01 대신 본 Popup 표시". 즉 **예약 폼 진입 전에 조회하는 별도 엔드포인트가 필요**하다.

추정 요청: `GET /meeting-reservations/restriction`

| 화면 항목 (Figma 값) | 추정 응답 key | 타입 | 정의서 근거 |
| --- | --- | --- | --- |
| 팝업 노출 여부 | `restricted` | `boolean` | 01행 "정상: 제한 없음이면 VO_MEETING_RESERVE_MOBILE 진입" |
| `No-show로 신규 예약 신청이 제한 중입니다.` | `reason` | `string` | 02행 |
| 제재 종류 분기 | `reasonCode` | `"NO_SHOW"` 등 | 02행 "No-show 발생 시 예약자 신규예약 제한 168시간" |
| `신규 예약 신청 · 168시간` | `restrictedUntil` + `durationHours` | ISO datetime + `number` | 02행 "최신 No-show 발생시각 기준 종료시각 갱신" |
| `제한 중 다시 No-show가 발생하면…` | 클라이언트 고정 문구로 충분 | — | 02행 갱신 규칙 |
| `기존 승인완료 예약 · 초대받은 회의 · 코드 참여` | 클라이언트 고정 문구로 충분 | — | 03행 "허용: 기존 승인완료 예약 이용 · 제재 전 승인대기 예약의 관리자 승인 · 다른 예약 지정 참여자·코드 참여" |

```json
{ "restricted": true, "reasonCode": "NO_SHOW",
  "reason": "No-show로 신규 예약 신청이 제한 중입니다.",
  "restrictedUntil": "2026-09-15T14:00:00+09:00", "durationHours": 168 }
```

**`restrictionScope` 문구는 서버가 조합하지 않기를 권장한다.** `168시간`은 `durationHours`에서, 대상은 고정 문구에서 만들 수 있고, UI 주석도 "남은 기간 계산은 호출부의 책임"으로 적혀 있다. 03행의 "A06 예약제한 관리 Overlay의 최신 제한 상태를 **다음 예약 진입 시 재검사**"는 이 조회를 캐시하지 말아야 한다는 뜻이다.

### 4. 예약 조회 목록 — STEP05 `VO_RESERVATION_LIST_MOBILE`

추정 요청: `GET /meeting-reservations?scope=mine|invited&page=1&size=10`

02행 "두 탭 전환 · 카드 선택 시 VO_RESERVATION_DETAIL_MOBILE", "목록에서는 코드·취소 실행 버튼을 직접 노출하지 않음" — 현재 구현과 일치한다.

| 카드 표시 항목 (Figma 값) | 추정 응답 key | 타입 | UI 매핑 |
| --- | --- | --- | --- |
| 카드 클릭 → 상세 | `reservationId` | `string` | `reservationId` |
| 상태 배지 `승인대기` | `status` | 6종 enum | `status` |
| 배지 문구 | `statusLabel` | `string` | 없으면 UI 기본 라벨 |
| `서비스 운영 협의` | `meetingName` | `string` | `meetingName` |
| `우주 · 2026.09.03 · 15:00 ~ 16:00` | `themeName` + `reservationDate` + `startsAt`/`endsAt` | `string` + ISO | `themeLabel`/`dateLabel`/`timeRangeLabel` (parser가 서식) |
| `예약자 김민수 · 기업 한국정보기술` | `reserverName` + `usageType` + `organizationName` | `string` + enum + `string \| null` | `reserverName` / `organizationLabel` |
| 승인만료 카드의 `예약 시작 5분 전까지 승인 미완료` | `note` | `string \| null` | `note` |

```json
{ "items": [ { "reservationId": "reservation-1", "status": "PENDING_APPROVAL", "statusLabel": "승인대기",
    "meetingName": "서비스 운영 협의", "themeName": "우주", "reservationDate": "2026-09-03",
    "startsAt": "2026-09-03T15:00:00+09:00", "endsAt": "2026-09-03T16:00:00+09:00",
    "reserverName": "김민수", "usageType": "company", "organizationName": "한국정보기술", "note": null } ],
  "page": 1, "size": 10, "totalCount": 1, "totalPages": 1 }
```

**Figma에서 확인된 차이 두 가지**

- 소속 표기가 `기업 한국정보기술` / `팀 아산 프로젝트팀`처럼 **이용유형 라벨 + 조직명**이다. 따라서 응답에 `usageType`이 필요하고, parser가 `organizationLabel`을 조합해야 한다.
- `note`는 상태에서 유도 가능한 고정 문구(`승인만료` → "예약 시작 5분 전까지 승인 미완료")로 보인다. 서버 필드로 받기보다 **클라이언트 상태별 문구 매핑을 권장**한다.

**주의**: STEP05 프레임에 **페이지네이션 UI가 없다.** 현재 구현은 `Pagination`을 쓰고 있으므로, 무한 스크롤·전체 목록 중 무엇이 맞는지 확인이 필요하다. 확정 전에는 `page`/`size` 쿼리를 유지하되 UI 노출 여부는 별도 판단 대상이다.

### 5. 예약 상세 — STEP06 `VO_RESERVATION_DETAIL_MOBILE`

추정 요청: `GET /meeting-reservations/{reservationId}`

| 화면 항목 (Figma 값) | 추정 응답 key | 타입 | 정의서 근거 |
| --- | --- | --- | --- |
| 상태 배지 `승인완료` | `status` / `statusLabel` | 6종 enum / `string` | 02행 "승인대기·승인완료·반려·취소·승인만료·종료" |
| `아산 프로젝트 주간회의` | `meetingName` | `string` | 02행 |
| `캠핑 · 2026.09.03 · 14:00 ~ 15:00` | `themeName`, `reservationDate`, `startsAt`, `endsAt` | `string` + ISO | 02행 "회의명·테마·예약일·정확히 1시간 시간대" |
| 예약 정보 `이용유형  팀` | `usageType` | enum | 03행 "이용유형·팀/기업명 조건부 표시·Agenda" |
| 예약 정보 `팀명  아산 프로젝트팀` | `organizationName` | `string \| null` | 03행 조건부 표시 |
| 예약 정보 `Agenda  주간 진행사항 공유` | `agenda` | `string \| null` | 03행 "등록된 예약정보는 읽기 전용" |
| 참여자 `예약자  정영진` | `reserverName` | `string` | 04행 "예약자 닉네임·지정 참여자 닉네임" |
| 참여자 `지정 참여자  김민수 · 박서연 외 4명` | `participants[].nickname` | `{ participantId, nickname }[]` | 04행 |
| 참여자 `참여 예정  7명 / 최대 10명` | `expectedParticipantCount` + `maxParticipantCount` | `number` | 04행 "예약자+지정+코드 참여자 포함 활성 이용 최대 10명" |
| 입장 코드 `1234567890` | `inviteCode` | `string \| null` (숫자 10자리) | 05행 "승인완료 상태에서만 표시 · 예약당 1개 · 수정/재발급 없음" |
| 취소된 예약의 코드 자리 `취소된 예약` | `inviteCodeRevoked` | `boolean` | STEP08 프레임 배경 화면. 취소 전 발급된 코드가 있었는지 구분해야 폐기 안내를 표시할 수 있다 |
| `회의 시작 5분 전부터 테마 대기공간 입장 가능` | 클라이언트 고정 문구 | — | 06행 |
| 취소 버튼 노출 | `cancelable` | `boolean` | 07행 "권한: 예약자 · 상태 승인대기/승인완료 · 현재 < T-5" |

```json
{ "reservationId": "reservation-1", "status": "APPROVED", "statusLabel": "승인완료",
  "meetingName": "아산 프로젝트 주간회의", "themeName": "캠핑", "reservationDate": "2026-09-03",
  "startsAt": "2026-09-03T14:00:00+09:00", "endsAt": "2026-09-03T15:00:00+09:00",
  "usageType": "team", "organizationName": "아산 프로젝트팀", "agenda": "주간 진행사항 공유",
  "reserverName": "정영진",
  "participants": [ { "participantId": "participant-1", "nickname": "김민수" },
                    { "participantId": "participant-2", "nickname": "박서연" } ],
  "expectedParticipantCount": 7, "maxParticipantCount": 10,
  "inviteCode": "1234567890", "inviteCodeRevoked": false, "cancelable": true }
```

취소된 예약을 다시 조회하면 `inviteCode: null`, `inviteCodeRevoked: true`가 되어 상세가 코드 자리에 폐기 안내를 표시한다. 승인대기에서 취소한 건은 발급된 코드가 없으므로 두 값 모두 `null` / `false`다.

**`cancelable`은 서버가 내려 주기를 권장한다.** 07행 조건(예약자 본인 · 승인대기/승인완료 · 현재 < T-5)에는 서버 시각과 본인 여부가 필요해 클라이언트가 정확히 재현할 수 없다. `isOwner`, `startsAt`을 함께 받아 클라이언트가 계산하는 방식은 시계 오차에 취약하다.

**승인만료 Variant (08행)**: 승인대기 상태로 T-5 도달 시 승인만료. 처리는 "코드 없음·슬롯 반환·No-show 없음·신규예약 제한 없음·취소 불가". 즉 승인만료 응답은 `inviteCode: null`, `cancelable: false`가 되고, 화면 문구 "승인만료 시 코드 없음 · No-show 없음 · 예약제한 없음"은 클라이언트 고정 문구로 충분하다.

### 6. 예약 취소 — STEP07 `VO_CANCEL_CONFIRM_POPUP` / STEP08 `VO_CANCEL_COMPLETE_POPUP`

**두 팝업 모두 구현 완료다**(커밋 `b5b07fa`). 확인 팝업은 회의명·메타를 다시 보여 주고 "회의 시작 5분 전까지 취소할 수 있습니다. / 취소 버튼을 누르면 조건을 다시 확인합니다."를 안내하며 `닫기` / `예약 취소` 두 버튼을 둔다. **별도 조회 API 없이 상세 응답의 `meetingName`·`themeName`·`reservationDate`·`startsAt`/`endsAt`을 재사용한다.**

추정 요청: `POST /meeting-reservations/{reservationId}/cancel`

02행 "Validation: 예약자 본인 · 상태 승인대기/승인완료 · 현재 시각 < T-5를 **최종 클릭 순간 재검증**"이므로, 상세의 `cancelable`은 표시용이고 **실제 판정은 이 호출이 한다.** 상태 전이가 있으므로 `DELETE`보다 하위 리소스 액션을 권장한다.

```json
{ "reservationId": "reservation-1", "status": "CANCELED", "statusLabel": "취소",
  "slotReleased": true, "inviteCodeRevoked": true, "participantNotified": true }
```

- `slotReleased`: 02행 "슬롯 즉시 반환" — 항상 true
- `inviteCodeRevoked`: 02행 "승인완료: 10자리 코드 폐기" / "승인대기: 코드 없음". **완료 팝업의 `inviteCodeRevoked` props로 그대로 전달**되어 `승인완료 건의 기존 코드는 폐기되었습니다.` 줄의 표시 여부를 결정한다. 상세를 재조회할 때도 같은 이름의 필드가 필요하다
- `participantNotified`: 02행 "승인완료: 지정 참여자 취소 알림 / 승인대기: 알림 없음". STEP08 02행 "**알림 실패가 발생해도 취소 업무 상태는 유지**" — 즉 이 값이 false여도 취소는 성공이며, UI가 이를 실패로 다루면 안 된다. 현재 UI는 이 값을 표시하지 않으므로 응답에서 빼도 화면은 동작한다

응답의 `status`/`statusLabel`은 취소 후 상세를 갱신하는 데 쓴다. 완료 팝업 자체는 회의명·메타만 필요하며 이는 상세에서 이미 갖고 있다.

오류 코드 추정: `NOT_CANCELABLE`(409, 03행 "현재 ≥ T-5 또는 최신 상태 변경 시 취소하지 않고 기존 예약 상태 유지"), `RESERVATION_NOT_FOUND`(404), `FORBIDDEN`(403, 예약자 본인 아님). 취소 사유 입력은 Figma에 없으므로 요청 본문은 비어 있다.

취소 완료 후 상세 화면은 상태 `취소`, 입장 코드 자리에 `취소된 예약` + "기존 승인 코드는 더 이상 사용할 수 없습니다"를 표시한다. 03행 "자동 화면 이동은 확정 근거가 없어 추가하지 않음" — 확인 버튼은 팝업만 닫는다.

### 상태 enum 확장

목록·상세 응답의 `status`는 6종이어야 한다(STEP05 02행, STEP06 02행). `model/reservation.ts`의 `MEETING_RESERVATION_STATUS`에 `REJECTED`, `COMPLETED`를 추가하고 `parser`의 `STATUS_LABELS`에도 `반려`, `종료`를 채워야 UI의 `RESERVATION_STATUS_LABEL`과 어긋나지 않는다.

## Figma 대조 결과

STEP06 프레임을 읽어 확인한 차이 12개 중 **10개는 2차 작업에서 해소했다.**

| # | Figma | 처리 |
| --- | --- | --- |
| 1 | 상단 `‹ 예약 목록` 텍스트 링크 | **해소** — `.vo-detail__back` + 스크린리더용 `h1` |
| 2 | 회의명 아래 한 줄 메타 | **해소** — `.vo-detail__meta` |
| 3 | `예약 정보` = 이용유형·팀명·Agenda | **해소** |
| 4 | `참여자` 섹션 = 예약자·지정 참여자·참여 예정 | **해소** |
| 5 | `참여 예정  7명 / 최대 10명` | **해소** — `attendanceLabel` props 추가 |
| 6 | 지정 참여자 `김민수 · 박서연 외 4명` 축약 | **해소** — 축약 문자열 조합은 Logic 책임으로 계약화 |
| 7 | `입장 코드` + 발급 안내 문구 | **해소** — UI 고정 문구 |
| 8 | 코드 복사 버튼 없음 | **해소** — 버튼과 `onCopyInviteCode` 제거 |
| 9 | 입장 가능시간 안내 | **해소** — UI 고정 문구 |
| 10 | 승인만료 variant 문구 | **해소** — `status === "EXPIRED"`에서 표시 |
| 11 | 취소 → `VO_CANCEL_CONFIRM_POPUP` 확인 단계 | **해소** — `ReservationCancelConfirmPopup` 신규 |
| 12 | 취소 성공 → `VO_CANCEL_COMPLETE_POPUP` | **해소** — `ReservationCancelCompletePopup` 신규. 취소된 예약의 상세 코드 자리 변형(`취소된 예약`)도 함께 구현 |

DESIGN.md와 충돌한 값은 DESIGN.md를 따랐다. 11px 문구는 12px로, 13px 본문은 14px로, 회의명 20px은 기존 18px 단계로 맞췄고 색은 기존 토큰만 썼다.

### 목록 화면(STEP05)에 남은 판단

- 소속 표기가 `기업 한국정보기술`처럼 **이용유형 라벨 + 조직명**이다. UI는 `organizationLabel` 문자열을 그대로 표시하므로 Logic이 조합해 내려 주면 된다. UI 변경은 필요 없다.
- **페이지네이션은 목록 아래 유지로 확정됐다**(사용자 결정, 2026-09-09). 현재 구현이 이미 `.vo-reservation-list__items` 다음에 두고 있어 변경하지 않았다. 항목이 있고 `pageCount > 1`일 때만 노출한다.

### 취소 흐름 UI 계약 (신규)

| 컴포넌트 | props | 비고 |
| --- | --- | --- |
| `ReservationCancelConfirmPopup` | `open`, `close`, `meetingName?`, `themeLabel?`, `dateLabel?`, `timeRangeLabel?`, `isCanceling?`, `onConfirm?` | 상세의 `onCancel`이 이 팝업을 연다. `onConfirm`이 실제 취소 요청. `isCanceling` 중에는 닫기를 막는다 |
| `ReservationCancelCompletePopup` | `open`, `close`, `meetingName?`, `themeLabel?`, `dateLabel?`, `timeRangeLabel?`, `inviteCodeRevoked?`, `onConfirm?` | `inviteCodeRevoked`는 취소 응답의 같은 이름 필드를 그대로 넘긴다. 승인대기 취소면 false라 코드 폐기 문구가 빠진다 |
| `MeetingReservationDetailPage` | `inviteCodeRevoked?` 추가 | 코드가 없어도 이 값이 true면 코드 자리에 `취소된 예약` + 폐기 안내를 표시한다 |

취소 흐름 배선은 호출부(라우트) 책임이다: 상세 `onCancel` → 확인 팝업 open → `onConfirm`에서 취소 API 호출 → 성공 시 확인 팝업 닫고 완료 팝업 open → 상세 재조회.

## 결정 사항 및 제약 조건

- 취소 권한 판정, 승인만료 전이, 참여 코드 발급은 Logic 경계로 합의됐다. UI는 boolean과 문자열만 받는다. Figma STEP07 02행의 "최종 클릭 순간 재검증"이 이 경계를 뒷받침한다.
- DESIGN.md: 고정 480px 셸, 뷰포트 미디어 쿼리 금지, 신규 색 토큰 금지.
- 화면 확인 수단은 **B(Logic 전체 구현)로 해결됐다.** MSW와 라우트가 붙어 `VITE_API_BASE_URL_STATUS=dev`로 실행하면 `/meeting/reservations`에서 목록·상세·취소를 실제로 확인할 수 있다.
- Figma 채널은 `hgkguilr`로 이번 세션에서 연결에 성공했다. 다음 세션에서도 같은 채널로 시도하고, 실패할 때만 사용자에게 새 채널을 요청한다.

## 소유권과 Git 계약

- 현재 HEAD: `2184467` (Logic 자식 브랜치를 ff-only로 병합한 결과)
- UI 커밋: `96a5e3e`(상세 신규), `ea4766b`(Figma 정렬), `b5b07fa`(취소 팝업)
- Logic 커밋: `2184467` (26 files, +1054/-111, codex/`task/reservation-mock-logic`)
- 역할별 파일 소유권: UI가 `ui/**`와 `ui/parts/*.css`를 소유. `api/**`, `model/**`, `hook/**`, `mocks/**`, `src/pages/meeting-reservation/**`, `src/app/routing.ts`, `src/shared/config/meetingReservationRoutes.ts`는 Logic 소유
- 충돌 여부: 없음. 워킹 트리 clean
- task·branch·worktree: `task/reservation-detail-ui` / 분기 기준 `sy-main` / `/Users/okand/SynologyDrive/asan-worktrees/reservation-detail-ui`
- Git 통합 담당자: **claude** (이 브랜치). 자식 `task/reservation-mock-logic`의 담당자는 codex였고 해당 계약은 `CLOSED`다
- **후속 조치 3건은 이 브랜치의 UI scope 밖이다.** 이어받는 세션은 두 경로 중 하나를 택한다.
  - (a) 이 브랜치에서 이어가기: `--role logic` 세션 + `scope-proposal → update-scope`로 `src/pages/meeting-reservation`, `src/app/routing.ts`, `src/features/meeting-reservation/api` 추가 승인. 계약의 `asan-role`이 `ui`인 점도 함께 정리해야 한다
  - (b) 새 자식 브랜치: `task/reservation-detail-ui`를 parent로 `branch_workflow.py proposal → create`. 이 브랜치가 아직 `ACTIVE`이므로 자식 생성이 가능하다
- 산출물 책임: owner (필수 8종 작성 완료)
- merge 상태: **미병합**. `sy-main` 병합 승인은 아직 받지 않았다. 사용자는 병합 후 `sy-main` 소유권 반납을 요청한 상태이며, 후속 조치 3건을 병합 전에 처리할지 후속으로 둘지 아직 결정되지 않았다

## 관련 경로와 스킬

- `.agent-policy/common/skills/policy/task-role-routing/references/logic.md`
- `.agent-policy/common/skills/policy/git-branch-strategy/SKILL.md`
- `src/features/meeting-reservation/api/meetingReservation.api.ts`, `.dto.ts`, `.parser.ts`
- `src/features/meeting-reservation/mocks/handlers.ts`, `src/app/mocks/browser.ts`, `src/app/mocks/startMocks.ts`
- `src/app/routing.ts`, `src/shared/config/meetingReservationRoutes.ts`
- `src/pages/meeting-reservation/ui/MeetingReserveRoute.tsx` (route ↔ hook ↔ page 연결 참고 구현)
- Figma 채널 `hgkguilr` / 프레임: STEP02 `10:3458`, STEP03 `10:3616`, STEP04 `10:3687`, STEP05 `10:3754`, STEP06 `10:3828`, STEP07 `10:3920`, STEP08 `10:3982`

## 명령어 및 결과

merge 후 `2184467`에서 claude/ui 세션이 실행한 결과다.

| 명령 | 결과 |
| --- | --- |
| `npm run lint` | 통과 |
| `npm run build` | 통과 |
| `npx vitest run` | **565 passed / 6 failed** |

6개 실패는 전부 `citizen-participation`(`api/http/citizenParticipation.api.test.ts` 1, `mocks/handlers.test.ts` 3, `pages/.../CitizenResultRoutes.test.tsx` 2)이며 MSW `onUnhandledRequest: "error"` 전략과 현재 msw 버전의 bypass 동작 충돌로 보인다. merge 전과 동일한 파일·테스트명이고 예약 도메인과 의존 관계가 없다. **전체 테스트가 이미 빨간 상태라 새 회귀 신호가 묻힌다.** 이어받는 세션은 예약 도메인만 돌려 신호를 분리할 것을 권장한다.

```sh
npx vitest run src/features/meeting-reservation/ src/pages/meeting-reservation/
```

## 실행하지 않은 검증

- **브라우저 실제 렌더 확인.** 라우트와 MSW가 붙어 이제 가능하다. `VITE_API_BASE_URL_STATUS=dev`로 `npm run dev` 후 `/meeting/reservations`에서 목록 → 상세 → 취소 흐름과 상태 6종 카드를 확인할 것. 단 이미지 캡처·시각 QA는 사용자가 요청할 때만 수행한다
- 목록 페이지·카드의 표시 회귀 테스트(해당 테스트가 저장소에 없음)
- 후속 조치 3건 수정과 그 회귀 테스트
- `sy-main` 병합과 사후 검증

## 다음 조치

1. `--role logic` 세션을 새로 시작하고 이 문서와 현재 브랜치 상태(`branch_workflow.py context`)를 함께 읽는다.
2. 「후속 조치 3건」을 사용자와 검토해 **처리 범위와 브랜치 경로(a: scope 확장 / b: 새 자식 브랜치)** 를 확정받는다. 1번(제한 팝업 닫기 이동)은 UX 결정이라 사용자 확인 없이 바꾸지 않는다.
3. 승인 후 2번(반려 사유) → 3번(폼 언마운트) → 1번(닫기 동작) 순으로 수정하고, 각 건에 회귀 테스트를 붙인다.
4. 예약 도메인만 돌려 검증한다: `npx vitest run src/features/meeting-reservation/ src/pages/meeting-reservation/`, 이어서 `npm run lint`, `npm run build`.
5. 브라우저에서 목록 → 상세 → 취소 흐름을 확인한다(사용자 요청이 있을 때만 캡처).
6. 이 브랜치의 `sy-main` 병합은 **claude(이 브랜치 Git 통합 담당자)** 가 수행한다. 후속 조치를 마쳤으면 완료 계약을 만들어 사용자 승인을 받는다. 사용자는 병합 후 `sy-main` 소유권 반납을 요청해 둔 상태다.

### 참고 — 완료 workflow에서 걸렸던 점

`finish-proposal`은 **source 워크트리에서** 실행해야 하고, 실행 전에 세션 산출물 8종이 구조 검사를 통과해야 한다. 이 세션은 처음에 `grill-me-review.md`(Method Guardrails·`neutral question-first 적용 여부` 문구·Recommended Answer 열·데이터 행 필요)와 `portfolio-log.md`(`## 사례 N` + 5개 `###` 소제목 + 필수 `- 필드:` 행 필요)에서 막혀 템플릿 구조로 다시 작성했다. 이어받는 세션도 같은 검사를 통과해야 한다.
