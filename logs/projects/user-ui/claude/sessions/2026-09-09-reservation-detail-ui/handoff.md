# 인계

## Assignment 이동

- 보내는 host·session·role: claude / `.claude/logs/sessions/2026-09-09-reservation-detail-ui` / `ui`
- 받는 host·session·제안 role: 미정 host / 새 세션 / `logic` (`--role logic`으로 새 inject 세션 시작 필요)

## 역할 라우팅

- 요청 역할(`requested_roles`): ui
- 확인된 역할(`confirmed_roles`): ui
- 완료 역할(`completed_roles`): ui (STEP06 예약 상세 화면 구현·테스트)
- 다음 제안 역할(`next_role`): logic
- 역할 판단 근거: 남은 작업이 목록·상세 조회 API, DTO·parser, 조회 hook, MSW 핸들러, 라우트 연결이며 전부 데이터·상태 전이 계층이다. UI 세션에서는 계층 경계상 구현할 수 없다.
- 사용자 확인: 사용자가 이번 세션에서 "logic한테 인계할 핸드오프 문서 작성"을 지시했다. 다음 역할의 실제 확정은 인계받는 세션에서 다시 받는다.

## 목표 및 현재 상태

예약 상세 모바일 화면(STEP06) UI는 구현·검증·커밋을 마쳤다(`96a5e3e`). 그러나 두 가지 문제가 있다.

1. **화면을 실제로 띄워 볼 수 없다.** 목록·상세 조회 API와 MSW 핸들러가 없고, 두 화면 모두 라우트에 등록돼 있지 않다.
2. **구현이 Figma 디자인과 여러 곳에서 다르다.** 「Figma 대조 결과」 섹션 참고. 이는 UI 역할의 후속 수정 대상이다.

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

## 대기 중인 작업 (Logic 범위)

### 1. 조회 API 부재

`api/meetingReservation.api.ts`에는 옵션 조회 4종과 `POST /meeting-reservations`만 있다. 다음이 없다.

- `GET /meeting-reservations` (목록, 탭·페이지 파라미터)
- `GET /meeting-reservations/{reservationId}` (상세)
- 예약 취소 실행
- 신규 예약 제한 상태 조회

### 2. MSW 핸들러 부재

`mocks/handlers.ts`의 목 데이터는 신청 폼 흐름 전용이다.

- 테마 `theme-camping` 1건 / 날짜 `2026-09-08` 1건 / 슬롯 14:00~15:00 1건 / 참여자 2명
- `POST` 응답은 항상 `PENDING_APPROVAL`, `inviteCode: null`
- 목록·상세 응답 없음. 상태 6종 중 `REJECTED`·`COMPLETED`는 목 데이터에 존재하지 않는다
- 워커는 `VITE_API_BASE_URL_STATUS === "dev"`일 때만 시작한다(`src/app/mocks/startMocks.ts`)

### 3. 라우팅 미등록

`src/app/routing.ts`의 보호 라우트에는 `meetingReservationRoutes.reserve` → `MeetingReserveRoute`만 있다. 목록·상세 라우트가 없고, `MeetingReservationListPage`는 feature `index.ts`에서 export되지 않는다(상세만 이번에 추가).

### 4. 상태 계약 불일치

`model/reservation.ts`의 `MEETING_RESERVATION_STATUS`는 4종(`PENDING_APPROVAL`, `APPROVED`, `EXPIRED`, `CANCELED`)이고, UI는 `REJECTED`·`COMPLETED`를 더한 6종을 `ui/parts/reservationStatus.ts`에서 소유한다. Figma STEP05·STEP06 정의서가 6종을 명시하므로 model을 6종으로 확장하는 것이 맞다.

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
- 화면 확인 수단에 대해 사용자에게 세 가지 안(A: fixture 프리뷰 라우트 / B: Logic 전체 구현 / C: 현행 유지)을 제시했고 **아직 선택되지 않았다.** A는 `src/pages/meeting-reservation`·`src/app/routing.ts`로의 scope 확장 승인이 필요하다.
- Figma 채널은 `hgkguilr`로 이번 세션에서 연결에 성공했다. 다음 세션에서도 같은 채널로 시도하고, 실패할 때만 사용자에게 새 채널을 요청한다.

## 소유권과 Git 계약

- 변경 경로: `src/features/meeting-reservation/**` (커밋 `96a5e3e`, 7 files, +416/-28)
- 역할별 파일 소유권: UI가 `ui/**`와 `ui/parts/*.css`를 소유. `api/**`, `model/**`, `hook/**`, `mocks/**`는 Logic 소유
- 충돌 여부: 없음. 워킹 트리 clean
- task·branch·worktree: `task/reservation-detail-ui` / 분기 기준 `sy-main` / `/Users/okand/SynologyDrive/asan-worktrees/reservation-detail-ui`
- branch 계약의 `asan-role`은 `ui`, `asan-scope`는 `src/features/meeting-reservation`과 세션 로그 경로뿐이다. Logic이 라우팅까지 손대려면 `scope-proposal → update-scope`로 `src/app/routing.ts`, `src/pages/meeting-reservation` 승인이 필요하다
- Git 통합 담당자: claude
- 산출물 책임: owner (필수 8종 작성 완료)
- merge 상태: **미병합**. `sy-main` 병합 승인은 아직 받지 않았다

## 관련 경로와 스킬

- `.agent-policy/common/skills/policy/task-role-routing/references/logic.md`
- `.agent-policy/common/skills/policy/git-branch-strategy/SKILL.md`
- `src/features/meeting-reservation/api/meetingReservation.api.ts`, `.dto.ts`, `.parser.ts`
- `src/features/meeting-reservation/mocks/handlers.ts`, `src/app/mocks/browser.ts`, `src/app/mocks/startMocks.ts`
- `src/app/routing.ts`, `src/shared/config/meetingReservationRoutes.ts`
- `src/pages/meeting-reservation/ui/MeetingReserveRoute.tsx` (route ↔ hook ↔ page 연결 참고 구현)
- Figma 채널 `hgkguilr` / 프레임: STEP02 `10:3458`, STEP03 `10:3616`, STEP04 `10:3687`, STEP05 `10:3754`, STEP06 `10:3828`, STEP07 `10:3920`, STEP08 `10:3982`

## 명령어 및 결과

| 명령 | 결과 |
| --- | --- |
| `npx vitest run src/features/meeting-reservation/ui/` | 24 passed (신규 9 포함) |
| `npm run lint` | 통과 |
| `tsc -b` / `npm run build` | 통과 |
| `npm run test` | 533 passed / **6 failed** |

6개 실패는 전부 `citizen-participation`(`api/http/citizenParticipation.api.test.ts` 1, `mocks/handlers.test.ts` 3, `pages/.../CitizenResultRoutes.test.tsx` 2)이며 MSW `onUnhandledRequest: "error"` 전략과 현재 msw 버전의 bypass 동작 충돌로 보인다. 이번 변경 이전부터 존재하는 실패이고 변경 파일과 의존 관계가 없다. **전체 테스트가 이미 빨간 상태라 새 회귀 신호가 묻힌다는 점을 Logic 세션에서 먼저 고려할 것.**

## 실행하지 않은 검증

- 브라우저 실제 렌더 확인(라우트·데이터 없음)
- 목록 페이지·카드의 표시 회귀 테스트(해당 테스트가 저장소에 없음)
- 「Figma 대조 결과」의 12개 차이 수정
- `sy-main` 병합과 사후 검증

## 다음 조치

1. 「Figma 대조 결과」를 사용자와 함께 검토하고, UI 수정 범위를 먼저 확정한다. 5번(참여 예정 인원)과 11·12번(취소 확인·완료 팝업)은 props와 API 계약을 바꾸므로 Logic 착수 전에 결정하는 것이 좋다.
2. `--role logic` 세션을 새로 시작하고 이 문서와 현재 브랜치 상태를 함께 읽는다.
3. 서버 계약을 확인하고 「화면별 API 요청·응답 DTO 추정」과 대조한다. 차이가 있으면 그 섹션을 실제 계약으로 갱신한 뒤 DTO·parser·api·hook을 구현한다.
4. 상태 6종을 `model/reservation.ts`로 확장한다(현재 4종).
5. 목록·상세·취소·예약 제한 MSW 핸들러를 추가한다. 상태 6종과 빈 값·오류·로딩을 모두 재현할 수 있는 목 데이터를 권장한다.
6. 라우트를 등록하고 상세·목록 페이지에 props를 연결한다. scope 확장 승인이 필요하다.
7. 이 브랜치의 `sy-main` 병합 여부를 사용자에게 확인한다(현재 미병합).
