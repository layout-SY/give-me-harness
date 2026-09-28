# 계획

## 목표

참여자 현황 UI 핸드오프의 확정 경로 `/meeting/reservations/:reservationId/participants`를 기존 화면에 연결한다. 이번 요청은 라우팅까지만 구현한다.

## 작업 유형

- feature

## 범위

- 작업 위치: `/Users/okand/SynologyDrive/asan-worktrees/vo-participant-status`, branch `task/vo-participant-status`.
- 시작 HEAD: `5bac866bfe764c39e75b4eb0936bb36f0c82c1bf`. 작업 전 staged·unstaged·untracked 변경 없음. UI 커밋은 보존한다.
- 직접 부모: 핸드오프에 명시된 `sy-main`. 실제 `sy-main..HEAD`는 UI 커밋 1건이다.
- `shared/config/meetingReservationRoutes.ts`: `participantsPattern`, `participants(id)`를 기존 ID 인코딩 방식으로 추가한다.
- `pages/meeting-reservation/ui/ParticipantStatusRoute.tsx`와 pages barrel: 기존 `ParticipantStatusPage`를 기본 props로 렌더한다.
- `app/routing.ts`: 기존 `AuthRouteBoundary` 아래에 경로를 등록한다.
- `app/routing.test.ts`: ID 전달·인코딩·인증 경계·예약 상세 경로와의 구분을 확인한다.

## 제외 사항

API·DTO·Agora·mock·진입 링크·UI 스타일 변경, Git stage·commit·merge는 포함하지 않는다.

## 제약 조건

- 참조: `.claude/logs/sessions/vo-participant-status-ui/handoff.md`. 다른 세션 문서는 수정하지 않는다.
- 데이터 연결 전 화면은 기존 기본 상태인 회의 정보·0/10·빈 참여자 목록을 표시한다. 예약 ID로 데이터를 조회하지 않는다.
- 기존 라우트 구성·페이지 경계·feature export를 재사용한다. 별도 추상화나 의존성을 추가하지 않는다.

## 스킬 및 역할

- 역할: inject `logic`; 기존 UI의 기능 연결 책임에 해당한다.
- 스킬: task-role-routing, git-branch-strategy, coding-convention, implementation-quality, documentation.
- 재사용 조사: `ParticipantStatusPage` 및 테스트, `MeetingEntryRoute`, `InquiryRoutes`, `meetingReservationRoutes`, `routing`, `AuthRouteBoundary` 및 테스트, `shared/ui`.
- 산출물 책임: owner.
- 승인할 Git 작업: 없음.

## 작업 순서와 검증

1. 위 worktree에서 기존 구성에 경로와 페이지 연결을 추가해 직접 URL 진입을 지원한다.
2. 같은 위치에서 중앙 `formatting.py apply`를 실행하고 실제 diff를 확인한다.
3. 라우팅·인증 경계·기존 참여자 UI 테스트와 `npm run lint`, `npm run build`로 연결과 타입을 검증한다.
4. 결과와 후속 데이터 연결 범위를 자기 세션 `final-summary.md`에 기록한다.

## 위험 요소 및 결정 사항

데이터 계층과 Agora 계약의 미확정 항목은 이번 라우팅에 필요하지 않으므로 확정하지 않는다. 기본 UI는 실제 예약 참여자 조회 결과를 의미하지 않는다. 브라우저 캡처와 시각 QA는 요청 범위가 아니다.

## 승인

- 상태: 승인됨.
- 사용자 응답: `반영`, `그냥 핸드오프 문서대로 구현해.`, 이후 승인 훅 등록을 위한 `진행`.
- 최초 소스 적용은 승인 상태 미기록으로 차단됐으며 파일 변경이 없음을 확인했다. `진행` 후 동일 범위 적용을 재개했다.
