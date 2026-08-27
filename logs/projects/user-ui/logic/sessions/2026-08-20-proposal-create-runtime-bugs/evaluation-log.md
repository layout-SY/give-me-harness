# 평가 로그

## 현재 판정과의 경계

현재 수정의 PASS/FAIL을 반복하지 않고 장기 개선 사항을 기록한다.

## 장기 관찰 사항

- 외부 controlled UI에 React Hook Form 값을 전달할 때 `useWatch`처럼 명시적 구독 경계를 사용하는 편이 계약이 선명하다.
- mock 생성 API는 성공 응답뿐 아니라 ID 유일성과 후속 조회를 모사해야 route navigation 테스트가 현실적이다.

## 목록에 등록할 재사용 가능 자산

- StrictMode 문자 단위 controlled input route test 패턴.
- fixture 충돌을 피하는 deterministic mock ID sequence.

## 기술 부채

- 실제 브라우저의 최초 입력 손실 증상은 프로젝트 정책상 자동 브라우저 재현하지 못했다.
- full suite의 범위 밖 실패 4건과 comment key warning이 남아 있다.

## 프로세스 개선 사항

- form route 테스트는 완성 문자열 1회 주입보다 문자 단위 입력과 request body를 함께 검증한다.
- mock mutation 테스트는 고정 성공 ID가 아니라 연속 생성의 유일성을 검증한다.

## 권고 사항

사용자 확인 후 브라우저 증상이 남으면 production UI 소유자인 Claude Code에 HeroUI 실제 이벤트 trace를 별도 요청한다.
