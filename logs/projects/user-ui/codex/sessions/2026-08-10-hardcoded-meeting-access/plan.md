# 계획

## 목표

백엔드 회의 API 대신 하드코딩 `MeetingAccessService`를 주입해 credential을 `useAgoraMeeting`에 전달하고, 방 생성 후 초대 코드를 화면에서 즉시 확인할 수 있게 한다.

## 범위

1. `src/features/meeting/lib/hardcodedMeetingAccess.ts` — 초대 코드 생성, 채널명 파생, create/join/refresh
2. `src/features/meeting/api/meetingAccess.service.ts` — service 계약 + hardcoded/api 구현 + mode 선택
3. `MeetingPage` — service injection, 생성 후 inviteCode 동기화
4. `MeetingStageHeader` / `MeetingAccessSummary` / `meeting.css` — 초대 코드 표시 강화
5. `useAgoraMeeting` — 빈 토큰을 `null`로 join
6. `.env` — `VITE_MEETING_ACCESS_MODE=hardcoded`
7. 관련 테스트 및 세션 문서

## 제외 사항

- App Certificate / 서버측 토큰 발급
- production UI의 대규모 리디자인
- 기존 `meeting.api` HTTPS insecure 검사 복원(범위 밖 실패 테스트)

## 제약 조건

- AGENTS.md 승인 후 구현
- Claude Code UI 소유권과 충돌할 수 있으나 사용자가 초대 코드 화면 표시를 명시 요청
- 하드코딩 기본값, API는 env로 전환

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 하드코딩 access 생성 | Hephaestus | coding-convention, data-fetch-layer, type-definition | service injection |
| MeetingPage 연결 | Hephaestus | coding-convention | hook에 credential 전달 |
| 초대 코드 UI | Hephaestus(사용자 명시 요청) | publishing/styles(기존 meeting CSS) | 화면 표시 |
| 검증 | Watcher | review-checklist | 테스트/build/lint |

## 검증

- `npx vitest run` 대상 테스트
- `npm run build`
- `npm run lint`

## 위험 요소 및 결정 사항

- Agora App Certificate 활성 시 빈 토큰 실패 → 콘솔에서 비활성 필요
- 동일 userSeq로 두 기기 접속 시 UID 충돌

## 승인

- 상태: approved (`오케이. 그럼 하드코딩된 형태를 hook에 전달하는 식으로 구현하고...`)
