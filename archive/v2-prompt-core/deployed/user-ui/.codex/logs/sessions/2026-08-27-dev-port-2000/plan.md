# 계획

## 목표

로컬 `npm run dev`가 2000 포트에서 실행되게 한다.

## 범위

- `package.json`의 `dev` 스크립트에 `--port 2000` 추가

## 제외 사항

- `preview` 포트 변경
- `vite.config.ts`의 `server.port` 기본값(2426) 변경
- `.env`의 `VITE_PORT` 도입

## 제약 조건

- 사용자 지시: `@package.json`만 변경
- 승인 문구: `변경해줘`

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 스크립트 | Hephaestus | coding-convention, documentation | `dev`가 2000 포트 사용 |

## 검증

`package.json`의 `dev` 값이 `vite --port 2000`인지 확인

## 승인

- 상태: approved
- 승인 문구: `변경해줘`
