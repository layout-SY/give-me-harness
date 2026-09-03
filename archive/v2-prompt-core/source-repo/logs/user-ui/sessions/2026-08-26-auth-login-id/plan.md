# 계획

## 목표

로그인 입력을 이메일이 아닌 `loginId` 문자열로 바꾸고, 인증 없이 `POST /auth/login`으로 액세스·리프레시 토큰을 받은 뒤 `expiresIn`이 지나기 전에 `POST /auth/refresh`로 갱신한다.

## 범위

- 로그인 요청 `{ loginId, password }`, 응답 `code: SUCCESS`의 `data` 토큰 계약
- 엔드포인트 `/auth/login`, `/auth/refresh`
- 로그인·리프레시 요청에 `Authorization`을 붙이지 않음
- 세션 저장과 만료 전 갱신 스케줄
- 로그인 UI 라벨·props를 아이디 문자열로 변경
- 관련 테스트

## 제외 사항

- 아이디 없음/비밀번호 틀림을 서로 다른 오류로 나누는 클라이언트 분기
- 리프레시 실패 시 강제 로그아웃 UX
- `oasisapp://login` 딥링크 제거
- 회의 API insecure URL 검증 복구

## 제약 조건

- 명시 승인 후 구현. 사용자 지시: `이를 반영해`
- 로그인 예시 토큰 payload에 `exp`가 없어 JWT 유틸로 만료를 읽지 않는다
- 리프레시 요청 본문 스키마는 사용자가 주지 않음. `{ refreshToken }`으로 전송한다

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| DTO/API | Hephaestus | data-fetch-layer, recipe-api-authoring, recipe-data-dto, type-definition | loginId 계약과 무인증 전송 |
| 세션 갱신 | Hephaestus | hook-extraction, coding-convention | expiresIn 전 refresh |
| 로그인 UI | Hephaestus | publishing, validation | 아이디 필드와 동일 실패 문구 |
| 문서 | Hephaestus | documentation, portfolio | 세션 산출물 8종 |

## 검증

auth feature vitest, `npm run build`, `npm run lint`

## 승인

- 상태: approved
- 승인 문구: `이를 반영해`
