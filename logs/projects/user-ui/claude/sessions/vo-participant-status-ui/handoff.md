# 인계

## Assignment 이동

- 보내는 host·session·role: Claude Code · 50d615e2-965c-441e-942f-b2f96b895688 · `ui`
- 받는 host·session·제안 role: 미정 host · 새 세션 · `logic`

## 역할 라우팅

- 요청 역할(`requested_roles`): ui, logic
- 확인된 역할(`confirmed_roles`): ui (이 세션)
- 완료 역할(`completed_roles`): ui
- 다음 제안 역할(`next_role`): logic
- 역할 판단 근거: 남은 작업은 좌석 번호를 배정·유지하는 상태(hook)와 `MeetingEntryRoute` 연결이다. 상태 전이는 Logic 책임이며 UI 세션 범위 밖이다.
- 사용자 확인: 사용자가 "A 방식(UI는 이 세션, 나머지는 logic 세션)"을 선택했고, 이후 회의실 내부 이동과 단독 화면 제거를 지시했다.

## 목표 및 현재 상태

Figma `VO_V2_STEP17_M06_VO_PARTICIPANT_STATUS_MOBILE`(node `10:4858`, 채널 `siss0ze7`)에서 시작했으나, 사용자가 사용 맥락을 두 번 바꿔 최종 형태는 Figma와 다르다.

- 최종: **회의 중 회의실 화면(`MeetingRoomView`)의 영상 위 좌석 섹션**만 남긴다.
- 대기공간용 단독 화면과 라우트는 제거했다(커밋 `e6b61df`).

UI는 완료했다. 좌석 번호를 기억하는 hook만 남았다.

## 완료된 작업

- `MeetingRoomView` 좌석 섹션 (커밋 `2477838`, 이후 미커밋 수정 포함)
  - 위치: `RoomHeader`와 `RoomVideoGrid` 사이. 참여자·채팅 탭과 무관하게 항상 보인다.
  - 기존 `.meeting-room__section` + `.meeting-room__section-title` 스타일만 사용한다. 새 CSS 규칙은 만들지 않았다.
  - 제목은 `현재 활성 이용인원 N/10`이며 `aria-labelledby`로 섹션과 연결했다.
  - `occupiedSeats?: readonly number[]` prop을 받는다. 없으면 참여자 수만큼 앞에서부터 채운다.
- `ui/parts/SessionSeatRow.tsx` + `session-seat-row.css` (`.vo-seat-row`)
  - `occupiedSeats`(1부터인 자리 번호)와 `totalCount`를 받는다. `[1, 3]`이면 2번은 비운다.
  - 범위 밖 번호·중복은 걸러내고, 표시 인원은 걸러낸 뒤의 개수다.
  - 조회 전용이며 좌석을 고를 수 없다.
- 제거한 것 (커밋 `e6b61df`)
  - `ParticipantStatusPage`와 css·테스트, `ParticipantStatusRoute`
  - `meetingReservationRoutes`의 `participantsPattern`·`participants`, `app/routing.ts` 등록, `routing.test.ts`의 관련 테스트 2건
  - `participantPresence.ts`(대기중/회의중/중도퇴실 라벨·tone) — 쓰는 화면이 없어졌다.
  - 회의실 하단 패널의 회의실 밖 참여자 목록, `waitingParticipants` prop, `WaitingRoomParticipant` 타입
- 테스트: `MeetingRoomView.test.tsx`에 3건 추가 (좌석 섹션 제목·채움, 배정 번호 유지, 영상보다 위 배치와 탭 전환 시 유지)

## 대기 중인 작업

Logic 세션: 좌석 번호 배정·유지 hook과 `MeetingEntryRoute` 연결. 이것이 유일한 잔여 작업이다.

## 결정 사항 및 제약 조건

- (사용자 확정) 참여자 현황은 회의 중 회의실 내부에서 본다. 회의 중 별도 페이지로 이동하면 `MeetingEntryContent`가 unmount되며 `leaveRtcSession`이 돌아 회의에서 빠지므로, 라우트 이동을 쓰지 않는다. 모달도 화면을 덮는 부담 때문에 쓰지 않는다.
- (사용자 확정) 회의실 화면에는 **영상 위 좌석 섹션만** 둔다. 회의실 밖(대기중·중도퇴실) 참여자는 표시하지 않는다.
- (사용자 확정) 좌석 채움 기준은 **회의실 참여자**(Agora 채널)다. 참여자 탭 라벨 `참여자 N/10`과 항상 같은 숫자다.
- (사용자 확정) 좌석 번호는 입장 순서대로 1번부터 배정하며 의미는 없다. "자리에 앉는다"를 보여 주는 표현이다.
- (사용자 확정) **자리는 퇴실할 때까지 유지한다.** 중간 사람이 나가도 뒤 사람을 앞으로 당기지 않는다. 표시는 구현했고 배정 상태는 미구현이다.
- (사용자 확정) 갱신은 Agora 실시간 이벤트 기준이다. 사용자가 들어오거나 나갈 때 갱신되며 polling은 두지 않는다. 현재 `useAgoraMeeting`의 `user-joined`·`user-left`로 `participants`가 바뀌면 좌석이 다시 그려진다.
- (사용자 보류) 웹 API로 대기중·중도퇴실 명단을 받는 계약은 보류다. 단독 화면이 없어져 현재 필요한 곳이 없다.
- (UI 결정) 다른 feature의 배럴(index) import를 쓰지 않는다. 아래 「검증에서 발견한 문제」 참고.

## 검증에서 발견한 문제와 조치

`MeetingRoomView`에서 `~/features/meeting-reservation`(배럴)로 `SessionSeatRow`를 import했을 때, 예약 기능 전체(페이지·hook·API client)가 딸려 들어와 `MeetingReservationRoutes.test.tsx`가 5초 타임아웃으로 16건 실패했다.

- 근거: `sy-main` 원본에서 같은 조합 2회 통과 / 브랜치에서 2회 모두 같은 16건 실패(import 67s) / 워커 1개 직렬 실행은 통과 → 타이밍 문제
- 조치: `~/features/meeting-reservation/ui/parts/SessionSeatRow` 직접 경로로 변경. 병렬에서도 329건 통과, import 52s로 복귀. 코드에 이유를 주석으로 남겼다.
- 주의: 앞으로 `features/meeting`에서 `features/meeting-reservation`의 파트를 쓸 때도 직접 경로를 쓴다.

## 보내는 작업의 위치와 변경 상태

- project·저장소 루트: `/Users/okand/SynologyDrive/asan-metaverse-user-ui`
- 현재 branch·worktree: `task/vo-participant-status` · `/Users/okand/SynologyDrive/asan-worktrees/vo-participant-status`
- 확인 시점·인계 기준 commit: 2026-09-30 · `e6b61df`
- 완료한 commit 목록 (오래된 순)
  - `5bac866` feat: 가상오피스 참여자 현황 화면 추가 (이후 제거됨)
  - `1b6dff3` feat: 참여자 현황 화면 라우트 등록 (다른 세션의 미커밋 변경을 사용자 지시로 커밋, 이후 제거됨)
  - `971ad28` feat: 회의실 참여자 패널에 좌석과 회의실 밖 참여자 표시
  - `2477838` refactor: 회의실 좌석 현황을 영상 위 섹션으로 옮기고 회의실 밖 참여자 표시 제거
  - `e6b61df` refactor: 대기공간용 참여자 현황 단독 화면과 라우트 제거
- 미커밋 변경 (자리 유지 표시, commit 예정)
  - 수정 `src/features/meeting-reservation/ui/parts/SessionSeatRow.tsx`: `filledCount` → `occupiedSeats`
  - 수정 `src/features/meeting/ui/room/MeetingRoomView.tsx`: `occupiedSeats` prop, 직접 경로 import
  - 수정 `src/features/meeting/ui/room/MeetingRoomView.test.tsx`: 자리 유지 테스트 추가
  - `.claude/logs/sessions/vo-participant-status-ui/handoff.md`: 이 문서 (gitignore 대상)
- 보존할 내용: 위 미커밋 변경. `sy-main`은 건드리지 않았다.
- 중간 3개 커밋은 만들었다가 지운 이력이다. 통합 시 그대로 둘지 정리할지 사용자와 확인이 필요하다. squash는 완료 경로로 쓰지 않는다.

## 인계 대상 작업 공간

### 작업 공간: vo-participant-status

- 수행할 기능·하위 작업: 좌석 번호 배정·유지 hook과 회의실 연결
- 사용할 역할: logic
- project·저장소 루트: `/Users/okand/SynologyDrive/asan-metaverse-user-ui`
- 목적지 branch: `task/vo-participant-status`
- worktree 절대 경로·실행 디렉터리: `/Users/okand/SynologyDrive/asan-worktrees/vo-participant-status`
- 기존 공간 / 생성 예정: 기존 공간. 이 세션에서 사용자 승인을 받아 생성했다. `npm ci`로 의존성도 설치돼 있다.
- 확인한 HEAD: `e6b61df` (+ 위 미커밋 변경)
- 직접 부모 branch: `sy-main` (`sy-main`에서 분기, 기준 `3e30393`)
- 공유 / 분리: UI → Logic 순차 작업이므로 같은 공간을 공유한다.
- 진입 전 확인: `git -C /Users/okand/SynologyDrive/asan-worktrees/vo-participant-status status`로 위 목록과 일치하는지 확인한다. 불일치하면 사용자에게 보고한다.
- 필요한 Git 작업: hook 구현 후 commit, 그리고 `sy-main` 통합 (모두 미승인)

## 역할별 상세 작업

### 역할·하위 작업: logic · 좌석 번호 배정과 유지

- 사용할 작업 공간 식별 이름: vo-participant-status
- 목표: 회의실 참여자마다 자리 번호를 배정하고 퇴실할 때까지 유지한다. 중간 사람이 나가도 뒤 사람을 당기지 않는다.
- 남은 작업
  1. 좌석 배정 hook (예: `src/features/meeting/hook/useSeatAssignment.ts`)
     - 입력: 현재 회의실 참여자 식별자 목록(`RoomParticipant.id`, 즉 Agora uid 문자열)과 정원(기본 10)
     - 동작: 새 참여자에게 비어 있는 가장 작은 번호를 배정하고, 사라진 참여자의 번호는 비운다. 재입장은 새 배정으로 본다(같은 번호 보장 아님).
     - 출력: `readonly number[]`(사용 중인 번호, 정렬 여부는 무관) 또는 `Map<참여자 id, 번호>`. 화면은 번호 목록만 쓴다.
     - 정원 초과: 배정할 번호가 없는 참여자는 좌석 표시에서 제외한다. 실제로는 서버가 10명을 넘기지 않지만 방어적으로 처리한다.
     - 상태는 렌더 사이에 유지해야 하므로 `useRef`/`useState` 기반으로 두고, 참여자 목록 변화에만 반응한다.
  2. `MeetingEntryRoute`에서 hook을 호출해 `MeetingRoomView`에 `occupiedSeats`로 넘긴다. 현재 `participants` 배열을 만드는 곳과 같은 위치다.
  3. hook 단위 테스트: 입장 순서 배정, 중간 퇴장 후 번호 유지, 빈 번호 재사용, 정원 초과
- 연결 계약
  - `MeetingRoomView`: `occupiedSeats?: readonly number[]` (미전달 시 참여자 수만큼 앞에서부터 채우는 기존 동작)
  - `SessionSeatRow`: `occupiedSeats`, `totalCount`
  - 표시 인원 = `occupiedSeats.length`, 좌석 총수 = `maxParticipants`(기본 10)
- 확인한 재사용 자산: `useAgoraMeeting`·`useAgoraParticipants`(`remoteParticipants`, `localUid`), `MeetingEntryRoute`의 `participants` 조립부와 `roleLabel`
- 겹치는 파일: `MeetingEntryRoute.tsx`, `MeetingRoomView.tsx`. UI 세션은 추가로 수정하지 않는다.
- 완료 기준: hook 테스트 통과, `npm run lint`·`npm run build` 통과, 아래 조합 테스트에서 새 실패 없음
- 미확정 사항·사용자에게 할 질문
  1. 같은 사용자가 중도퇴실 후 재입장할 때 이전 번호를 돌려줘야 하는지 확인해야 한다. 현재 제안은 "새로 배정"이다. 돌려주려면 사용자 식별자(`userSeq`) 기준으로 기억해야 하고, Agora uid는 재입장 시 바뀔 수 있다.
  2. 참여자 목록 항목의 `statusLabel`을 실제 상태로 채울지 확인해야 한다. 지금은 `MeetingEntryRoute`가 넘기지 않아 역할만 나온다. 회의실 안 사람은 모두 회의중이므로 생략해도 무리가 없다.

## 협업 순서와 Git 통합

- 공유 공간 수정 순서: UI(완료) → Logic. UI 세션의 진행 중인 쓰기는 없다.
- 분리 공간 관계: `task/vo-participant-status` → 직접 부모 `sy-main`
- 형제 작업: `fix/reservation-media-check`(worktree `/Users/okand/SynologyDrive/asan-worktrees/reservation-media-check`, `a1b113d`)가 있다. 비교는 아직 하지 않았다. 통합 전 형제 검토가 필요하다.
- 승인된 Git 작업: 브랜치·worktree 생성, 위 5개 commit
- 아직 승인받지 않은 작업: 미커밋 변경 commit, `sy-main` 통합
- 산출물 책임: contributor

## 관련 경로와 스킬

- `.agent-policy/common/skills/policy/task-role-routing/references/logic.md`
- `.agent-policy/common/skills/policy/git-branch-strategy/SKILL.md`
- Figma 채널 `siss0ze7`, node `10:4858` (최종 구현과는 다르다)

## 명령어 및 결과

- 포맷: `formatting.py apply` (수정 파일마다 실행)
- `npm ci`: worktree에 의존성 설치 (519 packages)
- `npm run lint`: 통과
- `npm run build`: 통과 (기존 chunk size 경고만 있음)
- `npx vitest run src/features/meeting src/features/meeting-reservation src/pages/meeting-reservation src/app/routing.test.ts`: 40개 파일 329건 통과
- `npm run test` 전체: citizen-participation 4개 파일에서 13건 실패. `sy-main` 원본에서도 동일하게 실패하는 기존 문제이며 이번 작업과 무관하다.

## 실행하지 않은 검증

- 브라우저에서 화면을 직접 확인하지 않았다 (사용자가 요청하지 않음).
- 실제 회의에서 여러 명이 입·퇴장할 때의 좌석 동작은 hook이 없어 확인하지 못했다.
- 형제 브랜치 `fix/reservation-media-check`와의 비교·통합 검토는 하지 않았다.

## 다음 조치

1. `--role logic` 새 세션에서 이 문서를 읽고 미확정 질문 2건을 사용자에게 확인한다.
2. 좌석 배정 hook과 `MeetingEntryRoute` 연결을 구현하고 테스트를 추가한다.
3. commit 승인을 받고, 형제 검토 후 `sy-main` 통합 승인을 받는다.

## 확인 경로

- 실행: `/Users/okand/SynologyDrive/asan-worktrees/vo-participant-status`에서 `npm run dev` (기본 포트 2426)
- 회의실까지: `http://localhost:2426/meeting/rooms/camping-01/code` → 코드 `A1B2C3D4E5` → 회의 정보 확인 → 장치 점검 → 회의실
- 임시 입장 서버는 `vite.config.ts`의 `meetingEntryPlugin`이 dev 서버에 함께 붙인다. 고정 코드는 `A1B2C3D4E5`(정상), `WAIT000001`(시작 전 대기), `CANCEL0001`(거부)이며 회의실 이름은 `camping-01`이다.
