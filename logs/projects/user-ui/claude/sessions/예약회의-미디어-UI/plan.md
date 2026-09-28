# 예약 회의 미디어 UI 계획

- host·role: Claude Code, `ui` (inject)
- 근거: `.codex/logs/sessions/reservation-media-check/handoff.md` (Codex logic 세션 인계)
- 작업 위치: `/Users/okand/SynologyDrive/asan-worktrees/reservation-media-check`, branch `fix/reservation-media-check`
- 사용자 결정: 컨트롤 표기는 A안(아이콘 + 짧은 글자 `나가기`·`마이크`·`카메라`, ON/OFF는 `aria-pressed`와 아이콘). 2026-09-17 `진행` 승인.

## 작업
1. 영상 격자: `RoomVideoGrid`에 `meeting-room__video-grid`를 추가하고 2열, 행 `minmax(120px, 26svh)`, 타일 최소 높이를 해제한다. 축소된 메타 영역을 조정한다.
2. 발화 테두리: 같은 범위에서 `--speaker-active`를 `var(--accent)`로 덮어쓴다.
3. 컨트롤: DOM 순서를 나가기 → 마이크 → 카메라로 바꾸고 `meeting-room__controls`로 3열 한 줄 배치한다. `micUnavailable`·`cameraUnavailable` props를 추가해 해당 버튼을 disabled 처리하고, `MeetingEntryRoute`에서 `rtc.*Unavailable`을 전달한다.
4. 장치 점검 문구: 배지·안내·주석의 "최초"와 "재입장 시 반복 없음"을 모든 입장 점검 의미로 바꾼다.
5. 테스트 보강 후 포맷·lint·build·회의 묶음 테스트를 실행한다. commit·merge는 범위 밖이다.
