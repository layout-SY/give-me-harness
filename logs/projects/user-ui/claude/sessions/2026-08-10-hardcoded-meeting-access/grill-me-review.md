# Grill-me 리뷰

## 결정된 분기

1. **데이터 위치**: hook 내부가 아니라 `MeetingAccessService`에서 credential을 만들고 hook에 주입한다.
2. **기기 간 공유**: 서버/공유 메모리 없이 초대 코드 → 채널명 결정적 파생.
3. **토큰**: 빈 문자열 + join 시 `null` (App Certificate 비활성 전제).
4. **모드 전환**: `VITE_MEETING_ACCESS_MODE`로 hardcoded(기본)/api 선택.

## 남은 운영 주의

- 두 기기는 서로 다른 사용자 Seq를 입력해야 한다.
- Agora 콘솔에서 App Certificate가 켜져 있으면 입장이 실패할 수 있다.
