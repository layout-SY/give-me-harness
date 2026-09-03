# 계획

## 목표

`POST /auth/refresh` 공식 계약에 맞춰 리프레시 토큰을 1회용으로 쓰고, 응답의 새 액세스·리프레시 토큰으로 교체한다. 이미 쓴 토큰을 다시 보내지 않는다.

## 범위

- 요청 `{ refreshToken }`, 응답 SUCCESS `data`의 토큰 계약은 기존 DTO 유지
- 성공 시 새 토큰으로 저장값을 교체
- 같은 리프레시 토큰을 동시에 두 번 보내지 않음
- 갱신 실패 시 세션을 지워 재로그인하게 함

## 제외 사항

- 재로그인 화면으로의 라우팅 UX
- 탭 간 리프레시 잠금
- 로그인 계약 변경

## 제약 조건

- 사용자 스펙: 인증 없이 호출, 1회용, 재사용 시 계정 리프레시 토큰 전부 폐기 후 재로그인
- 요청·응답 형태는 이전 가정과 동일하게 확정됨

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 세션 회전 | Hephaestus | data-fetch-layer, coding-convention | 1회 전송과 교체·실패 시 세션 삭제 |
| 테스트·문서 | Hephaestus | documentation, portfolio | 회전·단일 전송·실패 테스트와 산출물 8종 |

## 검증

`npx vitest run src/features/auth`, 변경 파일 eslint

## 승인

- 상태: approved
- 승인 근거: 이전 로그인 작업에서 refresh 스키마를 요청했고, 사용자가 `POST /auth/refresh` 스펙을 제공함
