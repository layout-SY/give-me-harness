# 계획

## 목표

브라우저 MSW 모의 서버는 `.env`의 `VITE_API_BASE_URL_STATUS`가 `dev`일 때만 시작한다.

## 범위

- `startMocks`가 `VITE_ENABLE_MSW`와 Vite `DEV` 기본값 대신 `VITE_API_BASE_URL_STATUS === "dev"`만 본다
- `ImportMetaEnv`에 `VITE_API_BASE_URL_STATUS`를 추가하고 `VITE_ENABLE_MSW`를 제거한다
- `startMocks` 테스트를 새 계약에 맞춘다
- 로컬 `.env`에 `VITE_API_BASE_URL_STATUS=dev`를 넣는다

## 제외 사항

- 테스트용 `msw/node` `setupServer` (이미 테스트가 직접 켠다)
- API base URL 선택 로직 (`VITE_API_BASE_URL` 자체)
- README 변경

## 제약 조건

- 명시 승인 후 구현. 사용자 지시: `추가해줘`
- 값은 앞뒤 공백을 제거한 뒤 `dev`와 정확히 비교한다

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 모의 시작 조건 | Hephaestus | coding-convention, type-definition | `dev`일 때만 worker.start |
| 테스트 | Hephaestus | review-checklist | 켜짐/꺼짐 경계를 고정 |
| 문서 | Hephaestus | documentation, portfolio | 세션 산출물 8종 |

## 검증

`npx vitest run src/app/mocks/startMocks.test.ts`, `npm run build`, `npm run lint`

## 승인

- 상태: approved
- 승인 문구: `추가해줘`
