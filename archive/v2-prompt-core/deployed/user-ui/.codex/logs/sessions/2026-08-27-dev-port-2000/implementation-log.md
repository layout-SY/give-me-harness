# 구현 로그

## 승인된 범위

`npm run dev`가 2000 포트에서 실행되게 `package.json`을 변경한다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `package.json` | `"dev": "vite --port 2000"` | CLI가 설정 파일의 2426보다 우선한다 |

## 결정 사항

- 사용자가 `package.json`만 지정했으므로 `vite.config.ts`는 건드리지 않는다.

## 검증 근거

| 확인 | 결과 |
| --- | --- |
| `package.json` scripts.dev | `vite --port 2000` |

## Watcher 인계

스크립트 한 줄 변경이다. 개발 서버는 상시 실행하지 않았다.
