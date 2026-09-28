# 회의 입장 Logic 구현 계획

## 결론과 승인

기존 `/meeting`의 Agora hook·토큰 발급·갱신·참여자·발화자·트랙 정리를 재사용해 UI 인계의 L1~L10을 연결한다. 사용자는 새 브랜치 분기와 구현을 승인했고, 서버 명세가 없으므로 페이지 요구 DTO와 기존 API·JSON을 이용한 임시 구현을 허용했다. 역할은 inject `logic`으로 확인했다.

- 요청 목적: 정상적인 Agora 사용과 코드 인증부터 회의 종료까지의 서비스 흐름을 UI에 연결한다.
- UI 인계: 프로젝트 기본 checkout의 `.claude/logs/sessions/2026-09-11-ui-16994a1e/handoff.md`.
- 기본 project: `/Users/okand/SynologyDrive/asan-metaverse-user-ui`.
- 구현 branch·worktree: `task/meeting-entry-logic` / `/Users/okand/SynologyDrive/asan-worktrees/meeting-entry-logic`.
- 직접 부모: `task/meeting-entry-ui`, 분기 HEAD `39f8c443dd5c98b3001220941936bffe25de35fd`.
- 브랜치 생성: 보호 작업 `ac9e46b6304f488284b70659a1e718bd`를 사용자 `명령 실행 승인` 후 실행했다. 구현 36파일은 별도 승인된 보호 작업 `a261832deaaef788e7f63b285edffcf9`로 `a3a50f0`에 커밋했다. 2026-09-16에는 승인된 보호 작업 `c8f7691f7cbd4659ab50d1b9ae23e285`로 직접 부모 `task/meeting-entry-ui`에 fast-forward 병합하고, UI worktree에서 lint·build 및 회의·예약·라우팅 테스트 310개 통과를 확인했다. 두 branch·worktree는 유지하며 sy-main 통합과 push는 수행하지 않았다.
- 부모에 있던 D5 미커밋 3파일은 부모를 변경하지 않고 자식에 동일하게 반영한다.
- 산출물은 이 Codex 세션 경로에 기록하며 다른 세션 기록은 수정하지 않는다.

## 재사용 근거와 변경 범위

| 구간 | 확인한 기존 자산 | 연결 방법 |
| --- | --- | --- |
| 인증·화면 | `AuthRouteBoundary`, `meetingReservationRoutes`, `pages/meeting-reservation` | 인증 경계 안에 `/meeting/rooms/:roomName/{code,confirm,device-check,room,end}`를 연결한다. |
| 입장 | `MeetingPage`, `MeetingAccessService`, `meeting.hardcoded`, `useApi` | 토큰 요청·갱신을 재사용하고 예약 입장 상태를 별도 hook으로 조율한다. |
| 장치·RTC | `useAgoraMeeting`, `useAgoraLocalMedia`, `useAgoraParticipants`, `agoraClientEvents`, `rtcSessionCleanup`, `activeSpeaker` | 장치별 미리보기와 입장 후 송출을 확장한다. SDK 수명주기 구현은 유지한다. |
| 예약 DTO·임시 데이터 | `meetingReservationRead.dto`, `mocks/fixtures.ts` | 기존 승인 예약 JSON을 기반으로 현재 시각의 검증 시나리오를 만든다. |
| UI | `RoomCodeEntryPage`, `CodeMeetingConfirmPage`, `DeviceCheckView`, `MeetingRoomView`, 팝업 4종, `MeetingEndPage` | 기존 props와 callback에 상태·API·트랙을 연결한다. |
| 시간 | `date.util` | 서울 시간 표시와 T-5/T/T+50/T+60 판정을 연결한다. |

임시 `POST /api/meeting-entry`는 validate/enter/connected/heartbeat/leave/chat 요청과 예약·참여자·메시지·서버 시각 응답을 검증한다. 개발 서버 메모리에서 자리 확보, 20초 연결 만료, 최초 입장, 명시적 최종퇴실, 최근 200개 메시지를 처리한다. 운영 API 계약·로그인 사용자 매핑·보관 정책이 확정되면 이 경계를 교체한다.

STEP18 3D NPC는 인계 범위 밖이다. 현재 확인 화면의 입장 동작이 시간 대기와 실제 입장으로 이어지고, 중간 퇴장은 확인 화면, 최종퇴실·종료 확인은 예약 목록으로 연결한다. 해당 목적지는 임시 연결이다. 미확정 사유 문구 8종도 임시 문구로 표시한다.

## 수행 항목

- [x] 프로젝트와 연결 worktree의 실제 branch·HEAD·dirty 및 부모 관계를 확인해 기존 변경을 보존한다.
- [x] 자식 worktree에서 승인된 D5를 반영하고 기존 훅의 장치별 생성·송출·정리를 확장한다.
- [x] 자식의 API·model·server에 임시 DTO와 요청 처리를 구성해 코드·정원·중복·시간·재입장 규칙을 연결한다.
- [x] 자식의 hook·pages·routing에서 화면 전환과 영상·참여자·채팅을 연결한다.
- [x] 기존 배치의 회귀 테스트, lint, build와 실제 개발 서버 HTTP 검증으로 변경 동작을 확인한다.
- [x] 실제 검증 결과, 임시 계약, 실행 방법과 미확인 사항을 `final-summary.md`에 기록한다.

브라우저 캡처·시각 QA는 요청이 없어 수행하지 않는다. 실제 두 기기의 Agora 통화는 토큰 발급 또는 SDK 대역 테스트와 구분해 보고한다.

## 2026-09-16 entry-ui Prettier 작업

- 사용자가 sy-main 병합 전에 `entry-ui` 관련 Prettier 작업을 요청했다. 대상은 `/Users/okand/SynologyDrive/asan-worktrees/meeting-entry-ui`, branch `task/meeting-entry-ui`, HEAD `a3a50f0`이다.
- 기준 `sy-main`의 `63eda3b` 대비 entry 변경 파일 57개를 프로젝트 `.prettierrc`로 검사하고 포맷 차이가 있는 파일만 반영한다. 기존 설정은 들여쓰기 2칸, `printWidth: 160`, 세미콜론 사용이다.
- [x] 기존 설정과 소스 상태를 확인하고 npm 캐시의 Prettier 3.9.6으로 결과를 생성해 34개 파일에 패치로 반영했다. package·lock·Prettier 설정은 변경하지 않았다.
- [x] 대상 57개 Prettier 검사, 적용 결과 34개 대조, `npm run lint`, `git diff --check`를 모두 통과했다. 기능 변경이나 신규 테스트는 추가하지 않았다.
- 사용자 승인 후 보호 작업 `6a044c60e4761952cd41c6ed6449a781`로 포맷 변경 34개를 `764c2a1b33acec645aef611dcc098180956e8239`에 커밋했다. 메시지는 `style: 회의 입장 UI와 로직의 코드 포맷 정리`이며, 작업 종료 코드 0 및 `done`, UI worktree clean을 확인했다. sy-main의 다른 팝업 작업은 여전히 미커밋이며 사용자가 정한 순서에 따라 해당 작업 커밋 후 entry 병합을 재개한다.
