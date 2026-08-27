# 탐색

## 요청

사용자는 로컬 `npm run dev` 실행 시 2000 포트로 뜨도록 `package.json`을 바꾸라고 했다.

## 대상 관련 사실

- `package.json`의 `dev`는 `vite`였다.
- `vite.config.ts`의 `server.port`는 `Number(env.VITE_PORT) || 2426`이다.
- Vite CLI `--port`는 설정 파일의 `server.port`보다 우선한다.

## 불러온 스킬

- `policy/harness`, `policy/coding-convention`, `policy/documentation`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| 공용 UI | 제외 | 패키지 스크립트 변경이다 |

## 제약 조건 및 미확인 사항

- `.env`의 `VITE_PORT` 값은 확인하지 않았다. CLI `--port 2000`이 우선한다.

## 결론

`package.json`의 `dev`만 `vite --port 2000`으로 바꾼다.
