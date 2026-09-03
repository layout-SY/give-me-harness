# 최종 요약

하드코딩 `MeetingAccessService`를 기본으로 주입해 백엔드 없이 회의 create/join credential을 만들고 `useAgoraMeeting`에 전달한다. 방 생성 후 초대 코드는 준비 패널 요약과 스테이지 메타에 표시되며, 다른 기기는 같은 초대 코드와 다른 사용자 Seq로 동일 채널에 참가할 수 있다. API 모드는 `VITE_MEETING_ACCESS_MODE=api`로 되돌린다.
