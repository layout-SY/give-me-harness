# 인계

## Assignment 이동

- 보내는 host·session·role: Claude Code · 50d615e2-965c-441e-942f-b2f96b895688 · `ui`
- 받는 host·session·제안 role: 미정 host · 새 세션 · `logic`

## 역할 라우팅

- 요청 역할(`requested_roles`): ui, logic
- 확인된 역할(`confirmed_roles`): ui (이 세션)
- 완료 역할(`completed_roles`): ui
- 다음 제안 역할(`next_role`): logic
- 역할 판단 근거: DTO·parser·API·query hook·MSW mock·Agora 상태 병합·라우트 연결은 Logic 책임이며 UI 세션 범위 밖이다.
- 사용자 확인: 사용자가 "A 방식(UI는 이 세션, 나머지는 logic 세션)"을 선택했다.

## 목표 및 현재 상태

Figma `VO_V2_STEP17_M06_VO_PARTICIPANT_STATUS_MOBILE`(node `10:4858`, 채널 `siss0ze7`) 참여자 현황 화면 구현. UI 컴포넌트는 완료했다. 데이터 연결과 라우트는 구현하지 않았다.

## 완료된 작업

- `ParticipantStatusPage`: props로만 동작하는 조회 전용 화면
  - 헤더 「참여자 현황 / 현재 인증 예약 세션 기준」
  - 회의 카드: 테마 배지, 회의명, 날짜·시간
  - 「활성」 배지와 `현재 활성 이용인원 X/10`, 좌석 1~10. 앞의 X석은 `data-filled="true"`
  - 참여자 카드: `닉네임 · 참여구분`, 상태별 위치 안내, 상태 배지
  - 상태 기준 안내, 세션 격리 안내, 빈 목록·로딩·오류 상태
- 컴포넌트 테스트 6건, `index.ts` export

## 대기 중인 작업

Logic 세션: DTO·parser·API·hook·mock 작성, Agora 회의중 상태 병합, 라우트 연결 (아래 상세)

## 결정 사항 및 제약 조건

- (사용자 확정) API가 아직 없으므로 화면 내용에서 요청·응답 DTO를 추론해 구현한다.
- (사용자 확정) 좌석 번호는 입장 순서대로 1번부터 채운다. 번호 자체에 의미는 없고 "자리에 앉는다"를 보여 주는 표현이다.
- (사용자 확정) 라우트는 별도 경로 `/meeting/reservations/:reservationId/participants`를 쓴다. 3D 대기공간에서 웹뷰로 여는 화면으로 보고, 기존 웹 화면에서 이 화면으로 가는 링크는 추가하지 않는다.
- (사용자 확정) 상태 출처
  - 「회의중」은 Agora 실시간 세션(채널) 안의 사용자로 판정한다.
  - 「대기중」과 「중도퇴실」은 웹 API로 받는다.
- (사용자 확정) Figma M06 프레임에 겹쳐 있는 탭(내 예약/초대받은 회의/투표/토론), 「검토중」 배지, 「+ 제안하기」 버튼은 템플릿 잔여물로 보고 구현하지 않았다.
- (UI 결정) Figma의 상태 배지는 모두 노란색이다. 구분을 위해 대기중=`warning`, 회의중=`positive`, 중도퇴실=`neutral` tone을 사용했다.
- (UI 결정) Figma 좌석은 1~9만 그려져 있다. 최대 10명 기준에 맞춰 10석으로 구현했다.

## 보내는 작업의 위치와 변경 상태

- project·저장소 루트: `/Users/okand/SynologyDrive/asan-metaverse-user-ui`
- 현재 branch·HEAD·worktree: `task/vo-participant-status` · `3e30393`(commit 없음) · `/Users/okand/SynologyDrive/asan-worktrees/vo-participant-status`
- 확인 시점·인계 기준 commit: 2026-09-21 · `3e30393`
- 완료한 commit 목록: 없음 (미커밋)
- staged 변경: 없음
- unstaged 변경: `src/features/meeting-reservation/index.ts`에 `ParticipantStatusPage`와 타입 export 추가
- untracked
  - `src/features/meeting-reservation/ui/entry/ParticipantStatusPage.tsx`: 화면
  - `src/features/meeting-reservation/ui/entry/participant-status.css`: 전용 스타일 (기존 토큰만 사용)
  - `src/features/meeting-reservation/ui/entry/ParticipantStatusPage.test.tsx`: 컴포넌트 테스트
  - `.claude/logs/sessions/vo-participant-status-ui/handoff.md`: 이 문서
- 보존할 내용: 위 UI 변경. commit은 아직 사용자 승인을 받지 않았다.

## 인계 대상 작업 공간

### 작업 공간: vo-participant-status

- 수행할 기능·하위 작업: 참여자 현황 데이터 연결과 라우트 연결
- 사용할 역할: logic
- project·저장소 루트: `/Users/okand/SynologyDrive/asan-metaverse-user-ui`
- 목적지 branch: `task/vo-participant-status`
- worktree 절대 경로·실행 디렉터리: `/Users/okand/SynologyDrive/asan-worktrees/vo-participant-status`
- 기존 공간 / 생성 예정: 기존 공간. 이 세션에서 사용자 승인을 받아 생성했다.
- 확인한 HEAD: `3e30393`
- 직접 부모 branch: `sy-main` (`sy-main`에서 분기)
- 공유 / 분리: UI → Logic 순차 작업이므로 같은 공간을 공유한다.
- 목적지의 미커밋 변경: 위 UI 변경을 보존한다.
- 진입 전 확인: `git -C <worktree> status`로 위 목록과 일치하는지 확인한다. 불일치하면 사용자에게 보고한다.
- 필요한 Git 작업: UI 변경 commit 여부와 시점을 사용자와 확인해야 한다 (미승인).

## 역할별 상세 작업

### 역할·하위 작업: logic · 참여자 현황 데이터 연결

- 사용할 작업 공간 식별 이름: vo-participant-status
- 목표·현재 상태: UI는 완료했다. 데이터 계층과 라우트는 없다.
- 남은 작업과 변경 내용 (제안 계약. 서버 명세가 확정되면 대조한다)
  1. `src/features/meeting-reservation/api/meetingParticipantStatus.dto.ts` (zod)
     - `GET /meeting-reservations/{reservationId}/participant-status`
     - 응답 data: `{ reservationId, meetingName, themeName, startsAt, endsAt, maxParticipantCount: 10, participants: [{ participantId, nickname, role: "reserver"|"invited"|"code", status: "WAITING"|"LEFT_TEMPORARILY", agoraUid, enteredAt }] }`
     - participants는 입장 순서로 정렬하고 최대 10명이다. 시간은 정확히 1시간이어야 한다 (`hasOneHourSlot` 패턴).
     - 사용자 결정에 따라 웹 API는 대기중과 중도퇴실만 제공한다. 이 경우 회의중 사용자를 API 목록에 포함할지(예: status 없이 명단만) 정해야 한다.
  2. parser, `meetingReservation.api.ts`에 메서드 추가, `queryKeys`에 `participantStatus(reservationId)` 추가, `useMeetingParticipantStatusQuery`
  3. Agora 병합 hook: API 명단과 Agora 채널 참여자(`agoraUid`)를 합쳐 채널에 있는 사용자는 `in-meeting`으로 만든다. `ParticipantStatusItem[]`을 입장 순서로 반환한다.
  4. `mocks/handlers.ts`·`fixtures.ts`에 MSW handler와 fixture 추가
  5. `pages/meeting-reservation/ui/ParticipantStatusRoute.tsx`
  6. `shared/config/meetingReservationRoutes.ts`에 `participantsPattern`과 `participants(id)` 추가, `app/routing.ts`의 protectedRoutes에 등록
     - `/meeting/reservations/:reservationId`보다 구체적인 경로이므로 매칭이 충돌하지 않는지 확인한다.
- 확인한 재사용 자산: `meetingReservationApi`, `mapApiResult`, `withAbortSignal`, `customConfig`, `unwrapMeetingReservationResult`, `meetingReservationErrorMessage`, `createMeetingReservationHandlers` 패턴, `useMeetingEntry`의 `metadata` 포맷(`formatDateToLocalTimezone` Asia/Seoul, `HH:mm ~ HH:mm`), `useAgoraMeeting`·`useAgoraParticipants`, `MeetingEntryRoute`의 `roleLabel`(동일한 role 값)
- props 계약 (`ParticipantStatusPage`)
  - `meetingName?`, `themeLabel?`, `dateLabel?`(YYYY.MM.DD), `timeRangeLabel?`(`HH:mm ~ HH:mm`)
  - `participants?: readonly { id; nickname; role: "reserver"|"invited"|"code"; status: "waiting"|"in-meeting"|"left" }[]`: 입장 순서
  - `maxCount?`(기본 10), `isLoading?`, `errorMessage?`
  - 활성 인원은 `participants.length`로 계산한다 (maxCount 초과 시 잘라 냄). 좌석은 앞에서부터 채운다.
- 선행 조건: 아래 미확정 사항의 답변
- 겹치는 파일: `index.ts`(export 추가 위치), `meetingReservation.api.ts`, `handlers.ts`. UI 세션은 추가로 수정하지 않는다.
- 완료 기준: DTO·parser 테스트, route 테스트, `npm run lint`·`npm run build` 통과. `npm run test`에서 새 실패가 없어야 한다 (아래 기존 실패 13건 제외).
- 미확정 사항·사용자에게 할 질문
  1. 이 화면은 3D 대기공간에서 열리므로 보는 사람은 보통 Agora 채널 밖에 있다. 채널에 join하지 않은 클라이언트가 채널 참여자를 어떻게 알 수 있는지(Agora RTM, 서버 NCS 이벤트, 관전 join 등)와 사용할 credential·channel 식별자를 확인해야 한다.
  2. 웹 API 응답에 회의중 사용자를 포함할지(명단 전체 + 대기/퇴실 상태만, 또는 대기/퇴실 사용자만)와 `agoraUid` 매핑 필드를 확인해야 한다.
  3. 웹 API 갱신 주기(polling 간격 또는 진입 시 1회)를 확인해야 한다.
  4. 좌석 순서 기준(`enteredAt` 또는 서버 정렬)과 중도퇴실 후 복귀 시 원래 자리를 유지하는지 확인해야 한다.
  5. reservationId 접근 권한(코드 인증한 세션만 조회 가능) 실패 시의 오류 문구를 확인해야 한다.
- 다음 인계: Watcher 검토 → 사용자 commit 승인 → `sy-main` 통합 승인

## 협업 순서와 Git 통합

- 공유 공간 수정 순서: UI(완료) → Logic. UI 세션의 진행 중인 쓰기는 없다.
- 분리 공간 관계: `task/vo-participant-status` → 직접 부모 `sy-main`
- 형제 작업: `fix/reservation-media-check` worktree가 존재한다. 비교는 아직 하지 않았다.
- 승인된 Git 작업: 브랜치·worktree 생성 (완료)
- 아직 승인받지 않은 작업: commit, merge
- 산출물 책임: contributor

## 관련 경로와 스킬

- `.agent-policy/common/skills/policy/task-role-routing/references/logic.md`
- `.agent-policy/common/skills/policy/git-branch-strategy/SKILL.md`
- Figma 채널 `siss0ze7`, node `10:4858`

## 명령어 및 결과

- `formatting.py apply`: 수정 파일 4개에 포맷 적용
- `npm ci`: worktree에 의존성 설치 (519 packages)
- `npm run lint`: 통과
- `npm run build`: 통과 (기존 chunk size 경고만 있음)
- `npx vitest run src/features/meeting-reservation`: 17 files, 138 tests 통과
- `npm run test`: citizen-participation 쪽 4개 파일에서 13건 실패
  - `sy-main` 원본 checkout에서 같은 4개 파일을 실행해도 동일하게 13건이 실패한다 (기존 실패, 이번 변경과 무관).

## 실행하지 않은 검증

- 브라우저에서 화면을 직접 확인하거나 Figma와 시각 비교하지 않았다 (사용자가 요청하지 않음).
- 라우트·데이터가 연결되지 않아 통합 동작은 확인하지 않았다.

## 다음 조치

1. `--role logic` 새 세션에서 이 문서를 읽고 미확정 질문 1~5를 사용자에게 확인한다.
2. 확정된 계약으로 데이터 계층과 라우트를 구현한다.
3. commit·통합 승인을 받는다.
