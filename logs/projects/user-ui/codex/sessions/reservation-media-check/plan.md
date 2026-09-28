# 예약 회의 렌더링·장치 권한 수정 계획

> 작업 위치 이전 완료: 이 문서의 아래 내용은 이동 전 기록이다. 현재 브랜치는 `fix/reservation-media-check`이며, 정본 문서와 변경사항은 [plan.md](/Users/okand/SynologyDrive/asan-worktrees/reservation-media-check/.codex/logs/sessions/reservation-media-check/plan.md)에 있다. 원래 `sy-main`에는 다른 작업의 `useApi` 변경만 남겼다.

예약 입장 화면의 불필요한 매초 렌더링을 없애고, 최초 입장과 재입장 모두 장치 점검에서 권한을 확인한다. UI 변경은 같은 작업 공간에서 이어갈 별도 UI 세션에 인계한다.

## 승인과 작업 위치

- 사용자 승인: 2026-09-17 `작업 진행`.
- 역할: Logic. UI 구현은 수행하지 않고 요구사항·연결 계약을 `handoff.md`에 기록한다.
- 작업 공간: `/Users/okand/SynologyDrive/asan-metaverse-user-ui`, `sy-main`, HEAD `71ba983e87e302578924d3be55936d729079cca0`.
- 시작 시 staged·unstaged·untracked 변경 없음. Git 변경은 요청·승인하지 않았다.
- 요청 명확성: `clear`, `can_proceed: true`, `approval_status: approved`.

## 확인한 근거와 선택

- 사용자 Profiler 파일의 `MeetingEntryContent`, key `camping-01` 갱신 간격은 약 1초다. `useMeetingEntry.ts`의 무조건 실행되는 interval과 일치한다.
- `useMeetingEntry`의 매초 갱신은 남은시간을 표시하는 `room` 단계로 제한한다. 다른 단계에서도 예약 종료 시각은 처리한다.
- 기존 `useAgoraLocalMedia`가 개별 장치 생성·권한 오류·트랙 해제를 소유하고, `useAgoraMeeting`이 세션과 송출을 관리한다. 이 hook들을 확장하고 기존 single-flight와 수명주기 검사를 재사용한다.
- 장치 점검에서 카메라·마이크 권한을 확인한 뒤 기본 OFF를 유지한다. 권한 거부·장치 미존재는 해당 장치 OFF로 진행한다. 회의 중 버튼은 준비된 트랙만 전환한다.
- 기존 `/meeting`도 Agora hook을 사용하므로 예약 경로의 사전 점검 계약을 명시적으로 구분한다.
- 재입장도 항상 장치 점검을 표시한다. 이용 안내 팝업의 최초 1회 정책은 기존 계약을 따른다.
- `RoomParticipant.isSpeaking`까지 연결되어 있으며 현재 `--speaker-active`는 초록색이다. UI는 기존 연결을 활용해 파란색으로 표시한다.
- UI 크기는 사용자 확인에 따라 타일 면적 1/4, 가로·세로 약 절반이다. 격자 배치와 작은 한 줄 컨트롤, `회의 나가기 → 마이크 → 카메라` 순서를 인계한다.

## 작업 순서와 완료 기준

1. 현재 작업 공간의 기존 hook 테스트에 렌더 횟수, 재입장 점검, 권한 대기·거부와 회의 중 토글 회귀 사례를 추가해 문제를 확인한다.
2. `useMeetingEntry.ts`, `useAgoraMeeting.ts`, `useAgoraLocalMedia.ts`와 필요한 route 연결을 수정한다. 다른 기능과 API 계약은 기존 구현을 재사용한다.
3. 중앙 `formatting.py apply`를 실제 workdir에서 실행한 뒤 관련 테스트, lint, 전체 테스트와 build로 결과를 확인한다.
4. `final-summary.md`와 `handoff.md`에 실제 변경·검증·미완료 UI 작업 및 작업 공간을 기록한다.

## 적용 스킬

중앙 snapshot의 `task-role-routing`, `git-branch-strategy`, `documentation`, `coding-convention`, `implementation-quality`, `type-definition`, `reference/custom-hooks`를 확인했다. 재사용 근거는 실제 hook·route·공용 Button·IconButton 및 `ui/room` 구현에서 조사했다.
