# 구현 로그

## 결론

하드코딩 `MeetingAccessService`를 기본 주입하고, 방 생성/참가 결과를 `useAgoraMeeting.joinRtcChannel`에 전달하도록 연결했다. 초대 코드는 레일 요약과 스테이지 메타에 강조 표시된다.

## 변경 파일

- `src/features/meeting/lib/hardcodedMeetingAccess.ts` (+ test)
- `src/features/meeting/api/meetingAccess.service.ts` (+ test)
- `src/features/meeting/ui/MeetingPage.tsx` (+ test mock 갱신)
- `src/features/meeting/hook/useAgoraMeeting.ts` — 빈 토큰을 `null`로 join
- `src/features/meeting/ui/stage/MeetingStageHeader.tsx`
- `src/features/meeting/ui/preparation/MeetingAccessSummary.tsx`
- `src/features/meeting/ui/meeting.css`
- `src/features/meeting/config/vite-env.d.ts`
- `.env` — `VITE_MEETING_ACCESS_MODE=hardcoded`

## 동작

1. 방 생성 → 6자리 초대 코드 생성, `channelName = mtg-{inviteCode}`, host `userSeq`를 localUid로 사용
2. 초대 코드 참가 → 동일 채널명 파생, 참가자 `userSeq`를 localUid로 사용
3. refresh → 동일 채널/UID credential 재생성(빈 토큰)
4. API 모드 복귀: `VITE_MEETING_ACCESS_MODE=api`

## 검증 명령

```bash
npx vitest run src/features/meeting/lib/hardcodedMeetingAccess.test.ts src/features/meeting/api/meetingAccess.service.test.ts src/features/meeting/ui/MeetingPage.test.tsx
npm run build
npm run lint
```

결과: 대상 테스트 7/7 통과, build 성공, lint 통과.
