# 회사 회의 API 계약

## 문서 범위

현재 프론트엔드가 회사 웹서버에 보내는 request와 실제 코드가 해석하는 response 형식을 다룬다. 서버의 전체 내부 DTO가 아니라 현재 구현과 contract test에서 확인되는 필드가 기준이다.

## 공통 요청 설정

### Base URL

```bash
VITE_API_BASE_URL=https://api.example.com
```

프론트는 URL 끝의 `/`와 Swagger 경로 `/docs`를 제거한 값을 API origin으로 사용한다. 환경 변수가 없으면 요청 전에 오류를 발생시킨다.

### Header

```http
Content-Type: application/json
Authorization: Bearer <accessToken>
```

`Content-Type`은 항상 포함한다. `Authorization`은 사용자가 입력한 Access Token을 trim한 결과가 있을 때만 포함한다. 현재 인증 미연동 상태를 지원하기 위해 Access Token은 선택값이다.

### 공통 응답 Envelope

```ts
type MeetingApiResponse<TResponseData> = {
  success: boolean
  code: number
  status: number
  message: string
  data: TResponseData
  timestamp: string
}
```

현재 코드는 HTTP `response.ok`로 성공 여부를 판단하고 JSON의 `data`를 파싱한다. `success`, `code`, `status`, `timestamp` 값 자체를 별도로 검증하지 않는다.

| Envelope 필드 | 타입 | 현재 프론트 사용 |
|---|---|---|
| `success` | `boolean` | 별도 검증하지 않음 |
| `code` | `number` | 별도 검증하지 않음 |
| `status` | `number` | 별도 검증하지 않음; HTTP status는 `response.ok`로 판단 |
| `message` | `string` | 오류 response 메시지 후보 |
| `data` | endpoint별 객체 | 회의와 RTC credential 파싱 |
| `timestamp` | ISO 8601 `string` | 현재 미사용 |

## Endpoint 목록

| 기능 | Method | Endpoint | Request body | Response |
|---|---|---|---|---|
| 회의 생성 및 개설자 credential 발급 | `POST` | `/v1/api/admin/agora/meetings` | `CreateMeetingRequest` | `CreateMeetingResponse` |
| 초대 코드 참가 | `POST` | `/v1/api/admin/agora/meetings/invite/:code/join` | `JoinMeetingRequest` | `JoinMeetingResponse` |
| 회의 ID 참가·Token 재발급 | `POST` | `/v1/api/admin/agora/meetings/:id/join` | `RefreshRtcTokenRequest` | `RefreshRtcTokenResponse` |

Path parameter인 초대 코드와 회의 ID는 `encodeURIComponent`로 인코딩한다.

### Request/Response 명명 경계

웹서버로 보내거나 웹서버에서 받은 타입과 변수에는 각각 `Request`, `Response`를 붙인다.

```ts
type MeetingAccessResponse = RtcCredentialResponse & {
  meeting: MeetingResponse
}

type CreateMeetingResponse = MeetingApiResponse<MeetingAccessResponse>
type JoinMeetingResponse = MeetingApiResponse<MeetingAccessResponse | RtcCredentialResponse>
type RefreshRtcTokenResponse = JoinMeetingResponse
```

`meetingApiResponse`, `meetingResponse`, `rtcCredentialResponse`는 아직 서버 필드명을 유지하는 경계 데이터다. 파서가 검증과 변환을 마친 뒤에는 `MeetingWithRtcCredential`, `meetingAccess`, `meeting`, `rtcCredential`처럼 `Response`를 제거한다.

## 회의 생성

### Request

```http
POST /v1/api/admin/agora/meetings
```

```ts
type CreateMeetingRequest = {
  title: string
  description?: string
  thumbnailUrl?: string
  mode: 'video'
  hostUserSeq: string
  scheduledEnd: string
}
```

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `title` | `string` | 예 | trim된 회의 제목 |
| `description` | `string` | 아니오 | trim 결과가 있을 때만 포함 |
| `thumbnailUrl` | `string` | 아니오 | 대표 이미지 URL |
| `mode` | `'video'` | 예 | 현재 고정값 |
| `hostUserSeq` | `string` | 예 | 개설자 회사 사용자 Seq |
| `scheduledEnd` | ISO 8601 `string` | 예 | 현재보다 미래인 회의 만료 시간 |

요청 예시:

```json
{
  "title": "프로젝트 회의",
  "description": "주간 진행 상황 공유",
  "thumbnailUrl": "https://example.com/meeting.jpg",
  "mode": "video",
  "hostUserSeq": "2",
  "scheduledEnd": "2026-07-22T06:00:00.000Z"
}
```

### Response

생성 응답은 `data.meeting`과 `data` 최상위의 RTC credential을 결합한다.

```json
{
  "success": true,
  "code": 0,
  "status": 201,
  "message": "SUCCESS",
  "data": {
    "meeting": {
      "seq": "9",
      "publicId": "meeting-public-id",
      "channelName": "meeting-channel",
      "title": "프로젝트 회의",
      "description": "주간 진행 상황 공유",
      "thumbnailUrl": "https://example.com/meeting.jpg",
      "inviteCode": "INVITE01",
      "mode": "video",
      "hostUserSeq": "2",
      "scheduledStart": "2026-07-22T00:00:00.000Z",
      "scheduledEnd": "2026-07-22T06:00:00.000Z",
      "startedAt": null,
      "endedAt": null,
      "maxParticipants": 16,
      "status": "scheduled",
      "createdAt": "2026-07-22T00:00:00.000Z",
      "updatedAt": "2026-07-22T00:00:00.000Z"
    },
    "appId": "agora-app-id",
    "uid": "3141791090",
    "role": "host",
    "rtcToken": "rtc-token",
    "expiresAt": "2026-07-22T01:00:00.000Z"
  },
  "timestamp": "2026-07-22T00:00:00.000Z"
}
```

## 초대 코드 참가

### Request

```http
POST /v1/api/admin/agora/meetings/invite/:code/join
```

```ts
type JoinMeetingRequest = {
  userSeq: string
}
```

| 값 | 위치 | 타입 | 설명 |
|---|---|---|---|
| `code` | path | `string` | trim 후 대문자로 정규화한 초대 코드 |
| `userSeq` | body | `string` | 참가자 회사 사용자 Seq |

```json
{
  "userSeq": "8"
}
```

### Credential-only Response

현재 contract test가 고정하는 초대 참가 응답 형식이다.

```json
{
  "success": true,
  "data": {
    "channelName": "meeting-channel",
    "appId": "agora-app-id",
    "agoraUid": "2718281828",
    "token": "invite-token",
    "expiresAt": "2026-07-22T02:00:00.000Z"
  }
}
```

회의 객체가 없으면 프론트는 다음 임시 회의 정보를 생성한다.

```ts
{
  meetingId: `invite:${inviteCode}`,
  channelName: credential.channelName,
  title: '초대 코드 회의',
  inviteCode,
  status: 'ready',
  expiresAt: credential.tokenExpiresAt,
}
```

## RTC Token 갱신

### 생성 경로로 입장한 회의

```http
POST /v1/api/admin/agora/meetings/:id/join
```

```ts
type RefreshRtcTokenRequest = {
  userSeq: string
}
```

`:id`에는 생성 응답의 `meeting.seq`를 정규화한 `meetingId`가 들어간다. 응답에서 새 RTC Token을 얻어 Agora `client.renewToken`에 전달한다.

### 초대 코드 경로로 입장한 회의

별도 회의 ID가 없으므로 Token 만료 임박 시 초대 코드 참가 endpoint를 동일한 `userSeq`로 다시 호출한다.

### 개발용 JSON 경로

서버 요청 없이 기존 credential을 반환한다. 따라서 실제 만료된 Token을 갱신할 수 없으며 개발 검증 전용이다.

## 서버 Response 필드

### Meeting 필드

| 서버 필드 | 타입 | 프론트 처리 | 정규화 결과 |
|---|---|---|---|
| `seq` | `string` | 필수 | `meeting.meetingId` |
| `publicId` | `string` | 선택 | `meeting.publicId` |
| `channelName` | `string` | 필수 | `meeting.channelName`, credential fallback |
| `title` | `string` | 필수 | `meeting.title` |
| `description` | `string` | 선택 | `meeting.description` |
| `thumbnailUrl` | `string` | 선택 | `meeting.representativeImageUrl` |
| `inviteCode` | `string` | 필수 | `meeting.inviteCode` |
| `status` | `string` | 필수 | `meeting.status` |
| `scheduledEnd` | `string \| null` | 선택 | `meeting.expiresAt` |
| `mode` | `string` | 현재 미사용 | 없음 |
| `hostUserSeq` | `string` | 현재 미사용 | 없음 |
| `scheduledStart` | ISO 8601 `string \| null` | 현재 미사용 | 없음 |
| `startedAt` | ISO 8601 `string \| null` | 현재 미사용 | 없음 |
| `endedAt` | ISO 8601 `string \| null` | 현재 미사용 | 없음 |
| `maxParticipants` | `number \| null` | 현재 미사용 | 없음 |
| `createdAt` | ISO 8601 `string` | 현재 미사용 | 없음 |
| `updatedAt` | ISO 8601 `string` | 현재 미사용 | 없음 |

`scheduledEnd`가 없거나 `null`이면 RTC credential의 `expiresAt`을 회의 만료 시간 fallback으로 사용한다.

### RTC Credential 필드

| 서버 필드 | 허용 타입 | 필수 | 정규화 결과 |
|---|---|---|---|
| `appId` | `string` | 예 | `rtcCredential.appId` |
| `channelName` | `string` | 조건부 | `rtcCredential.channelName` |
| `uid` | `string \| number` | `agoraUid`와 택일 | `rtcCredential.localUid` |
| `agoraUid` | `string \| number` | `uid`와 택일 | `rtcCredential.localUid` |
| `rtcToken` | `string` | `token`과 택일 | `rtcCredential.token` |
| `token` | `string` | `rtcToken`과 택일 | `rtcCredential.token` |
| `expiresAt` | `string` | 예 | `rtcCredential.tokenExpiresAt` |
| `role` | `string` | 현재 미사용 | 없음 |

`channelName`이 credential 위치에 없으면 `meeting.channelName`을 fallback으로 사용한다.

## 프론트 정규화 결과

```ts
type MeetingWithRtcCredential = {
  meeting: {
    meetingId: string
    publicId?: string
    channelName?: string
    title: string
    description?: string
    inviteCode: string
    status: string
    expiresAt: string
    representativeImageUrl?: string
  }
  rtcCredential: {
    appId: string
    channelName: string
    localUid: number | string
    token: string
    tokenExpiresAt: string
  }
}
```

이 형식이 `MeetingPage`에서 `meetingAccess`로 사용되고, 내부 `rtcCredential`이 `useAgoraMeeting.joinRtcChannel`에 전달된다. 이 객체는 RTC 연결 세션이 아니라 회의 정보와 현재 사용자의 채널 접근 인증을 결합한 데이터다.

## 오류 Response 처리

HTTP 응답이 `response.ok === false`이면 JSON에서 다음 순서로 메시지를 찾는다.

1. `message: string`
2. `error: string`
3. `'알 수 없는 오류가 발생했습니다.'`

성공 HTTP 응답이더라도 필수 meeting 또는 RTC credential 필드를 찾지 못하면 다음 오류를 발생시킨다.

```text
회의 API 성공 응답에서 RTC 접속 정보를 찾을 수 없습니다.
```

응답 body가 비어 있거나 JSON 파싱에 실패하면 `null`로 처리한 뒤 같은 오류 경계를 사용한다.

## 개발용 Legacy JSON

개발용 JSON 입력은 공통 envelope 전체, `data` 객체, 또는 다음 normalized 형식을 지원한다.

```json
{
  "meeting": {
    "meetingId": "meeting-100",
    "title": "개발 회의",
    "inviteCode": "INVITE01",
    "status": "ready",
    "expiresAt": "2026-07-22T06:00:00.000Z"
  },
  "rtcCredential": {
    "appId": "agora-app-id",
    "channelName": "meeting-channel",
    "localUid": "100001",
    "token": "rtc-token",
    "tokenExpiresAt": "2026-07-22T01:00:00.000Z"
  }
}
```

Legacy 형식의 필수 meeting 필드는 `meetingId`, `title`, `inviteCode`, `status`, `expiresAt`이다. 필수 credential 필드는 `appId`, `channelName`, `localUid`, `token`, `tokenExpiresAt`이다. 기존 개발 JSON의 `uid`도 입력 호환을 위해 파서에서만 허용한다.

## 서버 책임과 프론트 비포함 영역

다음 항목은 현재 request body에 포함되지 않으며 회사 서버가 결정하거나 검증해야 한다.

- Access Token 유효성, 정지 계정 여부와 사용자 식별
- 회의 생성 가능 개수와 참가 가능 인원
- 초대 코드 유효성, 회의 상태와 유효기간
- 참가자별 Agora UID 결정
- App Certificate를 이용한 RTC Token 서명
- RTC 역할, Token 만료와 권한 만료 정책
- Agora Webhook 기반 ACTIVE, EMPTY, ENDED 상태 처리

## 구현과 테스트 위치

| 책임 | 파일 |
|---|---|
| HTTP 요청과 endpoint | `src/features/meeting/services/meetingApi.ts` |
| 응답 검증과 정규화 | `src/features/meeting/services/meetingApiParser.ts` |
| TypeScript 도메인 타입 | `src/features/meeting/types.ts` |
| 생성·초대 응답 contract test | `tests/meetingApi.test.ts` |
