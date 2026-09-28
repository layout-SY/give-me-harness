# 예약 회의 UI 인계

> 작업 위치 이전 완료: 이 문서의 아래 내용은 이동 전 기록이다. 현재 브랜치는 `fix/reservation-media-check`이며, 정본 문서와 변경사항은 [handoff.md](/Users/okand/SynologyDrive/asan-worktrees/reservation-media-check/.codex/logs/sessions/reservation-media-check/handoff.md)에 있다. 원래 `sy-main`에는 다른 작업의 `useApi` 변경만 남겼다.

Logic 수정은 같은 `sy-main` 작업 공간에 미커밋 상태로 있다. 다음 UI 세션은 이 변경을 보존하고 영상 크기·격자·화자 색상·컨트롤 배치와 장치 점검 문구를 구현한다. 이 문서는 사용자가 요청한 UI 작업의 인계이며 UI 구현 완료 보고가 아니다.

## 역할과 사용자 결정

- 보내는 host·assignment·role: Codex, `2a4aa4cfd2c4457a88f62aca70458599`, `logic`.
- 받는 세션: 중앙 launcher의 새 `--role ui` 세션. host·native session은 아직 지정되지 않았다.
- `requested_roles`: Logic 수정, UI 작업 인계.
- `confirmed_roles`: `logic`(현재 inject role).
- `completed_roles`: Logic 구현·검증. UI 구현은 대기 중이다.
- `next_role`: `ui`. 새 세션의 역할 확인은 해당 inject 계약을 따른다.
- 사용자 구현 승인: 2026-09-17 `작업 진행`.
- 확정한 크기: 각 영상의 **면적을 현재의 1/4**, 가로·세로를 각각 약 절반으로 한다.
- 확정한 입장 정책: 다른 브라우저를 포함해 **재입장도 항상 장치 점검 화면을 표시**한다.
- 기본 OFF, 권한 거부·장치 미존재 시 해당 장치를 OFF로 두고 입장하는 기존 정책을 유지한다.
- 회의실 안에서는 준비한 장치의 ON/OFF만 수행한다. 권한 요청은 회의실 연결 전에 끝낸다.

## 보내는 위치와 인계 대상 작업 공간

### 작업 공간: reservation-shared

- project·저장소: `user-ui`, `/Users/okand/SynologyDrive/asan-metaverse-user-ui`.
- 보내는 위치와 목적지 branch: 모두 `sy-main`.
- worktree 절대 경로·명령 실행 디렉터리: `/Users/okand/SynologyDrive/asan-metaverse-user-ui`.
- 기존 공간이며 `git worktree list --porcelain`에서 기본 checkout임을 확인했다.
- 기준 HEAD: `71ba983e87e302578924d3be55936d729079cca0`.
- 직접 부모: 기준 브랜치 `sy-main` 자체이므로 이 작업의 상위 통합 대상 없음.
- 확인 날짜: 2026-09-17. UI 진입 직전 실제 HEAD·diff·staged·untracked 상태를 다시 확인한다. 문서의 HEAD로 되돌리지 않는다.
- 공유 이유: Logic 다음 UI가 같은 결과물을 순차로 연결한다. 새 branch·worktree 또는 역할 사이 merge가 필요하지 않다.
- 이 세션이 생성한 commit: 없음. stage·commit·branch 생성·merge 등 Git 변경 승인과 실행 없음.
- 시작 시 기존 미커밋 변경 없음. 현재 Logic 변경은 아래 여섯 소스 파일이며 모두 보존한다. 검증 종료 후 `src/shared/lib/hooks/use-api.tsx`와 `.test.tsx`의 별도 변경이 추가로 관찰되었다. 이 세션에서 작성하지 않았으며 최신 요청만 결과를 반영하는 로직·테스트 변경이다. 이를 수정·포맷·stage하지 않았다. 해당 소스를 읽은 뒤 입장·RTC hook 테스트 39개를 다시 실행해 모두 통과했으며, 별도 변경 자체의 전체 검증을 대신하지 않는다.
- staged: 없음. untracked 소스: 없음. `.codex/logs/sessions/reservation-media-check/`의 자기 문서는 `.gitignore`의 `.codex/*` 규칙에 해당한다.

| 현재 unstaged 경로 | 완료한 Logic 변경 |
| --- | --- |
| `src/features/meeting/hook/useMeetingEntry.ts` | 초 단위 갱신을 `room`으로 제한, 예약 종료 timeout 유지, 재입장 점검 강제, 점검 완료 전 다음·입장 차단, 퇴실 클릭 시 현재 시각으로 시간 정책 판정 |
| `src/features/meeting/hook/agora/useAgoraLocalMedia.ts` | 개별 장치 권한 확인 후 OFF 트랙 준비, 점검 결과 기록·퇴실 시 초기화, 실패·늦게 완료된 트랙 정리 |
| `src/features/meeting/hook/agora/useAgoraMeeting.ts` | 예약 경로의 `requireDeviceCheck` 옵션, `prepareRtcDevices`, 점검 전 RTC join 차단, 회의실에서 트랙 없는 장치 토글 시 재생성 방지 |
| `src/pages/meeting-reservation/ui/MeetingEntryRoute.tsx` | 비동기 `meeting.next()`를 void UI callback으로 연결 |
| `src/features/meeting/hook/useMeetingEntry.test.tsx` | 정적인 입장 단계의 렌더 횟수, 재입장·새 로컬 상태, 권한 대기, 예약 종료와 남은시간 검증 |
| `src/features/meeting/hook/agora/useAgoraMeeting.test.tsx` | 양쪽·한쪽 허용/거부, OFF 트랙 재사용, 점검 전 입장 차단, 재점검·오류·이탈 검증 |

## 확인된 데이터·callback 계약

- `useMeetingEntry`가 `useAgoraMeeting({ requireDeviceCheck: true })`를 사용한다. 기존 `/meeting`의 기본 Agora 동작과 구분한다.
- `enter()`는 `device-check`로 이동한 다음 `prepareRtcDevices()`를 기다린다. 이 동안 `meeting.busy`와 `rtc.isMediaStarting`으로 장치 버튼·다음을 막는다.
- `next()`는 재점검 완료 후 최초 입장이면 기존 이용 안내 팝업을 연다. 입장 이력이 있으면 점검 후 RTC에 연결한다. 이용 안내 최초 1회 정책은 그대로다.
- `cameraEnabled`, `micEnabled`: 현재 ON/OFF 표시. `cameraUnavailable`, `micUnavailable`: 권한 거부 또는 장치 미존재. `isMediaStarting`: 점검·장치 변경 진행 중.
- 점검은 허용된 트랙에 기존 SDK `setEnabled(false)`를 적용한다. 회의실에서 해당 트랙의 `setEnabled`로 전환하고 처음 ON 때만 publish한다. 거부된 장치에는 트랙이 없으므로 회의 중 클릭해도 새 권한 요청을 만들지 않는다.
- SDK 동작은 설치된 `agora-rtc-sdk-ng/rtc-sdk_en.d.ts`와 [Agora의 ICameraVideoTrack 문서](https://agoraio-extensions.github.io/agora-rtc-react/api-ref/interfaces/ICameraVideoTrack.html#setEnabled)를 확인했다. 실제 브라우저 권한 정책이나 외부에서 권한을 철회한 경우의 재활성화까지 이 테스트가 보장하지 않는다.
- `bindLocalVideoContainer`, `bindRemoteVideoContainer`를 합친 `bindVideoContainer(participantId, element)`를 유지한다. 참여자 `id`·React key를 배치 순서로 바꾸지 않는다.
- 화자 연결은 이미 존재한다: Agora `volume-indicator` → `getSpeakerUidKeys` → `useAgoraParticipants.participantSpeakerUidKeys` → `MeetingEntryRoute`의 `RoomParticipant.isSpeaking` → `RoomVideoTile`의 `video-tile--speaking`.
- 새 API·DTO·서버 정책·fixture는 추가하지 않았다. 기존 임시 입장 서비스와 RTC 계약을 사용한다.

## UI 역할의 구체적인 작업

사용할 공간은 모두 `reservation-shared`다. Logic 쓰기와 검증이 종료된 뒤 최신 소스를 읽고 수정한다.

### 영상 크기와 격자

- 수정 후보: `src/features/meeting/ui/room/RoomVideoGrid.tsx`, `src/features/meeting/ui/room/meeting-room.css`.
- 현재 `RoomVideoGrid`는 공통 `.video-grid`를 사용한다. `src/features/meeting/ui/meeting.css`의 값은 `grid-template-columns: 1fr`, `grid-auto-rows: minmax(230px, 52svh)`, `.video-tile`의 `min-height: 240px`이다.
- 예약 회의실에 적용할 클래스와 CSS를 확장해 가로·세로가 약 절반인 타일들을 격자로 배치한다. 2열을 기준으로 크기를 맞추고 기존 타일 최소 높이가 축소를 막지 않도록 함께 조정한다. 참여자 수 증가 시 다음 행에 배치한다.
- 장치 점검의 `.meeting-room__preview`와 기존 `/meeting`의 공통 화면까지 크기를 바꾸지 않도록 예약 회의실 영상 영역에 범위를 둔다.
- 닉네임·참여 유형·카메라 OFF 표시·마이크 상태가 축소된 타일 안에서 읽히도록 배치한다. 기존 비디오 컨테이너와 participant key를 재사용한다.

### 화자 파란 테두리

- 수정 후보: `meeting-room.css`, 필요한 경우 `RoomVideoGrid.tsx`의 시각 상태만 수정한다.
- 현재 공통 `--speaker-active`는 `#22c55e`이고 파란색 `--accent`는 `#2563eb`이다. 예약 회의실 범위에서 기존 파란 토큰을 활용한다.
- `isSpeaking`과 `video-tile--speaking` 연결을 유지한다. 별도 음량 타이머나 중복 화자 hook을 만들지 않는다.
- 발화 시작 시 파란 테두리가 나타나고 발화 종료·참여자 퇴장 시 사라져야 한다. 기존 reduced-motion 대응을 유지한다.

### 작은 한 줄 회의 컨트롤

- 수정 후보: `src/features/meeting/ui/room/MeetingRoomView.tsx`, `meeting-room.css`, 관련 테스트.
- DOM 순서를 **회의 나가기 → 마이크 → 카메라**로 변경하고 세 버튼을 작은 크기로 한 줄에 배치한다.
- 현재 `.meeting-controls`는 1열 grid이다. 예약 회의실 전용 범위에서 행 배치·간격·패딩·글자·아이콘 크기를 조정한다.
- 기존 `onLeave`, `onToggleMic`, `onToggleCamera`, `aria-pressed`, `isLeaving`과 나가기 확인 정책을 유지한다. CSS order만 바꿔 시각 순서와 키보드 순서가 달라지지 않게 한다.
- 재사용 조사: 공용 `src/shared/ui/button/button.tsx`, `src/shared/ui/icon-button/icon-button.tsx`를 확인했으나 현재 회의 화면은 자체 `.control-button` 구조를 사용한다. 이 작업은 기존 회의 컨트롤을 확장하는 범위이며 공용 버튼으로의 일괄 교체는 포함하지 않는다.
- UI props에 `cameraUnavailable?: boolean`, `micUnavailable?: boolean`을 추가해 각 장치 버튼의 disabled 상태에 반영한다. `MeetingEntryRoute.tsx`에서는 이미 존재하는 `rtc.cameraUnavailable`, `rtc.micUnavailable`을 그대로 전달한다. Logic에서는 트랙 없는 장치의 회의 중 재요청을 이미 막았다.

### 장치 점검 안내 문구

- 수정 후보: `src/features/meeting/ui/room/DeviceCheckView.tsx`와 `.test.tsx`.
- 현재 `GUIDE`의 `정상 재입장 시 장치점검 반복 없음`, 헤더 배지의 `최초 장치 점검`, 컴포넌트 설명 주석은 새 정책과 맞지 않는다. 모든 입장에서 점검한다는 의미로 변경한다.
- 기본 OFF·권한 거부 시 OFF 입장 안내는 유지한다. 이미 권한이 저장된 브라우저는 브라우저 팝업이 다시 뜨지 않을 수 있지만 장치 점검 화면은 항상 나타난다.

## 검증과 완료 기준

- UI 변경 후 해당 세션에 바인딩된 `formatting.py apply`를 이 workdir에서 실행한다.
- `npm run lint`, `npm run build`, `npm run test -- src/features/meeting src/features/meeting-reservation src/pages/meeting-reservation`을 실행한다.
- `MeetingRoomView.test.tsx`에서 컨트롤 DOM 순서·callback·disabled·화자 상태 변화·participant 컨테이너 연결을 확인한다.
- `DeviceCheckView.test.tsx`에서 변경 문구, 권한 거부 상태, 점검 진행 중 버튼 비활성화를 확인한다.
- 브라우저 캡처·시각 QA는 이번 세션에서 수행하지 않았다. 실제 브라우저 권한 팝업과 실제 장치 송출도 자동 테스트로 확인한 것으로 간주하지 않는다.
- 최종 Logic 소스의 `npm run lint`, `npm run build`, `git diff --check`는 통과했다. build의 500 kB 초과 청크 경고는 남아 있다.
- 전체 테스트 재실행은 741 통과·13 실패다. 실패는 시민참여의 투표/MSW/결과 화면 4개 파일에서 발생했고 이 세션에서 해당 소스는 수정하지 않았다.
- 최종 콜백 정리 후 회의·예약 묶음 실행은 38개 파일·298개 테스트 통과, 예약 라우트 1개 파일·16개 테스트 실패다. 첫 테스트의 5초 시간 초과 이후 `act()` 중첩과 연쇄 실패가 발생했으며 sandbox와 허용 환경 모두에서 관찰되었다. 이를 sandbox만의 문제로 단정하지 않는다.
- 동일 소스의 `npm run test -- src/pages/meeting-reservation/ui/MeetingReservationRoutes.test.tsx` 단독 실행은 16개 모두 통과했다. 해당 테스트는 이번에 수정한 `MeetingEntryRoute`나 입장 hook을 사용하지 않고 예약 폼·목록·상세를 직접 렌더한다. 실행 부하에 따른 테스트 불안정 가능성은 있지만 원인을 확정하거나 테스트 제한을 완화하지 않았다.
- 마지막 공용 `useApi` 변경을 관찰한 뒤 `useMeetingEntry.test.tsx`, `useAgoraMeeting.test.tsx`, `useAgoraLocalMedia.test.tsx`를 재실행해 3개 파일·39개 테스트가 통과했다. 기존 lint·build·전체 테스트 결과는 그 공용 변경 이전 시점의 결과다.
- 첫 sandbox 전체 실행의 HTTP listen EPERM은 실행 권한을 허용해 해소했다. 최종 결과·한계는 `final-summary.md`에도 기록한다.

## 협업·통합과 다음 조치

1. 새 UI 세션에서 이 문서와 `final-summary.md`, 실제 `git status`·`git diff`를 읽는다. 기본 branch를 바꾸거나 Logic 변경을 되돌리지 않는다.
2. 위 UI 작업을 같은 공간에서 순차 구현한다. 겹치는 파일은 `MeetingEntryRoute.tsx`이며 현재 Logic 변경은 `onNext` callback의 두 줄 연결이다.
3. UI 검증 결과와 남은 문제는 UI 세션 자신의 산출물에 기록한다. 이 Codex 세션 문서를 대신 수정하지 않는다.
4. 새 hook 계약이 필요하면 확인된 기존 값과 요구 차이를 Logic에 인계한다. 단순 권한 flag 전달과 기존 callback 연결은 위 계약을 사용한다.
5. commit·merge는 승인된 작업이 없다. 추후 요청 시 구체적인 diff·대상을 확인하고 중앙 Git 보호 실행 절차를 따른다.

산출물 책임은 현재 작업의 owner이며, 이 문서는 부분 역할 간 인계다. 위 작업 공간·파일 목록은 작업 계획이고 독점 권한이 아니다.
