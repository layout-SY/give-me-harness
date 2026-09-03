# Meeting Frontend Architecture

## 목적

회사 회의 API가 발급한 RTC credential을 Agora Web SDK에 전달하고, 브라우저의 미디어 트랙과 참가자 UI를 안전하게 동기화한다. 회의 메타데이터와 인증 정책은 회사 서버가 소유하며 프론트엔드는 App Certificate나 RTC Token 생성 책임을 갖지 않는다.

상세 데이터 형식은 [Agora RTC 통신 계약](agora-rtc-contract.md)과 [회사 회의 API 계약](meeting-api-contract.md)을 참고한다.

## 디렉터리 책임

```text
src/features/meeting/
├── MeetingPage.tsx                 # API 진입과 화면 조합
├── components/
│   ├── MeetingPreparationPanel.tsx # 준비 섹션 조합
│   ├── MeetingStage.tsx            # 회의 섹션 조합
│   ├── preparation/                # 접속, 생성, 참가, JSON, 회의 접근 정보 요약
│   └── stage/                      # 헤더, 영상 그리드, 미디어 컨트롤
├── hooks/
│   ├── useAgoraMeeting.ts          # RTC 세션 facade
│   ├── useAgoraLocalMedia.ts       # 로컬 장치와 Track 소유권
│   └── useAgoraParticipants.ts     # 원격 참가자와 발언 상태
├── model/                          # 순수 검증과 상태 변환
├── services/
│   ├── meetingApi.ts               # 회사 API adapter
│   ├── meetingApiParser.ts         # API 응답 parser
│   └── agoraClientEvents.ts        # Agora 이벤트 adapter
└── types.ts                        # 회의 도메인 계약
```

## 입장 흐름

1. `MeetingPage`가 생성, 초대 코드 또는 개발 JSON으로 `MeetingWithRtcCredential`을 얻어 `meetingAccess`로 관리한다.
2. `useAgoraMeeting.joinRtcChannel`이 이전 RTC 연결을 정리하고 join attempt ID를 발급한다.
3. `agoraClientEvents`를 등록한 뒤 credential의 appId, channelName, token, localUid로 `client.join`을 호출한다.
4. `useAgoraLocalMedia`가 마이크와 카메라 Track을 생성하고 로컬 미리보기를 재생한다.
5. Agora client가 Track을 publish한다.
6. `user-published` 이벤트는 원격 Track을 subscribe하고 `useAgoraParticipants`에 전달한다.

## 상태 소유권

### useAgoraMeeting

- 연결 상태, 오류, 로컬 Agora UID를 소유한다.
- join, reconnect, leave, token 만료와 전체 cleanup 순서를 조정한다.
- SDK 이벤트나 DOM 영상 컨테이너의 상세 구현은 직접 소유하지 않는다.

### useAgoraLocalMedia

- 마이크·카메라 Track ref와 활성 상태를 소유한다.
- Track 생성, 로컬 재생, 토글, stop/close를 담당한다.
- 생성만 됐지만 publish되지 못한 stale Track도 동일한 release 함수로 정리한다.

### useAgoraParticipants

- 원격 참가자 presence와 audio/video publish 상태를 소유한다.
- 원격 video Track과 DOM container를 UID 문자열로 매핑한다.
- `volume-indicator` 결과로 계산한 발언 UID를 보관한다.

### agoraClientEvents

- Agora SDK callback을 meeting 도메인 action으로 변환한다.
- 원격 subscribe/play와 RTC Token 갱신을 처리한다.
- React 상태 setter와 UI 컴포넌트를 직접 참조하지 않는다.

## 중요한 불변식

### Join attempt guard

`join`, 장치 권한 요청, `publish`는 각각 비동기 단계다. 사용자가 중간에 나가거나 새 입장을 시작할 수 있으므로 각 `await` 뒤에서 현재 attempt ID를 확인한다. 오래된 continuation은 자신이 아직 client owner일 때만 cleanup할 수 있다.

### Cleanup 순서

1. Agora listener 해제
2. publish된 로컬 Track unpublish
3. 로컬 Track stop/close
4. 원격 Track과 DOM ref 제거
5. Agora channel leave
6. React 표시 상태 초기화

일부 cleanup이 실패해도 다음 단계는 계속 수행한다. 카메라와 마이크 점유를 남기지 않는 것이 우선이다.

### UID 정규화

Agora UID는 문자열 또는 숫자다. 서버 response의 `uid` 또는 `agoraUid`는 파싱 후 현재 사용자의 `localUid`가 된다. SDK 원격 사용자 UID는 `remoteUid`, 음량 이벤트처럼 양쪽을 포함할 수 있는 UID는 `participantUid`로 명명한다. Map과 발언자 비교에서는 `String(participantUid)`를 사용해 API response와 SDK callback의 표현 차이를 흡수한다.

### Meeting, Channel, RTC Session

- `Meeting`은 회사 서버에 저장되는 지속적인 회의 정보다.
- `Channel`은 Agora에서 참가자들이 실제로 미디어를 송수신하는 공간이다.
- `MeetingWithRtcCredential`은 회의 정보와 현재 사용자의 채널 접근 인증을 결합한 데이터이며 세션이 아니다.
- RTC session은 한 브라우저가 `join()`한 뒤 `leave()`할 때까지의 연결 생명주기다. Token을 갱신해도 같은 RTC session이 유지된다.

## 발언자 표시

채널 입장 후 `enableAudioVolumeIndicator()`를 호출한다. SDK가 2초마다 제공하는 0~100 음량 중 60 초과 UID를 발언자로 판정한다. UID 집합이 실제로 바뀔 때만 React 상태를 갱신하며, 음소거·unpublish·퇴장·세션 종료 시 강조 상태를 제거한다.

## 확장 지점

- 장치 선택 및 화면 공유: `useAgoraLocalMedia`
- 참가 권한, 정렬 및 발언 기록: `useAgoraParticipants`
- 신규 Agora callback: `agoraClientEvents`
- 서버 DTO 변경: `meetingApi` parser와 contract test
- UI 추가: `components/preparation` 또는 `components/stage` 내부 도메인 컴포넌트

회의 화면 외부에서 두 번째 소비자가 생기기 전에는 이 모듈을 전역 공용 RTC abstraction으로 승격하지 않는다.
