# 최종 요약

## 제공 사항

- 브라우저 MSW는 `VITE_API_BASE_URL_STATUS`가 `dev`일 때만 시작
- `VITE_ENABLE_MSW`와 개발 모드 기본 켜짐 제거
- 로컬 `.env`에 `VITE_API_BASE_URL_STATUS=dev` 추가 (gitignore)

## 제외 사항

- 테스트용 `msw/node`
- `VITE_API_BASE_URL` 값 자체 변경
- README

## 검증

| 명령어 | 결과 |
| --- | --- |
| `npx vitest run src/app/mocks/startMocks.test.ts` | 4 passed |
| `npm run build` | 성공 |
| `npm run lint` | 성공 |

## 산출물

`.codex/logs/sessions/2026-08-26-msw-status-dev/`의 plan, exploration, implementation-log, grill-me-review, review-log, evaluation-log, final-summary, portfolio-log

## 남은 제한 사항

- `dev`가 아니면 모의가 꺼지므로 실 API를 친다.
- 배포 env에 `dev`를 넣으면 프로덕션에서도 MSW가 뜰 수 있다.

## 다음 단계

실 API를 쓰려면 `VITE_API_BASE_URL_STATUS`를 `dev`가 아닌 값으로 둔다.
