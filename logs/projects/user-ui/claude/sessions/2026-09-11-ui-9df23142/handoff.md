# 회의 예약 폼 UI → Logic 인계 (회의실명 미지정·실패 모달)

## Assignment 이동

- 보내는 host·session·role: Claude Code / `2026-09-11-ui-9df23142` / `ui`
- 받는 host·session·제안 role: Logic 세션 / `logic`

## 역할 라우팅

- 요청 역할(`requested_roles`): ui, logic
- 확인된 역할(`confirmed_roles`): ui (inject `--role ui`)
- 완료 역할(`completed_roles`): ui (날짜 선택기, 칩 입력, Backspace 삭제, 슬롯 상태, 회의실명 표시)
- 다음 제안 역할(`next_role`): logic — 제안이며 권한 부여가 아니다.
- 역할 판단 근거: 아래 남은 작업은 라우팅·route 연결·hook·검증·API 호출 제어라 Logic 범위다.
- 사용자 확인(2026-09-11): "ui 부분 외에는 logic 세션에게. 따라서 logic이 추가적으로 해야 할 작업 범위를 핸드오프 문서에 기재"

## 목표 및 현재 상태

- 원본 인계: `/Users/okand/SynologyDrive/asan-worktrees/meeting-reserve-room-slot/docs/meeting-reserve-room-slot-handoff.md`
- 이전 Logic 인계: `.codex/logs/sessions/2026-09-11-logic-03d68ca7/handoff.md`
- UI·Logic·연결 변경이 모두 `task/meeting-reserve-room-slot` worktree에 미커밋으로 있다. 현재 lint·`tsc -b`·예약/라우트/공유 UI/app 테스트(25 files, 173 tests)가 통과한다.
- 이번 사용자 결정(아래 D1~D4)은 UI 표시만 반영되었다. 라우팅·route·hook의 동작은 아직 이전 계약이다.

## 사용자 결정 (2026-09-11)

| # | 결정 |
| --- | --- |
| D1 | 헤더에는 라우트 path의 `roomName`을 그대로 표시한다. 없거나(`undefined`) 공백뿐이면 `회의실명 미지정`을 표시한다. 폼은 그대로 띄운다. |
| D2 | 회의실 이름이 없거나 공백이면 **서버에 요청하지 않고** 오류를 낸다. 문구: `일시적인 오류로 실행이 불가능합니다.` |
| D3 | 실패 메시지는 폼 전체를 대체하지 않고 **모달**로 띄운다. `확인`을 누르면 모달만 닫히고 폼 작성 상태는 그대로 유지된다. |
| D4 | 모달은 프로젝트의 기존 API 실패 모달 패턴(아래)을 따르고, 제목·내용은 그 패턴의 props로 넣는다. |

## 기존 모달 패턴 (재사용 대상, 신규 UI 없음)

- 전역: `meta.presentation`이 없는 요청의 서버 오류는 `src/app/providers/ApiErrorDialogBridge.tsx`가 `alert({ header: "오류 안내 · {code}", content: message })`로 띄운다.
- 기능 처리: 쿼리·뮤테이션에 `meta: { presentation: "inline" }`을 두고 hook에서 `useDialog().alert({ header: "<행위> 실패", content: 메시지 })`를 호출한다.
  - 예: `src/features/meeting-reservation/hook/useMeetingReservationMutation.ts:34` → `dialog.alert({ header: "예약 신청 실패", content: meetingReservationErrorMessage(error) })`
- `AlertProps`: `{ header?: string; content: ReactNode; callback?: () => void }` (`src/shared/ui/dialog/dialog.store.ts`). `확인`은 모달만 닫으므로 D3의 "폼 상태 유지"를 그대로 만족한다. `header`를 생략하면 영문 `Alert`가 나오므로 반드시 넣는다.

## 완료된 UI 작업 (이번 인계분)

- `MeetingReservePage.tsx`: `roomLabel`을 trim해 비어 있으면 `회의실명 미지정`, 아니면 그 값을 헤더 부제목에 표시. 기존 폴백 `필수 항목을 입력해 주세요`는 제거.
- `MeetingReservePage.test.tsx`: 이름 있음·없음·빈 문자열·공백 케이스 추가.
- props 계약 변화 없음. route가 `roomLabel`만 넘기면 된다.

## 대기 중인 작업 (Logic)

| # | 파일 | 작업 |
| --- | --- | --- |
| L1 | `src/app/routing.ts` | `roomName` 없는 `/meeting/reserve`도 `MeetingReserveRoute`로 연결한다(별도 경로 또는 `/meeting/reserve/:roomName?`). 현재는 wildcard `*`로 `/meeting`에 떨어진다. `routing.test.ts`의 `"/meeting/reserve"` → `*` 기대값도 갱신한다. |
| L2 | `src/pages/meeting-reservation/ui/MeetingReserveRoute.tsx:19` | 빈 `roomName`일 때의 `<Navigate to="/meeting" replace />`를 제거하고 폼을 렌더한다. `key`와 hook 인자는 `roomName ?? ""`. |
| L3 | `MeetingReserveRoute.tsx` `MeetingReservePage` 호출부 | `roomLabel={roomName ?? ""}`를 전달한다(trim·폴백은 UI가 처리). |
| L4 | `MeetingReserveRoute.tsx:43-48` | `isRoomNotFound`일 때 폼 전체를 `role="alert"` 화면으로 바꾸는 분기를 제거한다(D3). `ROOM_NOT_FOUND`는 L6의 모달로 알린다. |
| L5 | `hook/useMeetingReservation.ts`, `hook/useMeetingReservationQueries.ts:19` | `roomName.trim()`이 비면 시간 슬롯 조회를 **요청하지 않고**, 날짜 선택 직후(자동 조회 시점)와 `requestOptions("timeSlot")` 재조회 시점에 `dialog.alert({ header: "시간 슬롯 조회 실패", content: "일시적인 오류로 실행이 불가능합니다." })`를 띄운다. 같은 날짜에서 렌더마다 반복해서 뜨지 않도록 "사용자 동작 1회 = 모달 1회"로 제어한다. |
| L6 | `hook/useMeetingReservation.ts` | 시간 슬롯 조회 API 실패(`ROOM_NOT_FOUND` 포함)는 `dialog.alert({ header: "시간 슬롯 조회 실패", content: meetingReservationErrorMessage(error) })`로 띄운다. 모달로 알린 실패는 `timeSlotError`로 중복 표시하지 않는다(route에서 `timeSlotError` 전달 중단 또는 hook에서 `undefined`). UI의 `timeSlotError` prop은 선택값이라 그대로 두어도 된다. |
| L7 | `hook/useMeetingReservation.ts` `submit`, `model/forms/meetingReservationForm.ts:98` | 제출 시 `roomName`이 비거나 공백이면 POST를 호출하지 않고 `dialog.alert({ header: "예약 신청 실패", content: "일시적인 오류로 실행이 불가능합니다." })`를 띄운다. 현재 필드 오류 `errors.timeSlot = "회의실 정보를 확인해 주세요."`는 모달과 중복되므로 제거하거나 모달로 대체한다. 다른 필드 검증 오류는 기존대로 필드에 표시한다. |
| L8 | 테스트 | `MeetingReservationRoutes.test.tsx`: `/meeting/reserve`·공백 `roomName` 진입 시 폼과 `회의실명 미지정` 표시, 날짜 선택 시 슬롯 API 미호출 + 모달(`시간 슬롯 조회 실패` / `일시적인 오류로 실행이 불가능합니다.`), 제출 시 POST 미호출 + 모달(`예약 신청 실패`), `확인` 후 입력값 유지, `ROOM_NOT_FOUND` 응답 시 폼 유지 + 모달. `useMeetingReservation.test.tsx`: 빈/공백 roomName에서 슬롯·POST 미호출. |

- 참여자 검색(`GET /participants`)은 `roomName`을 쓰지 않으므로 D2 차단 대상이 아니다.
- 모달 제목 `시간 슬롯 조회 실패`는 기존 `예약 신청 실패` 형식(`<행위> 실패`)에 맞춘 UI 세션의 제안이다. 필드 라벨 `1시간 시간 슬롯` 기준으로 바꾸려면 Logic 세션에서 사용자 확인 후 조정한다.

## 결정 사항 및 제약 조건

- 신규 모달 컴포넌트를 만들지 않는다. 전역 `Dialog`(`useDialog().alert`)를 재사용한다.
- `MeetingReservePage`는 이번 D1~D4로 props가 추가되지 않았다.
- 이전 인계의 계약(`minReservationDate`·`maxReservationDate`(이번 달 말일)·`participantCandidates`·`timeSlotError`, Backspace 뱃지 제거는 `onRemoveParticipant` 재사용)은 그대로다.
- 연결 과정에서 공유 `src/shared/ui/dropdown/dropdown.tsx`에 `allowsEmptyCollection`이 추가되었다(빈 슬롯 목록에서도 빈 결과 문구 표시). 전체 build·테스트에서 회귀는 없었다.

## 소유권과 Git 계약

- UI 변경 경로(이 세션): `DESIGN.md`, `src/shared/ui/date-picker/**`(신규), `src/shared/ui/text-input/{text-input.tsx,text-input.css}`, `src/features/meeting-reservation/ui/{MeetingReservePage.tsx,MeetingReservePage.test.tsx}`, `src/features/meeting-reservation/ui/parts/{ParticipantPicker.tsx,meeting-reservation-parts.css}`
- Logic 작업 경로(L1~L8): `src/app/routing.ts`, `src/app/routing.test.ts`, `src/pages/meeting-reservation/ui/{MeetingReserveRoute.tsx,MeetingReservationRoutes.test.tsx}`, `src/features/meeting-reservation/{hook,model}/**`
- 충돌 여부: L1~L8은 UI 파일을 수정하지 않는다.
- task·branch·worktree: `task/meeting-reserve-room-slot` / `/Users/okand/SynologyDrive/asan-worktrees/meeting-reserve-room-slot` / HEAD `c19bdd5`, 전부 미커밋
- 승인할 Git 작업: 없음(미실행). commit·merge는 L1~L8 완료 후 별도 승인.
- 사용자 지시: 작업 완료·병합 후 **이 worktree를 삭제**한다(완료 승인 시 정리 포함, `npm ci`로 생성한 `node_modules/` 포함).
- 산출물 책임: contributor

## 관련 경로와 스킬

- 스킬: `task-role-routing`(ui.md), `git-branch-strategy`, `ui-library`, `abstraction-strategy`
- 모달 패턴 참고: `src/app/providers/ApiErrorDialogBridge.tsx`, `src/shared/ui/dialog/{hook.ts,dialog.store.ts,dialog.tsx}`, `src/features/meeting-reservation/hook/useMeetingReservationMutation.ts`

## 명령어 및 결과 (worktree)

- `npx vitest run src/features/meeting-reservation/ src/pages/meeting-reservation/ src/shared/ui/ src/app/`: 25 files, 173 tests 통과
- `npm run lint`: 통과
- `npx tsc -b --noEmit`: 통과
- 직전 확인한 `npm run build`: 통과. `npm run test` 전체: 5건 실패 — 모두 `citizen-participation` 투표(3 files). 이 worktree는 해당 파일을 변경하지 않았고, Mock 투표 기간(2026-08-08~08-31)이 오늘(09-11) 기준 종료된 날짜 의존 실패로 추정. 기준 commit에서의 재현은 확인하지 않음.

## 실행하지 않은 검증

- L1~L8 반영 후의 통합 테스트·build
- 브라우저 시각 확인(요청 없음)

## 다음 조치

1. Logic: L1~L8 구현과 테스트.
2. 통합 후 `npm run lint`, `npm run build`, 예약 관련 vitest 재실행.
3. commit·`sy-main` 병합 승인 → worktree 정리.
