# 구현 로그

## 승인된 범위

`react-router-dom` 라우팅, 공용 UI 카탈로그, 모바일 전역 스타일, 라우팅 테스트와 필수 문서만 구현했다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `package.json`, `package-lock.json` | `react-router-dom@^7.18.2` 설치 | React 19 호환 라우팅 의존성 추가 |
| `src/main.tsx`, `src/App.tsx` | `BrowserRouter`, `/`, `/ui-showcase`, fallback route 구성 | 직접 URL과 SPA route 동작 |
| `src/features/shared-ui-showcase/` | 공용 UI 상태·상호작용 카탈로그 추가 | 25개 렌더 표면과 비시각 export 설명 제공 |
| `src/index.css` | 모바일 안전 전역 baseline과 semantic token 추가 | 320px 최소 폭, focus-visible, media 크기, overflow 기준 적용 |
| `public/showcase-sample.svg` | 같은 오리진 이미지 시연 자산 추가 | ImageModal 보안 정책을 통과하는 예시 제공 |
| `DESIGN.md` | 카탈로그 계약과 해소된 부채 반영 | 디자인 계약 최신화 |

## 결정 사항

- 사용자의 “간단하게” 요청에 따라 lazy route나 추가 라우팅 계층 없이 `BrowserRouter + Routes`만 사용했다.
- legacy `src/shared/assets/css/main.css`는 포커스 제거와 고정 폭 회귀 가능성 때문에 활성화하지 않았다.
- `Loading`은 카탈로그 안에서만 absolute overlay를 해제해 다른 시연의 클릭을 막지 않게 했다.
- ImageModal 샘플은 Vite inline data URL 대신 root-relative public 자산을 사용했다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `npm run lint` | PASS |
| `npm run build` | PASS; 기존 단일 bundle 크기 경고 유지 |
| `npm audit --omit=dev --json` | PASS, 취약점 0건 |

## Watcher 인계

저장소 규칙에 따라 `npm run build`와 `npm run lint` 결과를 판정 근거로 사용한다.
