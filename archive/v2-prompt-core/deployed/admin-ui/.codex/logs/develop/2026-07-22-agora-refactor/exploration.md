# 탐색 기록

## 스킬 확인
- 확인: orchestration, harness, publishing, coding-convention, validation, hook-extraction, documentation, review-checklist, styles, data-fetch, data-dto

## 재사용 자산 탐색
- 탐색 범위: `src/components/`, `src/hooks/`, `src/App.tsx`, `src/App.css`, `src/index.css`, `package.json`
- 발견한 재사용 자산: `App.tsx`의 `VITE_API_BASE_URL` 환경변수 계약과 AbortController 기반 fetch 패턴
- 재사용 제안: API base URL 계약은 유지하고 회의 API 어댑터로 이동한다.
- 신규 선택 근거: `src/components/`와 `src/hooks/`가 없고 기존 화면은 API 연결 확인만 담당한다.

## SDK 검증
- Agora Web SDK `join`은 `Promise<UID>`를 반환한다.
- `uid`가 null이면 Agora가 숫자 UID를 배정해 반환한다.
- 송출은 local track 생성 후 `publish`, 수신은 `user-published`에서 `subscribe` 후 `play`가 필요하다.
- 만료 전 이벤트에서 새 토큰을 받아 `renewToken`한다.

## 리스크 / 제약
- 실제 저장소는 React 19, Vite 8, npm 기반으로 운영 문서의 버전/명령과 다르다. 실제 `package.json`을 기준으로 검증한다.
- RTC 트랙은 leave/unmount 시 stop/close하지 않으면 카메라와 마이크 점유가 남는다.
- 브라우저 미디어 권한과 실제 Agora 자격 증명 없이는 완전한 2인 통화 검증이 불가능하다.

## 실제 서버 API 확인
- 공통 응답은 `{ success, code, status, message, data, timestamp }` envelope이다.
- 생성: `POST /v1/api/admin/agora/meetings`, 필수 `title`, `hostUserSeq`; 유효시간은 `scheduledEnd`, 이미지는 `thumbnailUrl`이다.
- 초대 참가: `POST /v1/api/admin/agora/meetings/invite/:code/join`, body는 `{ userSeq }`이다.
- 내부 meeting seq 참가: `POST /v1/api/admin/agora/meetings/:id/join`이며 Token 재발급에도 같은 응답을 사용한다.
- 성공 `data`는 `meeting` 객체와 최상위 `appId`, `uid`, `role`, `rtcToken`, `expiresAt`으로 구성된다.
- 현재 인증 연동 전이므로 `hostUserSeq/userSeq`를 요청 body에 전달해야 한다.

## 발언자 감지 탐색
- 재사용 자산: `useAgoraMeeting`의 Agora listener 수명주기와 `MeetingStage`의 `VideoTile`을 그대로 사용한다.
- 설치된 Agora SDK 4.24.6 타입 선언에서 `enableAudioVolumeIndicator()`와 `volume-indicator` 이벤트를 확인했다.
- 이벤트는 로컬·원격 UID와 0~100 음량을 2초마다 제공하며 SDK는 60 초과를 일반적인 발언 기준으로 안내한다.
- SDK API에는 보고 주기 인자가 없으므로 별도 오디오 분석이나 타이머를 추가하지 않는다.

## 통신 데이터 계약 탐색
- 설치된 Agora Web SDK 버전은 4.24.6이다.
- 프론트는 Agora client 생성, join, publish, subscribe, Token 갱신, unpublish, leave를 직접 호출한다.
- 구독 이벤트는 연결 상태, 사용자 입퇴장, publish/unpublish, 음량, Token 만료 8종이다.
- 회사 API는 생성, 초대 코드 참가, 회의 ID join 3개 POST endpoint를 사용한다.
- 생성 응답은 meeting과 flat credential을 결합하고, 초대 참가 응답은 credential-only 형식을 지원한다.
- credential의 `uid/agoraUid`, `rtcToken/token`, meeting 위치의 `channelName` fallback을 지원한다.

## 명명 경계 탐색
- 기존 결합 타입과 `session` 변수는 Meeting 데이터, Channel 접근 정보, RTC 연결 생명주기를 혼동시켰다.
- API 요청은 `payload`, 응답은 `data`로만 불려 호출부에서 방향을 판별하기 어려웠다.
- 내부 `RtcCredential.uid`와 `RemoteParticipant.uid`가 동일한 이름이라 현재 사용자와 원격 사용자를 구분하기 어려웠다.
- Agora SDK 원본의 `uid` 필드는 변경할 수 없으므로 event adapter에서 역할별 내부 이름으로 변환하는 것이 적절하다.
