# Agora RTC 통신 계약

## 문서 범위

현재 프론트엔드가 `agora-rtc-sdk-ng`를 통해 Agora와 직접 주고받는 값만 다룬다. 기준 SDK 버전은 `4.24.6`이다. 회의 메타데이터 API와 RTC Token 생성은 회사 서버의 책임이며 [회사 회의 API 계약](meeting-api-contract.md)에서 설명한다.

## 공통 타입

### UID

```ts
type AgoraUid = number | string
```

Agora SDK의 `UID`도 `number | string`이다. API 응답과 SDK 이벤트의 표현 차이를 없애기 위해 Map key와 발언자 비교에서는 역할이 확인된 `localUid`, `remoteUid`, `participantUid`를 문자열로 변환한다.

### RTC Credential

```ts
type RtcCredential = {
  appId: string
  channelName: string
  localUid: AgoraUid
  token: string
  tokenExpiresAt: string
}
```

| 필드 | Agora 전달 위치 | 설명 |
|---|---|---|
| `appId` | `client.join` 1번째 인자 | Agora 프로젝트 식별자 |
| `channelName` | `client.join` 2번째 인자 | 입장할 RTC 채널 |
| `localUid` | `client.join` 4번째 인자 | 현재 브라우저 사용자가 채널 안에서 사용할 식별자 |
| `token` | `client.join` 3번째 인자 | 해당 채널과 UID에 발급된 RTC Token |
| `tokenExpiresAt` | Agora에 직접 전달하지 않음 | 프론트 표시 및 서버 credential 정보 |

`appId`, `channelName`, 서버 응답의 `uid` 또는 `agoraUid`, `token`은 회사 서버에서 받는다. 파싱 후 서버 UID 필드는 `localUid`로 정규화한다. App Certificate는 프론트로 전달하거나 Agora `join`에 포함하지 않는다.

## 프론트에서 Agora로 보내는 호출

### RTC Client 생성

```ts
AgoraRTC.createClient({
  mode: 'rtc',
  codec: 'vp8',
})
```

| 파라미터 | 타입 | 현재 값 | 설명 |
|---|---|---|---|
| `mode` | SDK mode | `'rtc'` | 다자간 화상회의 통신 모드 |
| `codec` | SDK codec | `'vp8'` | 영상 코덱 |

반환값은 `IAgoraRTCClient`이며 Hook 수명주기 동안 하나의 ref로 유지한다.

### 채널 입장

```ts
const joinedLocalUid = await client.join(
  credential.appId,
  credential.channelName,
  credential.token,
  credential.localUid,
)
```

| 순서 | 파라미터 | 타입 | 출처 |
|---|---|---|---|
| 1 | `appId` | `string` | 회사 서버 RTC credential |
| 2 | `channelName` | `string` | 회사 서버 RTC credential |
| 3 | `token` | `string` | 회사 서버 RTC credential |
| 4 | `localUid` | `number \| string` | 회사 서버 응답의 `uid` 또는 `agoraUid`를 파싱한 값 |

반환값은 실제 입장에 사용된 `UID`다. 현재 구현은 이 값을 화면의 `localUid`로 저장한다. 별도의 회의 객체나 channel ID는 반환되지 않는다.

### 로컬 Track 생성

```ts
const [audioTrack, videoTrack] =
  await AgoraRTC.createMicrophoneAndCameraTracks()
```

| 반환 순서 | 타입 | 용도 |
|---|---|---|
| 1 | `IMicrophoneAudioTrack` | 마이크 오디오 송출 |
| 2 | `ICameraVideoTrack` | 카메라 영상 송출 및 로컬 미리보기 |

현재 구현은 별도 config를 전달하지 않아 SDK 기본 장치와 기본 encoder 설정을 사용한다. 호출 시 브라우저의 카메라·마이크 권한 요청이 발생할 수 있다.

### 로컬 Track 송출

```ts
await client.publish([audioTrack, videoTrack])
```

파라미터는 `IMicrophoneAudioTrack | ICameraVideoTrack` 배열이다. 성공 반환값은 `void`이며, 원격 클라이언트에는 `user-published` 이벤트가 전달된다.

### 원격 Track 구독

```ts
const remoteAudioTrack = await client.subscribe(remoteUser, 'audio')
const remoteVideoTrack = await client.subscribe(remoteUser, 'video')
```

| 파라미터 | 타입 | 설명 |
|---|---|---|
| `remoteUser` | `IAgoraRTCRemoteUser` | 이벤트로 받은 원격 사용자 |
| `mediaType` | `'audio' \| 'video'` | 구독할 Track 종류 |

오디오 Track은 `audioTrack.play()`로 즉시 재생한다. 비디오 Track은 UID별 DOM container가 준비되면 `videoTrack.play(container)`로 재생한다.

### 발언 음량 감지 활성화

```ts
client.enableAudioVolumeIndicator()
```

채널 입장 후 매번 호출한다. 활성화하면 Agora가 약 2초마다 `volume-indicator` 이벤트를 발생시킨다.

### RTC Token 갱신

```ts
await client.renewToken(refreshedRtcCredential.token)
```

`token-privilege-will-expire` 이벤트에서 회사 서버로 새 credential을 요청한 뒤 새 `token: string`만 Agora에 전달한다. App ID, channelName, UID는 변경하지 않는다.

### 송출 해제와 퇴장

```ts
await client.unpublish(localTracks)
await client.leave()
```

`unpublish`에는 현재 소유한 로컬 Track 배열을 전달한다. `leave`는 인자 없이 호출하며 둘 다 `Promise<void>`를 반환한다. 정리 중 일부 호출이 실패해도 장치 Track 해제와 나머지 정리를 계속한다.

### 로컬 Track 제어

| 호출 | 파라미터 | 반환 | 설명 |
|---|---|---|---|
| `track.setEnabled(enabled)` | `boolean` | `Promise<void>` | 마이크 또는 카메라 송출 상태 변경 |
| `videoTrack.play(container)` | `HTMLElement` | `void` | 로컬·원격 영상 DOM 재생 |
| `audioTrack.play()` | 없음 | `void` | 원격 오디오 재생 |
| `track.stop()` | 없음 | `void` | 재생·캡처 중지 |
| `track.close()` | 없음 | `void` | 장치와 Track 자원 해제 |

## Agora에서 프론트로 받는 이벤트

### 이벤트 목록

| 이벤트 | Payload | 발생 의미 | 현재 처리 |
|---|---|---|---|
| `connection-state-change` | `(currentState, previousState, reason?)` | RTC 연결 상태 변경 | 재연결·연결 완료·비정상 종료 처리 |
| `user-joined` | `(user)` | 원격 사용자가 채널 입장 | UID를 원격 참가자 목록에 추가 |
| `user-published` | `(user, mediaType, config?)` | 원격 사용자가 Track 송출 | audio/video subscribe 및 재생; config는 미사용 |
| `user-unpublished` | `(user, mediaType, config?)` | 원격 Track 송출 중지 | audio/video 상태와 Track 제거; config는 미사용 |
| `user-left` | `(user, reason)` | 원격 사용자가 채널 퇴장 | 참가자·영상·발언 상태 제거; reason은 현재 미사용 |
| `volume-indicator` | `({ uid, level }[])` | 사용자별 음량 보고 | 60 초과 UID를 발언자로 표시 |
| `token-privilege-will-expire` | 없음 | RTC Token 만료 임박 | 회사 서버에서 새 Token을 받아 갱신 |
| `token-privilege-did-expire` | 없음 | RTC Token 만료 완료 | RTC 오류 상태 표시 |

### 연결 상태 Payload

```ts
type ConnectionState =
  | 'DISCONNECTED'
  | 'CONNECTING'
  | 'RECONNECTING'
  | 'CONNECTED'
  | 'DISCONNECTING'
```

```ts
type ConnectionStatePayload = {
  currentState: ConnectionState
  previousState: ConnectionState
  reason?: ConnectionDisconnectedReason
}
```

현재 구현은 다음 상태만 별도 처리한다.

- `RECONNECTING`: 화면 상태를 `joining`으로 변경
- `CONNECTED`: 로컬 Track이 있으면 `joined`로 변경
- `DISCONNECTED`: `reason !== 'LEAVE'`이면 비정상 종료로 판단하고 세션 정리

### 원격 사용자 Payload

SDK의 `IAgoraRTCRemoteUser`에서 현재 사용하는 필드는 다음과 같다.

```ts
type AgoraRemoteUserData = {
  uid: AgoraUid
  audioTrack?: IRemoteAudioTrack
  videoTrack?: IRemoteVideoTrack
  hasAudio: boolean
  hasVideo: boolean
}
```

`uid`는 Agora SDK가 정한 외부 필드명이므로 변경할 수 없다. 이벤트 adapter에서 `remoteUser.uid`를 `remoteUid` 인자로 전달하며, 프론트 상태에는 SDK 객체 전체를 저장하지 않고 다음 형식으로 정규화한다.

```ts
type RemoteParticipant = {
  remoteUid: AgoraUid
  hasAudio: boolean
  hasVideo: boolean
}
```

실제 `IRemoteVideoTrack`은 UID별 ref Map에서 별도로 관리한다.

### 발행 이벤트 Payload

```ts
type MediaType = 'audio' | 'video' | 'datachannel'

type UserPublishedPayload = {
  remoteUser: IAgoraRTCRemoteUser
  mediaType: MediaType
}
```

현재 구현은 `audio`와 `video`만 구독한다. `datachannel`은 타입에는 포함되지만 별도 처리를 하지 않는다.

SDK의 `user-published`와 `user-unpublished` callback은 세 번째 선택 인자인 `config?: IDataChannelConfig`도 제공한다. 현재 프론트 listener는 data channel을 처리하지 않으므로 이 값을 받지 않는다.

### 사용자 퇴장 Payload

```ts
type UserLeftPayload = {
  remoteUser: IAgoraRTCRemoteUser
  reason: 'Quit' | 'ServerTimeOut' | 'BecomeAudience' | string
}
```

SDK는 `reason`을 두 번째 인자로 전달하지만 현재 구현은 `remoteUser.uid`만 사용한다. 따라서 정상 퇴장, network timeout, audience 전환을 UI 상태에서 구분하지 않는다.

### 음량 이벤트 Payload

```ts
type ParticipantVolume = {
  participantUid: AgoraUid
  level: number
}
```

`level`은 0부터 100 사이의 정수다. 현재 기준은 `level > 60`이며 여러 사용자가 동시에 기준을 넘으면 모두 발언자로 처리한다.

## 데이터 처리 흐름

```text
회사 서버 response
  → RtcCredential의 localUid로 파싱
  → client.join(appId, channelName, token, localUid)
  → 현재 사용자의 Agora UID 반환
  → local Track 생성 및 publish
  → Agora user/Track/volume/Token 이벤트
  → meeting 도메인 action
  → RemoteParticipant 및 participantSpeakerUidKeys 상태
  → 영상 타일과 발언자 테두리 갱신
```

## 현재 사용하지 않는 SDK 데이터

| 데이터 | 상태 | 확장 시 용도 |
|---|---|---|
| `connection-state-change.previousState` | callback에서 받지만 미사용 | 상태 전이 원인 분석 |
| `user-left.reason` | 미사용 | 정상 퇴장과 timeout 구분 |
| publish/unpublish `config` | 미사용 | data channel 설정 |
| `IAgoraRTCRemoteUser.dataChannels` | 미사용 | Agora data channel |
| `IAgoraRTCRemoteUser.audioTrack/videoTrack` | 직접 저장하지 않음 | 현재는 subscribe 반환 Track을 별도 Map에 저장 |

## 보안 경계

- App Certificate는 회사 서버에만 보관하고 프론트로 전달하지 않는다.
- 프론트는 RTC Token을 생성하지 않고 서버 응답의 Token만 Agora에 전달한다.
- `tokenExpiresAt`은 프론트 관리용 시각이며 `client.join` 파라미터가 아니다.
- Agora는 `appId`, `channelName`, UID, `token` 조합을 검증하므로 서버 response에서 파싱한 `localUid`를 임의로 변경하면 안 된다.

## 구현 위치

| 책임 | 파일 |
|---|---|
| RTC 세션 입장·퇴장 | `src/features/meeting/hooks/useAgoraMeeting.ts` |
| 로컬 Track 생성·제어 | `src/features/meeting/hooks/useAgoraLocalMedia.ts` |
| 원격 Track과 참가자 상태 | `src/features/meeting/hooks/useAgoraParticipants.ts` |
| Agora 이벤트 Payload 변환 | `src/features/meeting/services/agoraClientEvents.ts` |
| 발언자 음량 판정 | `src/features/meeting/model/activeSpeaker.ts` |
