# 구현 로그

## 작업 요약
- Agora Web SDK 기반 단일 화상회의 페이지를 구현했다.
- 실제 서버 API 생성, 초대 코드 참가, 개발용 JSON 입장 경로를 모두 같은 `MeetingWithRtcCredential` 계약으로 연결했다.
- RTC 수명주기는 `useAgoraMeeting` 훅에서 관리하고 UI 컴포넌트는 Agora SDK를 import하지 않도록 분리했다.

## 재사용 자산
- 기존 `VITE_API_BASE_URL` 환경변수 계약을 유지해 회의 API 서비스에서 사용했다.
- 기존 `src/components/`, `src/hooks/` 재사용 후보는 없었다.
- 설치된 `agora-rtc-sdk-ng`, `lucide-react`만 사용했고 package.json은 수정하지 않았다.

## 신규 파일 / 수정 파일
- 신규: `src/features/meeting/types.ts`
- 신규: `src/features/meeting/model/meetingForms.ts`
- 신규: `src/features/meeting/services/meetingApi.ts`
- 신규: `src/features/meeting/hooks/useAgoraMeeting.ts`
- 신규: `src/features/meeting/components/MeetingPreparationPanel.tsx`
- 신규: `src/features/meeting/components/MeetingStage.tsx`
- 신규: `src/features/meeting/MeetingPage.tsx`
- 수정: `src/App.tsx`
- 수정: `src/App.css`
- 수정: `src/index.css`
- 수정: `README.md`

## 핵심 로직
- `meetingApi.ts`는 공통 envelope와 에러 응답을 `unknown`으로 받은 뒤 안전하게 좁혀 파싱한다.
- 실제 서버 응답의 `envelope.data.meeting.seq`를 `meetingId`로 정규화하고, RTC flat credential(`appId`, `uid`, `rtcToken`, `expiresAt`)을 `rtcCredential`로 매핑한다.
- 기존 normalized `{ meeting, rtcCredential }` JSON은 개발용 JSON 입장 호환을 위해 계속 지원한다.
- `meetingForms.ts`는 제출 전 사용자 Seq 필수 검증, title trim 검증, 미래 만료시간 검증, 초대 코드 uppercase trim을 담당한다.
- `useAgoraMeeting.ts`는 단일 Agora client ref, local track refs, remote video track refs, 이벤트 listener 등록/해제를 관리한다.
- active attempt id와 owner guard로 leave/unmount/new join이 이전 join continuation을 무효화한다.
- `join()`이 반환한 실제 UID를 로컬 세션 상태에 반영한다.
- join 전 listener를 등록하고, join 후 마이크/카메라 track 생성, local video play, publish 순서로 입장한다.
- `client.join`, local track 생성, publish 각 await 이후 현재 attempt인지 검사하고 stale이면 cleanup 후 return한다.
- `user-published`, `user-unpublished`, `user-left`에서 원격 참가자 UI 상태와 track play/cleanup을 처리한다.
- `token-privilege-will-expire`는 refresh callback 후 `renewToken`을 호출하고, `did-expire`는 명확한 오류 상태로 전환한다.
- leave/unmount/join 실패는 unpublish best effort, track stop/close, client.leave, listener off를 같은 cleanup 경로로 수행한다.

## 검증 / 요청 처리
- API base 미설정, 사용자 Seq 누락, 비정상 JSON, 비정상 API 응답을 사용자 오류 메시지로 노출한다.
- Access token은 선택값으로 처리하고 값이 있을 때만 Authorization Bearer 헤더를 추가한다.
- 실제 생성 API는 `POST /v1/api/admin/agora/meetings`, 초대 참가 API는 `POST /v1/api/admin/agora/meetings/invite/:code/join`, 토큰 갱신은 `POST /v1/api/admin/agora/meetings/:id/join`을 사용한다.
- 오류 영역은 `aria-live`로 연결했다.
- 마이크/카메라 버튼은 `aria-pressed`와 44px 이상 컨트롤 크기를 적용했다.
- 활성 회의 중에는 다른 생성·참가 요청을 막아 화면 세션과 실제 RTC 채널의 불일치를 방지한다.
- joining 중에는 나가기 버튼도 비활성화한다.
- 미디어 장치 토글 실패는 Promise rejection으로 방치하지 않고 오류 영역에 표시한다.
- desktop은 준비 rail + stage, mobile은 stack + sticky controls 구조로 구성했다.

## 리스크
- 실제 Agora appId/token 및 브라우저 미디어 권한 없이는 실제 송수신까지 로컬에서 완전 검증할 수 없다.
- 개발용 JSON 경로의 토큰 갱신은 붙여넣은 credential을 재사용하므로 실제 만료 갱신 검증에는 API 경로가 필요하다.
- 원격 다자 연결은 실제 두 개 이상의 브라우저 세션 또는 장치가 있어야 최종 확인 가능하다.

## 핸드오프 메모
- watcher 리뷰 준비 완료.

## 통합 검토 반영
- joined/joining/leaving 상태에서는 create/join/json 준비 액션을 disable하고 submit handler에서도 차단했다.
- Agora `client.join` 반환 UID를 `localUid`로 설정하도록 수정했다.
- 마이크/카메라 `setEnabled` 실패를 훅 내부 `errorMessage`로 노출하도록 처리했다.
- `localUid`가 `0`일 때도 UID로 표시되도록 null 비교로 수정했다.

## Watcher fail 수정 라운드
- join/leave race 방지를 위해 `activeAttemptRef`, `ownerAttemptRef`를 추가했다.
- leave/unmount/new join 시작 시 이전 attempt를 무효화하고, join async continuation은 await 이후마다 attempt를 확인한다.
- stale attempt는 cleanup 후 return하며, 새 attempt가 이미 owner이면 stale cleanup이 새 세션을 건드리지 않도록 guard를 둔다.
- 실제 서버 API 계약을 반영해 endpoint, payload, envelope parser, 오류 message 처리, 사용자 Seq 필수 입력, 선택 Access token 처리를 수정했다.
- 기존 `.env.local`의 Swagger `/docs` URL은 API 요청 전에 server origin으로 정규화한다.
- README를 실제 API 계약 기준으로 갱신했다.
- 검증: `npm run lint` pass, `npm run build` pass. Build는 Agora SDK 단일 chunk 크기 경고를 유지한다.

## 초대 참가 응답 수정
- 실제 초대 참가 성공 응답은 회의 객체 없이 `channelName`, `appId`, `agoraUid`, `token`, `expiresAt`을 반환하는 credential-only 구조임을 확인했다.
- 생성 응답의 `meeting.channelName`과 초대 응답의 최상위 `channelName`을 모두 지원하도록 RTC credential parser를 확장했다.
- 초대 참가 세션은 초대 코드 기반 최소 회의 메타데이터를 구성하고 즉시 Agora `join()`으로 전달한다.
- 초대 참가자의 토큰 갱신은 임시 meeting id를 사용하지 않고 동일 초대 코드 참가 API를 다시 호출한다.
- 성공 응답을 해석하지 못한 경우 서버의 `SUCCESS` 문구 대신 RTC 정보 누락 오류를 표시한다.
- `tests/meetingApi.test.ts`에 생성 응답과 초대 참가 응답 파서 회귀 테스트를 추가했다.
- 검증: `npm test`, `npm run lint`, `npm run build` pass.

## Agora 발언자 강조
- `activeSpeaker.ts`에 음량 임계값 판정, UID 정규화·중복 제거, 상태 동등성 비교를 분리했다.
- 채널 입장마다 `enableAudioVolumeIndicator()`를 활성화하고 `volume-indicator` listener를 등록했다.
- 발언 UID 목록이 실제로 바뀔 때만 React 상태를 갱신한다.
- 음소거, 원격 오디오 중단, 참가자 퇴장, 세션 cleanup에서 관련 발언 상태를 즉시 제거한다.
- 로컬·원격 `VideoTile`에 발언 상태를 전달하고 녹색 외곽 발광 효과 및 `prefers-reduced-motion` 대체 스타일을 적용했다.
- 원격 타일을 별도 `memo` 경계로 감싸 다른 참가자의 발언 상태 변경에 따른 불필요한 렌더를 막았다.
- `tests/activeSpeaker.test.ts`에서 임계값, UID 중복 제거·정렬, 목록 비교를 검증한다.
- 검증: `npm test` 4건 pass, `npm run lint` pass, `npm run build` pass.

## 회의 기능 관심사 분리 리팩터링
- 732줄 `useAgoraMeeting`을 353줄 세션 facade와 `useAgoraLocalMedia`, `useAgoraParticipants`, `agoraClientEvents`로 분리했다.
- SDK callback signature는 event adapter에 격리하고 React hook은 meeting 도메인 action만 연결한다.
- 로컬 Track 소유권과 원격 Track/DOM ref 소유권을 서로 다른 hook으로 분리했다.
- `MeetingPreparationPanel`은 접속, 생성, 초대 참가, JSON 참가, 세션 요약 섹션을 조합한다.
- `MeetingStage`는 헤더, 영상 그리드, 컨트롤 섹션을 조합한다.
- `docs/meeting-architecture.md`에 파일 책임, 입장 흐름, cleanup 순서, attempt guard, UID 정책과 확장 지점을 기록했다.
- 주석은 stale attempt 소유권과 best-effort cleanup 등 코드만으로 의도가 드러나지 않는 지점에 제한했다.

## 코드 주석 한글화
- 회의 기능과 Vite 설정에 남아 있던 영어 JSDoc 및 인라인 주석을 모두 한글로 변경했다.
- Agora SDK 메서드명과 RTC 같은 기술 식별자는 정확성을 위해 원문 표기를 유지했다.
- 영어 설명 문장 재검색 결과 잔존 항목이 없음을 확인했다.

## 기능 우선 코드 순서 및 명명
- Hook 반환 함수명을 RTC 세션, 로컬 미디어, 원격 참가자 대상을 포함하도록 변경했다.
- `meetingApi.ts`는 공개 API를 상단에 두고 응답 parser를 `meetingApiParser.ts`로 분리했다.
- parser의 공개 기능은 상단, legacy/server parser와 JSON reader는 하단에 배치했다.
- 대표 UI 컴포넌트를 내부 타일과 formatter보다 먼저 배치했다.
- 모호한 `handleChange`, `startSession`, `formatDateTime` 계열 이름을 대상과 행위가 드러나는 이름으로 변경했다.
- 전체 함수명 길이를 검사해 25자 초과 항목을 제거했다.
- `docs/code-ordering.md`에 선언 순서, 주요 기능 판단, 함수 명명과 추출 기준을 기록했다.

## 통신 데이터 계약 문서화
- `docs/agora-rtc-contract.md`에 SDK 버전, RTC credential, 호출 파라미터, 반환값, Track 타입과 이벤트 payload를 기록했다.
- Agora UID 정규화, 발언 음량 기준, Token 갱신과 프론트 참가자 상태 매핑을 기록했다.
- `docs/meeting-api-contract.md`에 base URL, header, endpoint, request body와 응답 envelope를 기록했다.
- 생성 응답과 credential-only 초대 응답 예제, 필수·선택·미사용 필드, 호환 이름과 fallback 규칙을 기록했다.
- 생성·초대·개발 JSON 경로별 Token 갱신 차이와 오류 메시지 선택 순서를 기록했다.
- README와 아키텍처 문서에서 두 계약 문서로 연결했다.
- SDK 선언과 대조해 `user-left.reason`, publish/unpublish의 선택적 `config`, 현재 미사용 SDK 데이터를 보강했다.
- 서버 응답 envelope 필드별 사용 여부와 서버 책임·프론트 비포함 영역을 명시했다.
- 검증 중 발견한 과거 결합 타입 참조를 현재 회의 접근 정보 계약으로 통일했다.

## 회의 접근 정보와 UID 역할 명명
- 회의와 RTC 인증 결합 타입을 `MeetingWithRtcCredential`, 내부 값과 props를 `meetingAccess`로 통일했다.
- 생성·참가·갱신 결과를 `createdMeetingAccess`, `joinedMeetingAccess`, `refreshedMeetingAccess`로 구분했다.
- 서버 경계 타입과 값에 `Request` 또는 `Response`를 붙이고 파싱 후 내부 모델에서는 접미사를 제거했다.
- 서버의 `uid/agoraUid`는 parser에서 `localUid`로 변환하고 원격 참가자와 공통 음량 UID는 각각 `remoteUid`, `participantUid`로 구분했다.
- 실제 RTC 연결 생명주기를 나타내는 `joinRtcChannel`, `leaveRtcSession`, `cleanupRtcSession`의 의미는 유지했다.
- 검증: `npm test` 6건, `npm run lint`, `npm run build` 통과.

## RTC 연결 상태 및 원격 참가자 동기화
- Agora 로그에서 개설자 연결이 종료됐지만 React 상태가 `joined`로 남아 있던 문제를 확인했다.
- `connection-state-change`를 구독해 재연결 중 상태를 표시하고, 비정상 `DISCONNECTED`에서는 RTC 자원을 정리한 뒤 오류 상태로 전환한다.
- `user-joined`를 구독해 publish 여부와 무관하게 채널 참가자를 원격 인원에 반영한다.
- join 완료 직후 `client.remoteUsers`를 동기화해 기존 참가자 이벤트의 타이밍 누락을 보완한다.
- 신규 listener는 기존 cleanup 경로에서 모두 해제한다.
- 실제 브라우저 검증: userSeq 2 / UID 3141791090과 userSeq 8 / UID 3024640890이 동일 채널에서 양쪽 모두 원격 1명 및 상대 영상 수신에 성공했다.
- 검증: `npm test`, `npm run lint`, `npm run build` pass.
