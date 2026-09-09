# 계획

## 목표

액세스 토큰이 있으면 모든 API 요청에 `Authorization: Bearer` 헤더를 붙인다. 기존 `authRequired` 옵트인에 의존하지 않는다.

## 범위

- 공유 Axios 요청 인터셉터가 토큰이 있을 때 항상 헤더를 붙인다
- 인증 Axios 인스턴스에도 같은 인터셉터를 붙인다
- 회의 `fetch`는 인자 토큰이 비면 `localStorage` 토큰을 쓴다
- 헤더 부착 단위 테스트와 로그인 요청 헤더 테스트

## 제외 사항

- 토큰이 없을 때 요청을 실패시키는 동작
- 시민참여 API 파일에서 중복 `customConfig` 제거
- 회의 API의 주석 처리된 insecure URL 검증 복구

## 제약 조건

- 명시 승인 후 구현. 사용자 지시: `추가해`
- 토큰은 `localStorage`의 `access-token` 키에서 읽는다

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 전송 인터셉터 | Hephaestus | data-fetch-layer, recipe-api-authoring | 모든 Axios 요청에 Bearer |
| 테스트 | Hephaestus | coding-convention | 토큰 있음/없음 경계 |
| 문서 | Hephaestus | documentation, portfolio | 세션 산출물 8종 |

## 검증

관련 vitest, `npm run build`, `npm run lint`

## 승인

- 상태: approved
- 승인 문구: `추가해`
