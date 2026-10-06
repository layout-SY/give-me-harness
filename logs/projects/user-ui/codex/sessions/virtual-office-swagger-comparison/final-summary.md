# 가상 오피스 API 비교 결과

현재 예약 기반 입장 흐름은 제공된 8개 서버 연산을 직접 호출하지 않는다. 단일 임시 입장 API의 통합 스냅샷을 별도 세션·입장·참여자·채팅 조회로 나누는 controller 변경이 필요하다. RTC 자격 증명과 영상·장치 계층은 기존 계약을 재사용할 수 있는 부분이 많다. 변경량은 URL 교체보다 크지만 RTC 전체 재작성으로 판단할 근거는 없다.

## 분석 기준과 제한

- 기준: `sy-main`, `5df71dc0aed38ba793f5cb413b9bd2e2ce070bc1`, 현재 작업 파일. 다른 worktree는 제외.
- 서버 근거는 2026-10-04 사용자 제공 Swagger 발췌다. 직접 웹 조회는 네트워크 시간 초과로 실패했다.
- 예제의 `code: "string"`, `role: "HOST"`, `status: "INVITED"`, 숫자 10자리 코드는 전체 enum·성공 코드·검증 규칙을 확정하는 근거로 쓰지 않는다.
- 발췌는 회의실 API 8개이며 예약 생성·목록·취소·노쇼 API는 포함하지 않는다. 예약 7개 연산의 서버 일치 여부는 미확인이다.
- 소스 및 기존 문서는 변경하지 않았다. 자기 세션의 계획·분석 기록만 작성했다. 테스트·빌드·실제 서버 호출은 수행하지 않았다.

## 현재 세 가지 연결 구조

1. 예약: `features/meeting-reservation/api/meetingReservation.api.ts`의 7개 연산, 공통 Axios/ApiClient, TanStack Query, Zod parser. `VITE_API_BASE_URL_STATUS=dev`이면 MSW가 처리한다. MSW 이외 모드는 설정된 baseURL로 요청하므로 실제 실행 모드와 서버 연결 성공을 정적 분석만으로 단정하지 않는다.
2. 예약 기반 입장: `useMeetingEntry.ts`가 `/api/meeting-entry`와 `hardcodedMeetingAccessService`를 직접 호출한다. `VITE_MEETING_ACCESS_MODE`에 따른 선택을 사용하지 않는다. Vite 입장 서버와 RTC 토큰 서버를 거친다.
3. 기존 `/meeting` 화면: `getMeetingAccessService()`가 API/hardcoded를 선택한다. 서버용 경로는 `/v1/api/admin/agora/meetings` 계열 3개다. 새 발췌의 `/meeting/rooms` 계열과 경로·요청이 다르다. 기존 서버 경로의 폐기 여부는 발췌로 알 수 없다.

예약 MSW는 브라우저 메모리에 자체 records를 만들고, 임시 입장 서버는 `createEntryFixtures()`로 별도 records를 만든다. 두 구현이 fixture 생성기를 재사용해도 예약 생성·취소 상태를 공유하는 것은 아니다.

## 8개 연산 대응

| 서버 연산 | 현재 동작 | 차이와 영향 |
| --- | --- | --- |
| POST `/meeting/rooms/sessions/code` | `action: validate`, `roomName`, `code`, `viewer` 전송 | `{entryCode}`만 전송하는 계약. 반환된 숫자 `id`의 의미와 회의실 path ID 관계 확인 필요 |
| GET `/meeting/rooms/sessions/current` | 대응 조회 없음. snapshot 없이 code 이외 단계면 code로 이동 | 인증 세션 조회·복원 흐름 추가 가능. 무세션 응답과 복원 범위 확인 필요 |
| GET `/meeting/rooms/{meetingRoomId}/entry` | snapshot의 `hasEntered`와 임시 viewer 사용 | `firstEntry`, `nickname` 별도 조회. 서버에서 최초 입장을 기록하는 시점 확인 필요 |
| POST `/meeting/rooms/{meetingRoomId}/join` | 임시 토큰 발급 → enter → Agora join → connected | 토큰 발급과 입장 처리 경계 변경. 요청 본문은 발췌에 없음. 실패 보상·토큰 갱신 재호출 정책 미확인 |
| GET `/meeting/rooms/{meetingRoomId}/participants` | heartbeat 응답의 participants | 독립 조회. `uid/nickname/role/status`와 현재 `userSeq/agoraUid/nickname/role` 구조가 다름 |
| GET `/meeting/rooms/{meetingRoomId}/messages` | heartbeat 응답의 전체 messages | `afterId` 이후 증분 조회. 커서·중복 제거·정렬·최초 조회 정책 필요 |
| POST `/meeting/rooms/{meetingRoomId}/messages` | `action: chat`, 클라이언트 messageId, text, 세션 필드 → 전체 snapshot | `{content}` → 서버 ID가 있는 메시지 하나. 서버 ID 기준으로 조회 결과와 병합 필요 |
| POST `/meeting/rooms/{meetingRoomId}/leave` | `action: leave`, final, 세션 필드 → 전체 snapshot | `{finalExit}` → 문자열 data. 성공 후 로컬 정리·캐시 갱신이 필요 |

직접 연결된 서버 연산은 0/8이다. 이는 해당 기능이 없다는 뜻이 아니다. 기능 대부분은 다른 임시 계약으로 구현되어 있다. 현재 입장 API는 한 POST에 6개 action을 담고 RTC 토큰은 별도 POST다.

## DTO와 상태의 핵심 차이

### 통합 snapshot에서 분리 데이터로

현재 모든 성공 응답은 `{success:true,data:{reservation,hasEntered,participants,messages,serverNow,revision}}`이다. 새 API는 `{code,message,data}`이며 data가 연산별 객체·배열·문자열이다. 현재 `entryResponseSchema`는 성공 discriminator가 없어 새 응답을 수용하지 못한다.

controller는 snapshot 하나를 교체하는 대신 세션, 입장 전 정보, RTC 자격 증명, 참여자, 채팅을 각각 관리하거나 명시적으로 조합해야 한다. 현재 revision 비교는 분리 응답에 그대로 적용할 수 없다. 지연 응답이 다른 회의의 상태를 덮어쓰지 않는 기준도 필요하다.

공통 `ApiClient`와 mapper는 `{code:"SUCCESS",message,data}`를 이미 처리한다. 발췌의 성공 code 실제 값이 SUCCESS인지 확인해야 하며, `success` 필드가 없다는 이유만으로 공통 응답 계층이 불일치한다고 볼 수 없다.

### 식별자와 사용자

- 현재 `reservationId`는 문자열이고 임시 RTC meetingId는 `hardcoded:<code>`다. 서버 path는 integer(int64) `meetingRoomId`, 세션 응답은 숫자 `id`다. 서로 같은 개체인지 확인 없이 기존 예약 ID를 전달할 수 없다. 숫자의 실제 범위·직렬화도 계약 확인 대상이다.
- 현재 viewer는 URL의 userSeq/nickname 또는 localStorage/임의 UUID로 구성한다. 서버 요청 본문에는 viewer가 없고 응답 UID는 UUID 형태다. 사용자 식별 책임·인증 전달은 발췌만으로 확정되지 않는다.
- 임시 RTC는 `mtg-<code>` 채널과 숫자 해시 UID를 만든다. 새 join의 channelName/uid를 그대로 쓰는 연결로 변경해야 한다.
- 현재 화면은 로컬 userSeq로 본인 여부, agoraUid로 원격 프로필을 찾는다. 새 join.uid, participants.uid, messages.senderUid와 로그인 사용자 UID의 관계를 확인해야 한다.

### RTC와 시간

새 join의 `appId/channelName/uid/token/expiresAt`는 기존 `parseRtcApiResponse()`가 해석할 수 있는 payload다. `uid → localUid`, `expiresAt → tokenExpiresAt` 변환이 이미 있고 내부 AgoraUid는 string 또는 number다. 기존 Agora join은 전달받은 UID를 그대로 사용한다.

반면 `serverTime`은 기존 RTC 모델에 보존되지 않는다. 현재 controller는 snapshot.serverNow로 서버 시간 차이를 보정하므로 서버 시간은 별도 상태로 연결해야 한다. 회의 endsAt와 토큰 expiresAt도 구별해야 한다.

`hasEntered`와 `firstEntry`는 반대 개념처럼 보이지만 서버의 기록 시점이 미확정이다. 장치 검사 전 join을 호출하면 최초 입장 상태를 먼저 바꾸는지, 취소·접속 실패 시 어떻게 복구하는지 확인해야 한다. 현재 최초 입장 이력은 Agora 연결 후 connected action에서 기록된다.

### 참여자와 채팅

현재 role은 reserver/invited/code로 예약자·초대 방식까지 한 축에 섞여 있다. 서버는 role과 status를 별도로 제공하며 예제로 HOST와 INVITED가 있다. 둘을 단순 enum 치환할 수 없고 전체 값과 의미가 필요하다. 현재 임시 participants에는 연결 완료된 사용자만 들어가므로 새 목록이 초대·퇴장 사용자도 포함하는지도 확인해야 한다.

현재 채팅은 문자열 id/userSeq/senderName/text이며 발송 UUID 중복을 임시 서버에서 제거하고 최근 200개를 snapshot으로 반환한다. 서버는 숫자 id/senderUid/senderName/content/createdAt이며 GET의 afterId로 증분 조회한다. 단순 text 명칭 교체 외에 누적·중복 제거·커서·전송 재시도 의미가 달라진다. 발췌에는 클라이언트 messageId나 멱등키가 없어 기존 중복 방지 보장을 동일하게 가정할 수 없다.

## UI가 요구하지만 발췌에서 확인되지 않는 값

`MeetingEntryRoute.tsx`는 예약자명과 안건을 확인 화면에 전달한다. 현재 entryReservationSchema는 reserverUserSeq/reserverName/agenda/inviteCode/roomName/maxParticipants도 요구한다. 새 세션·entry 응답에는 이 필드들이 보이지 않는다. UI에서 계속 필요하면 데이터 출처를 확인해야 하며 임의 기본값으로 채우면 안 된다.

theme/themeName은 현재 roomName/themeName과 의미가 완전히 같은지 확인해야 한다. 코드 인증 요청에서 roomName을 보내지 않으므로 현재 WRONG_ROOM 판정의 서버 계약도 미확인이다.

## 재사용 및 변경 수준

| 영역 | 판단 |
| --- | --- |
| Agora 세션·미디어·장치 제어 | 재사용 후보. 새 자격 증명 연결 및 통합 검증 필요 |
| RTC DTO 매핑 | 변경 작음. 기존 매핑 활용 가능, serverTime 별도 처리 |
| shared ApiClient/응답 mapper | 성공 code·인증 확인 후 재사용 후보 |
| 입장 transport·DTO | 변경 큼. 8개 서버 연산과 연산별 응답으로 연결 |
| useMeetingEntry | 변경 큼. 단일 snapshot·heartbeat·enter/connected 흐름 재구성 |
| 채팅 상태 | 변경 큼. 전체 교체에서 afterId 기반 누적으로 변경 |
| 참여자 프로필·본인 판별 | 변경 중간~큼. UID 관계와 role/status 의미에 의존 |
| 표시 컴포넌트 | 기존 props를 만족할 수 있으면 재사용 가능. 예약자·안건 등 누락 데이터 결정 필요 |
| 예약 API 7개 | 발췌 범위 밖. 호환성 판정 불가 |

## 실제 연결 전 확인할 계약

1. baseURL/prefix, Bearer 또는 cookie 인증, 코드 인증 후 세션 전달 방식과 무세션 current 응답.
2. 세션 응답 id와 meetingRoomId, 기존 reservationId의 관계; join.uid/participants.uid/senderUid/로그인 UID 관계.
3. code의 성공 값·실패 코드·HTTP 상태, 전체 role/status/participantStatus enum, null·필수 필드.
4. firstEntry 기록 시점, join 재호출을 토큰 갱신에 사용해도 되는지, 장치 검사 취소·Agora 실패 시 보상 처리.
5. heartbeat/connected의 대체 동작, 비정상 연결 종료·중복 접속·최종퇴실 정책과 서버 감지 방식.
6. 코드 형식·대소문자·길이, 시작 5분 전 인증·시작 시 입장·종료 10분 전 최종퇴실·10명 제한 등 기존 가정과 서버 정책의 일치 여부.
7. 예약자명·안건·회의실 표시 정보 출처, 테마와 roomName의 관계.
8. 채팅 정렬·최초 조회·조회 한도·afterId 커서 보장·발송 재시도/중복 처리 정책, 참여자 조회 주기와 목록 포함 상태.
9. 예약 생성·조회·취소·시간 슬롯·참가자 검색·노쇼 제한의 별도 명세.

## 문서와 코드의 추가 불일치

`docs/meeting-api-contract.md`는 명시적으로 전달한 토큰만 쓴다고 설명하지만 실제 `buildMeetingApiHeaders()`는 전달 토큰이 비면 localStorage의 ACCESS_TOKEN_STORAGE_KEY를 사용한다. 이는 서버 발췌와의 차이가 아닌 로컬 문서와 코드의 차이다. 문서는 수정하지 않았다.

기존 hardcoded 생성 경로는 초대 코드를 6자리로 만들고 예약 기반 entry schema는 영문·숫자 10자리를 요구한다. 두 임시 흐름의 코드 규격이 이미 다르다. 서버 예제가 숫자 10자리라는 사실만으로 숫자만 허용한다고 단정하지 않았다.
