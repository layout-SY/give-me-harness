# 탐색

## 요청

Agora 미팅의 백엔드 API 응답을 프로젝트 내부 하드코딩 서비스로 주입하고, 방 생성 후 화면에 초대 코드를 표시한다. 두 기기가 같은 초대 코드로 동일 채널에 접속해 로컬 카메라/마이크를 검증할 수 있어야 한다.

## 대상 관련 사실

- `useAgoraMeeting`은 API를 호출하지 않으며 `joinRtcChannel(RtcCredential, RefreshRtcCredential)`만 받는다.
- `MeetingPage`가 `createMeeting` / `joinMeetingByInviteCode` / `joinMeetingByRtcToken`을 호출한 뒤 credential을 hook에 전달한다.
- `MeetingAccessSummary`에 초대 코드 항목이 이미 있었으나, 스테이지 헤더에는 초대 코드가 없었다.
- 기기 간 인메모리 Map은 공유되지 않으므로, 초대 코드 → `channelName` 결정적 파생이 필요하다.
- 하드코딩 토큰은 빈 문자열이며, App Certificate가 꺼진 Agora 프로젝트에서 `client.join(..., null, ...)`로 입장한다.

## 불러온 스킬

- `.agents/skills/SKILL.md`
- `policy/harness`
- `policy/documentation`
- `policy/coding-convention`
- `policy/data-fetch-layer`
- `policy/type-definition`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| 공용 배지/카드 | 재사용하지 않음 | 기존 meeting rail/stage 스타일 계약 유지가 더 적합 |

## 제약 조건 및 미확인 사항

- App Certificate가 켜진 Agora 프로젝트에서는 빈 토큰 입장이 실패한다.
- 두 기기는 서로 다른 `userSeq`(localUid)를 써야 한다.

## 결론

`MeetingAccessService` injection으로 하드코딩 구현을 기본 제공하고, API 모드는 `VITE_MEETING_ACCESS_MODE=api`로 되돌린다. UI는 요약·스테이지에 초대 코드를 강조 표시한다.
