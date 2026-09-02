# 평가 로그 (Evaluator)

## 장기 개선

1. App Certificate가 필요한 환경에서는 토큰 발급을 서버 또는 안전한 개발용 발급기로 분리하는 편이 낫다.
2. `meeting.api`의 insecure URL 검사가 주석 처리된 채 테스트만 남아 있어, 검사 복원 또는 테스트 정리가 필요하다.
3. hardcoded 모드에서는 Access Token 입력 UI를 숨기거나 안내 문구를 추가하면 혼란이 줄어든다.
