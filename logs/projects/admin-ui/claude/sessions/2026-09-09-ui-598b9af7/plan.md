# 계획 — 관리자 로그인 화면 신설

- 작업일: 2026-09-09
- 역할: ui (inject role)
- 산출물 책임: owner
- 브랜치: `task/sign-in-page` (parent `sy-main` @ 79d31f8bf5e5cb0d72e609e76c14b1fd069b198e)
- 브랜치 승인 SHA-256: 6877330a3bb4a9a55e8341e6f0ce7fcabd9f39670dede2ff09d5e4700b256e57
- Git 통합 담당자: claude

## 사용자 요구

"현재 구현에서 login 페이지 없지?" 로 부재 여부 확인 요청. 부재를 확인해 보고한 뒤 "작업 진행" 으로 신설을 승인받았다.

## 문제 근거

- `src/pages/` 에 로그인 슬라이스가 없고 `src/app/router/routes.tsx` 에 `/sign-in` 라우트가 없다.
- 반면 `src/app/router/private-route.tsx:11` 과 `src/widgets/app-header/ui/header.tsx:18` 은 이미 `/sign-in` 으로 이동한다.
- 결과적으로 헤더에서 로그아웃하면 존재하지 않는 경로로 이동한다.

## 범위

1. `src/pages/sign-in/` 신설 — page / view / controller hook / types / css / 배럴
2. `src/app/router/routes.tsx` — 관리자 셸 밖에 `/sign-in` 라우트 추가

## 결정 사항

- **A안 채택**: 로그인 화면만 신설한다. `PrivateRoute` 를 `/cp` 에 연결하는 B안은 미인증 시 전 관리자 화면이 리다이렉트되어 개발 중 화면 확인 흐름을 깨므로 이번 범위에서 제외했다. 사용자가 A/B 중 선택을 명시하지 않아 계획서에 권장안으로 제시한 A를 적용하고 그 사실을 보고했다.
- 인증·토큰·세션 로직은 신규 작성하지 않고 기존 `useAuth().getAuthentication` 에 위임한다(UI 역할 경계 유지).
- `src/shared/ui/form` 은 react-hook-form 미설치 placeholder 라 사용하지 않고 controlled state 로 처리한다.
- 신규 색상·디자인 토큰은 도입하지 않는다(정책). `_variables.css` 와 `_cp-admin.css` 토큰만 사용한다.

## 검증 방법

- `npm run lint`
- `npm run build` (`tsc -b` 포함)
