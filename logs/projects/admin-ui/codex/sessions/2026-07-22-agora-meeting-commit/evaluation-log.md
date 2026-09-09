# 평가 로그

## 컨텍스트
- 라우터에 연결되지 않은 Agora 회의 이식 초안 스냅샷을 작업 단위로 커밋한다.
- 이번 평가는 커밋 pass/fail이 아닌 운영 통합 전 장기 구조 리스크를 진단한다.

## 구조적 리스크
1. P0: 회의 API가 기존 Axios/useApi 경계를 우회한다.
2. P0: Access Token, userSeq, 개발용 JSON 입장의 운영 보안 경계가 미확정이다.
3. P1: Agora SDK 정적 import로 라우터 연결 후 초기 bundle이 커질 수 있다.
4. P1: `components/hooks/services` 구조가 프로젝트 FSD 세그먼트와 다르다.
5. P1: 공용 Button/TextInput/TextArea/IconButton을 아직 재사용하지 않는다.

## 왜 중요한가
- RTC 구현 내부 응집도는 양호하지만 대상 프로젝트의 인증, API 오류 처리, UI, public API 규칙과 분리되어 있다.
- 운영 연결 전에 이 경계를 맞추지 않으면 회의 기능만 별도 규칙으로 유지된다.

## 개선 옵션
1. meeting API adapter를 Axios/useApi 경계에 연결한다.
2. route lazy loading 또는 join 시점 Agora SDK dynamic import를 적용한다.
3. 개발용 JSON 입장을 env flag 또는 dev-only route로 격리한다.
4. 공용 UI를 적용하고 meeting 전용 레이아웃만 도메인 스타일로 유지한다.
5. 공용 RTC abstraction은 화면 공유/녹화/권한 분기 추가 시점까지 보류한다.

## 권장 백로그
1. P0: 전용 token refresh 계약과 인증 identity 정책 확정
2. P0: 실제 서버 기반 두 브라우저 create/join/publish/leave/reconnect 검증
3. P1: parser/API fixture contract test 추가
4. P1: FSD 세그먼트와 `src/features/meeting/index.ts` public API 정리
5. P2: npm/yarn 중 운영 package manager 정책 단일화

## 다음 단계 제안
- 이번 초안 커밋 이후 별도 feature 작업으로 라우터/API/UI 통합을 계획한다.
