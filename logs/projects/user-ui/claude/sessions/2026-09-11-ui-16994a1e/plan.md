# 계획

## 목표

Figma `가상오피스` 페이지의 미구현 사용자 흐름 STEP14~16·19~24를 모바일 UI로 구현한다. STEP19~23은 Figma가 데스크톱 기준이므로 항목 구성만 참고하고, 실제 레이아웃은 `/meeting` 임시 구현체의 모바일 셸(`src/features/meeting/ui/meeting.css`)을 채택한다.

## 작업 유형

- feature (UI only)

## 범위

- A. 코드 입장 흐름 (`src/features/meeting-reservation/ui/entry/`)
  - STEP14 `RoomCodeEntryPage`, STEP15 `CodeMeetingConfirmPage`, STEP16 `EntryDeniedPopup`, STEP19 `EntryWaitPopup`, STEP24 `MeetingEndPage`
- B. 회의실 흐름 (`src/features/meeting/ui/room/`)
  - STEP20 `DeviceCheckView`, STEP21 `MeetingEntryNoticePopup`, STEP22 `MeetingRoomView`(+`RoomVideoGrid`, `RoomHeader`), STEP23 `MeetingExitConfirmPopup`
- 컴포넌트별 테스트와 feature `index.ts` export

## 제외 사항

- API·hook·타이머 계산·라우트 연결(Logic 후속)
- ADM 프레임(STEP09~13·25~31): 사용자 대응 화면은 이미 구현됨, 승인·반려·일정관리는 관리자 전용
- STEP17(보류), STEP18(3D NPC)
- 기존 `/meeting` 파일 수정

## 제약 조건

- `DESIGN.md`: 새 색상·뷰포트 분기 금지, 고정 모바일 셸, 44px 터치 대상
- 회의 전용 토큰은 `.meeting-app` 범위에서만 사용, 팝업은 전역 토큰만 사용

## 스킬 및 역할

- 제안 역할: UI (inject `--role ui`)
- 역할 판단 근거: 화면 구조·스타일·접근성·props 계약만 구현한다.
- 사용자 역할 확인: inject role. 계획은 2026-09-11 "이 계획대로 진행해"로 승인.
- 승인할 Git 작업: `task/meeting-entry-ui` branch·linked worktree 생성, 논리 단위 commit 2건, sy-main 부모 동기화
- 산출물 책임: owner

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 코드 입장 흐름 | UI | frontend-design(기존 계약 우선) | STEP14·15·16·19·24 컴포넌트·테스트 |
| 회의실 흐름 | UI | frontend-design(기존 계약 우선) | STEP20~23 컴포넌트·테스트 |

## 검증

- `npm run test`, `npm run lint`, `npm run build` (시각 QA 제외)

## 위험 요소 및 결정 사항

- STEP16 사유 8종 문구는 Figma 원문 미확정 → props 주입, 기본값은 ACTIVE_SESSION_CONFLICT
- STEP22 참여자/채팅은 영상 아래 탭 전환(공용 `Tabs`)
- 경고 아이콘을 3개 팝업이 공유하므로 `src/shared/assets/icons/error.icon.tsx`로 승격
- 추가 결정(2026-09-14): 입장 코드는 영문·숫자 조합 10자리, Logic은 이 branch를 이어받아 작업

## 승인

- 상태: approved (2026-09-11, "이 계획대로 진행해")
