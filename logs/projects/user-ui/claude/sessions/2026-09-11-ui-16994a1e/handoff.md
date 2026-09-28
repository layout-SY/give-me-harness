# 코드 입장·회의실 UI → Logic 인계 (STEP14~16·19~24)

## Assignment 이동

- 보내는 host·session·role: Claude Code / `2026-09-11-ui-16994a1e` / `ui`
- 받는 host·session·제안 role: Logic 세션 / `logic`

## 역할 라우팅

- 요청 역할(`requested_roles`): ui, logic
- 확인된 역할(`confirmed_roles`): ui (inject `--role ui`)
- 완료 역할(`completed_roles`): ui (STEP14 코드 입력, STEP15 코드 확인, STEP16 입장불가 팝업, STEP19 대기 팝업, STEP20 장치 점검, STEP21 이용 안내 팝업, STEP22 회의실, STEP23 최종퇴실 확인 팝업, STEP24 회의 종료)
- 다음 제안 역할(`next_role`): logic — 제안이며 권한 부여가 아니다.
- 역할 판단 근거: 남은 작업은 route 연결, 입장 Validation API, RTC·장치 hook, 시간 판정, 채팅으로 모두 Logic 범위다.
- 사용자 확인(2026-09-14): "2번 방식으로 진행 되어야 해" — `task/meeting-reserve-room-slot` 전례처럼 Logic 세션이 이 branch를 이어받아 UI·Logic을 함께 완성한 뒤 sy-main에 병합한다.

## 목표 및 현재 상태

- branch·worktree: `task/meeting-entry-ui` / `/Users/okand/SynologyDrive/asan-worktrees/meeting-entry-ui`
- HEAD: `39f8c44` (Merge branch 'sy-main' into task/meeting-entry-ui)
  - `7f5753e` feat : 코드 입장·대기·종료 모바일 UI를 구현한다
  - `ac24c19` feat : 예약 회의 장치 점검·회의실·팝업 모바일 UI를 구현한다
  - `39f8c44` sy-main(`63eda3b`, 회의실별 예약 폼·토론 API) 부모 동기화. 충돌 없음
- 미커밋 변경: 없음. D5(입장 코드 영문·숫자) 수정은 아래 "인계 이후 경과"를 따른다.
- Figma: `가상오피스` 페이지. STEP19~23은 데스크톱 기준이라 항목 구성만 참고하고 레이아웃은 `/meeting` 모바일 셸(`src/features/meeting/ui/meeting.css`)을 채택했다.
- 라우트 연결은 하지 않았다. 현재 이 컴포넌트들은 어떤 경로에도 연결되어 있지 않다.

## 인계 이후 경과 (2026-09-16 확인)

이 문서를 작성하기 전에 Logic 세션이 이미 작업을 시작했다. 아래 내용은 사후 확인 결과이며, 위 "대기 중인 작업" 표의 일부는 이미 처리되었다.

- Logic branch: `task/meeting-entry-logic` (`/Users/okand/SynologyDrive/asan-worktrees/meeting-entry-logic`), 부모는 `task/meeting-entry-ui` @ `39f8c44`
- Logic commit: `a3a50f0 feat: 기존 Agora 기반 회의 입장과 퇴실 흐름 연결` (2026-09-15, 36 files)
- 처리된 항목: L1·L2(라우트, `MeetingEntryRoute.tsx`, `meetingReservationRoutes.ts`), L3(입장 API·`useMeetingEntry`·`entryPolicy`), L5(`useMeetingDeviceCheck`·`useAgoraLocalMedia`), L6(`useAgoraMeeting` 확장). 임시 입장 서버(`server/entry/temporaryEntryService.ts`, `vite/meetingEntryPlugin.ts`)도 추가되었다.
- 남은 항목: L4(사유 코드 9종 문구 확정), L7(시간 판정 T-5/T/T+50/T+60), L8(최초 입장·재입장 기록), L9(채팅), L10(통합 테스트), STEP22 회의실 화면 연결
- D5 수정(`RoomCodeEntryPage.tsx`·`.test.tsx`·`meeting-entry.css`)은 Logic 세션이 `a3a50f0`에 동일 내용으로 커밋했다. 이미 병합된 `ReserveCompletePopup.tsx`의 "숫자 10자리" 문구도 그 커밋에서 "영문·숫자 10자리"로 정리되었다.
- 따라서 이 branch의 미커밋 변경은 내용이 같음을 diff로 확인한 뒤 `git restore`로 되돌렸다. UI worktree는 `39f8c44` 기준 clean이며, 최신 D5 내용은 자식 branch에 있다.
- 완료 병합 순서: `task/meeting-entry-logic` → `task/meeting-entry-ui` → `sy-main`. UI branch와 worktree는 직접 부모이므로 그 전에 정리하지 않는다.

## 사용자 결정

| # | 결정 |
| --- | --- |
| D1 | STEP19~23은 Figma 데스크톱 대신 `/meeting` 모바일 UI를 그대로 채택한다. |
| D2 | ADM 프레임(STEP09~13·25~31)은 user 프로젝트에서 별도 화면을 만들지 않는다. 사용자 대응 화면(목록·상세·상태)은 이미 구현되어 있고, 승인·반려·일정 관리는 관리자 전용이다. |
| D3 | STEP16 입장불가 사유는 Figma 원문이 ACTIVE_SESSION_CONFLICT 1종뿐이라, 문구를 props로 주입하고 기본값만 그 1종으로 둔다. |
| D4 | STEP22 참여자 목록과 채팅은 영상 아래 탭으로 전환한다(공용 `Tabs`). |
| D5 | 입장 코드는 숫자 전용이 아니라 **영문·숫자 조합 10자리**다. `inputMode="text"`, placeholder `영문·숫자 10자리 코드를 입력하세요`, `autoCapitalize="characters"`. 대소문자 정규화는 UI에서 하지 않는다. |

## 완료된 UI 작업

### 코드 입장 흐름 — `src/features/meeting-reservation/ui/entry/`

| 컴포넌트 | STEP | 주요 props / callback |
| --- | --- | --- |
| `RoomCodeEntryPage` | 14 | `themeLabel`, `code`, `errorMessage`, `isSubmitting`, `isSubmitDisabled`, `onCodeChange`, `onSubmit`, `onBack` |
| `CodeMeetingConfirmPage` | 15 | `meetingName`, `themeLabel`, `dateLabel`, `timeRangeLabel`, `reserverName`, `agenda`, `isEntering`, `onEnter`, `onBack` |
| `EntryDeniedPopup` | 16 | `open`, `close`, `reasonLabel`, `guide`, `description`, `onConfirm` |
| `EntryWaitPopup` | 19 | `open`, `close`, `startLabel`, `onConfirm` |
| `MeetingEndPage` | 24 | `meetingName`, `themeLabel`, `dateLabel`, `timeRangeLabel`, `onConfirm` |
| `EntryGuideSection` | 공용 | `title`, `description`(`\n` 유지), `emphasis` |

- 화면 고정 문구(입장 가능 시간, 코드 안내, 종료 처리 안내 등)는 UI가 소유한다. 값이 아니라 정책 안내라 호출부가 내려 주지 않는다.
- `RoomCodeEntryPage`는 `입장하기` 버튼과 폼 submit(키패드 완료)이 같은 `onSubmit`을 호출한다. `isSubmitting`·`isSubmitDisabled`면 호출하지 않는다.
- `CodeMeetingConfirmPage`의 Agenda는 비면 `미입력`으로 표시한다.

### 회의실 흐름 — `src/features/meeting/ui/room/`

| 컴포넌트 | STEP | 주요 props / callback |
| --- | --- | --- |
| `DeviceCheckView` | 20 | `meetingName`, `themeLabel`, `timeRangeLabel`, `nickname`, `cameraEnabled`, `micEnabled`, `cameraUnavailable`, `micUnavailable`, `networkQuality`(`stable`\|`normal`\|`unstable`), `isSpeakerTesting`, `isProceeding`, `previewRef`, `onToggleCamera`, `onToggleMic`, `onTestSpeaker`, `onNext` |
| `MeetingEntryNoticePopup` | 21 | `open`, `close`, `onConfirm` |
| `MeetingRoomView` | 22 | `meetingName`, `themeLabel`, `timeRangeLabel`, `remainingTimeLabel`, `endTimeLabel`, `stateLabel`, `participants`, `maxParticipants`(기본 10), `bindVideoContainer`, `chatMessages`, `chatDraft`, `isChatSending`, `micEnabled`, `cameraEnabled`, `isLeaving`, `onChatDraftChange`, `onChatSend`, `onToggleMic`, `onToggleCamera`, `onLeave` |
| `MeetingExitConfirmPopup` | 23 | `open`, `close`, `isExiting`, `onContinue`, `onFinalExit` |
| `RoomVideoGrid`, `RoomHeader`, `roomMeta.ts` | 공용 | `RoomParticipant`, `RoomChatMessage` 타입 export |

- `RoomParticipant`: `{ id, nickname, roleLabel, statusLabel?, isLocal?, micEnabled, cameraEnabled, isSpeaking? }`
- `bindVideoContainer(participantId, element)`로 참여자별 영상 컨테이너를 넘긴다. `previewRef`는 장치 점검 미리보기용이다.
- 남은시간은 계산하지 않고 `remainingTimeLabel` 문자열을 그대로 표시한다.
- 탭 선택(참여자/채팅)만 UI 내부 state이며, 나머지 상태는 전부 props다.
- 회의실 전용 토큰은 `.meeting-app` 범위에서만 유효하므로 `DeviceCheckView`·`MeetingRoomView`는 `<main className="meeting-app">` 안에서 렌더한다. 팝업은 전역 토큰만 쓴다.

### 공용 변경

- `src/shared/assets/icons/error.icon.tsx` 신규. 기존 `ReservationRestrictedPopup`의 인라인 경고 아이콘을 승격했고, 해당 파일은 import만 바꿨다.
- export: `src/features/meeting-reservation/index.ts`, `src/features/meeting/index.ts`
- 기존 `/meeting`(`MeetingPage`, `stage/**`) 파일은 수정하지 않았다.

## 대기 중인 작업 (Logic)

| # | 파일 | 작업 |
| --- | --- | --- |
| L1 | `src/shared/config/meetingReservationRoutes.ts`, `src/app/routing.ts`, `routing.test.ts` | 코드 입장·회의실 경로를 추가한다. 예약 폼의 `roomName` 규칙에 맞춰 `/meeting/rooms/:roomName/code`, `/confirm`, `/device-check`, `/room`, `/end`를 제안한다(경로명은 사용자 확인 필요). 팝업 4종은 경로를 갖지 않고 부모 라우트가 상태로 연다. |
| L2 | `src/pages/meeting-reservation/ui/**` 또는 신규 `pages/meeting-room/**` | 각 화면의 route 컴포넌트를 만들고 props를 연결한다. 배치 위치는 Logic 세션이 판단한다. |
| L3 | `features/meeting-reservation/api`·`hook` | 입장 Validation API. 순서: 10자리 형식 → 코드 존재·상태 → 승인완료 → 현재 테마 일치 → T-5~T+60 → 재입장 제한 → 다른 활성 세션 → 현재 활성인원 < 10. 성공 시 STEP15로 이동, 실패 시 `EntryDeniedPopup`을 연다. |
| L4 | `features/meeting-reservation/model` | 사유 코드 9종(INVALID_CODE / WRONG_ROOM / TOO_EARLY / CANCELED / EXPIRED / CAPACITY_FULL / REENTRY_BLOCKED / DUPLICATE_SESSION / ACTIVE_SESSION_CONFLICT)을 `reasonLabel`·`guide`·`description`으로 매핑한다. ACTIVE_SESSION_CONFLICT 외 8종 문구는 미확정이라 사용자 확인이 필요하다. |
| L5 | `features/meeting/hook/**` | 장치 점검: 카메라·마이크 권한 요청(기본 OFF), `previewRef`에 로컬 트랙 연결, 권한 거부·장치 미존재 시 `cameraUnavailable`·`micUnavailable`, 스피커 테스트음, 네트워크 품질 측정. |
| L6 | `features/meeting/hook/agora/**` | 회의실 RTC. 기존 `useAgoraMeeting`·`useAgoraParticipants` 재사용 여부를 판단하고, `RoomParticipant`(닉네임·참여 유형)와 Agora uid를 매핑한다. 발화자 판정은 기존 `activeSpeaker` 사용. |
| L7 | 시간 판정 hook | T-5(대기공간 입장), T(회의 입장), T+50(최종퇴실 확인), T+60(종료)을 판정한다. `remainingTimeLabel`·`endTimeLabel` 문자열 생성, T 도달 전 NPC 상호작용 시 `EntryWaitPopup`, 나가기 시 T+50 기준으로 중도퇴실/`MeetingExitConfirmPopup` 분기, T+60에 `MeetingEndPage`. |
| L8 | 예약 세션 상태 | 예약 세션별 최초 입장 여부를 기록해 STEP20·21을 1회만 노출하고 재입장 시 건너뛴다. 네트워크 단절·앱 종료는 최종퇴실로 처리하지 않는다. |
| L9 | 채팅 | 송수신 연결. 저장 여부·보관기간이 미확정이라 "저장 완료" 류 문구를 추가하지 않는다. |
| L10 | 테스트 | route 매칭, 입장 Validation 분기별 팝업, 최초 입장·재입장 분기, 시간 분기, 채팅 전송. |

## 결정 사항 및 제약 조건

- `DESIGN.md`: 새 색상·뷰포트 분기를 추가하지 않았다. 기존 토큰과 `color-mix`만 사용했다.
- 신규 팝업 셸은 기존 `Popup` + `vo-complete`(예약 계열) / `meeting-popup`(회의실 계열)을 재사용했다.
- STEP17(보류), STEP18(3D NPC)은 범위 밖이다.
- STEP21의 최종 CTA 원문과 STEP24 확인 후 이동 경로는 Figma에서도 미확정이다.
- 이미 병합된 `ReserveCompletePopup.tsx:30`과 `MeetingReservationDetailPage.tsx:58`에 "숫자 10자리" 문구가 남아 있다. D5와 어긋나므로 정리가 필요하다(사용자 판단 대기).

## 소유권과 Git 계약

- UI 변경 경로(이 세션): `src/features/meeting-reservation/ui/entry/**`, `src/features/meeting/ui/room/**`, `src/shared/assets/icons/error.icon.tsx`, `src/features/meeting-reservation/ui/ReservationRestrictedPopup.tsx`(import만), 두 feature `index.ts`
- Logic 작업 경로(L1~L10): `src/app/routing.ts`, `routing.test.ts`, `src/shared/config/**`, `src/pages/**`, `src/features/meeting-reservation/{api,hook,model,mocks}/**`, `src/features/meeting/{api,hook,lib,model}/**`
- 충돌 여부: L1~L10은 위 UI 파일을 수정하지 않는다.
- 승인된 Git 작업: worktree·branch 생성, 커밋 2건, sy-main 부모 동기화 병합. 모두 실행 완료.
- 남은 Git 작업: D5 미커밋 변경 commit, L1~L10 완료 후 sy-main 완료 병합과 worktree 정리. 별도 승인 필요.
- 산출물 책임: owner

## 명령어 및 결과 (worktree)

- `npm ci`: 519 packages
- `npm run lint`: 통과
- `npm run build`: 통과 (기존 500kB 청크 경고만)
- `npm run test -- src/features/meeting-reservation src/features/meeting src/pages/meeting-reservation`: 36 files, 221 tests 통과 (부모 동기화 전)
- `npm run test` 전체(부모 동기화 후): 690 통과 / 13 실패. 전부 `citizen-participation`이며 이 세션 변경과 무관하다.
  - 투표 관련 5건: 동기화 전에도 실패. sy-main 기본 checkout에서도 동일하게 실패한다.
  - `browserHandlers.test.ts` 토론 MSW 8건: sy-main(`63eda3b`)에서 따라온 실패. 깨끗한 sy-main checkout에서 단독 실행해도 8건 모두 실패한다.

## 실행하지 않은 검증

- 브라우저 시각 확인(사용자 요청 없음). 라우트가 없어 아직 화면을 띄울 수 없다.
- L1~L10 반영 후의 통합 테스트

## 다음 조치

1. Logic: 남은 L4·L7·L8·L9·L10과 STEP22 회의실 화면 연결. STEP16 사유 문구 8종은 사용자 확인 후 확정한다.
2. 통합 후 `npm run lint`, `npm run build`, 회의 관련 vitest 재실행.
3. 완료 병합 승인 → `task/meeting-entry-logic` → `task/meeting-entry-ui` → `sy-main` 순서로 병합하고 worktree를 정리한다.
