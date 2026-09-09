# 최종 요약

## 제공 사항

- `npm run dev`가 `vite --port 2000`으로 실행됨

## 제외 사항

- `vite.config.ts` 기본 포트 변경
- `preview` 포트

## 검증

`package.json`의 `scripts.dev`가 `vite --port 2000`이다.

## 산출물

`.codex/logs/sessions/2026-08-27-dev-port-2000/`의 8종

## 남은 제한 사항

설정 파일만으로 `vite`를 실행하면 여전히 2426(또는 `VITE_PORT`)이다.

## 다음 단계

설정 파일 기본값도 맞출지 확정하면 된다.
