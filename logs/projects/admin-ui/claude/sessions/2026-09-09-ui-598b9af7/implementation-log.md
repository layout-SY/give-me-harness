# 구현 기록

## 신규 파일

| 경로 | 역할 |
| --- | --- |
| `src/pages/sign-in/index.ts` | `SignInPage` 배럴 |
| `src/pages/sign-in/ui/sign-in-page.tsx` | controller 연결 (`cp-dashboard-page` 패턴) |
| `src/pages/sign-in/ui/sign-in-view.tsx` | 폼 마크업과 표현 |
| `src/pages/sign-in/ui/sign-in.css` | 단독 화면 레이아웃 |
| `src/pages/sign-in/hook/use-sign-in-controller.tsx` | 입력 상태·제출·오류 메시지 |
| `src/pages/sign-in/model/sign-in.types.ts` | `SignInController` 계약 |

## 수정 파일

- `src/app/router/routes.tsx` — `SignInPage` import 추가, 관리자 셸 **밖에** `{ path: "/sign-in" }` 라우트 추가(`/meeting` 과 동일한 위치).

## UI 계약

`SignInController` — `loginId`, `password`, `errorMessage`, `isSubmitting`, `canSubmit`, `onChangeLoginId`, `onChangePassword`, `onSubmit`.
View 는 이 계약만 소비하고 API·라우팅을 직접 호출하지 않는다.

## 동작

- 제출: `<form onSubmit>` → `preventDefault` → `onSubmit()`. Enter 키 제출이 기본 동작으로 성립한다.
- 성공: `getAuthentication` 이 `commitAuthSession` 으로 토큰·인증 상태를 반영한 뒤 `/cp/dashboard` 로 `replace` 이동.
- 실패: 예외를 잡아 인라인 메시지 표시 후 비밀번호 입력을 비운다.
  - `transport` → "서버에 연결하지 못했습니다. 잠시 후 다시 시도해 주세요."
  - `server` 이면서 401/403 이 아닌 경우 → 서버 메시지 그대로
  - 그 외(401/403 포함) → "아이디 또는 비밀번호를 확인해 주세요." (계정 존재 여부를 구분해 노출하지 않는다)
- 입력을 수정하면 오류 메시지를 지운다.
- 제출 중에는 두 입력을 `disabled`, 버튼을 `isLoading` 으로 둔다. `canSubmit` 은 아이디·비밀번호가 비어 있지 않고 제출 중이 아닐 때만 참.

## 접근성

- `<label htmlFor>` ↔ `id` 연결(`sign-in-login-id`, `sign-in-password`).
- `autoComplete="username"` / `"current-password"`, 아이디 필드 `autoFocus`.
- 오류 영역 `role="alert"` + `aria-live="assertive"`.
- 오류 영역은 `min-height` 로 자리를 고정해 표시/숨김 시 버튼이 흔들리지 않는다.

## 디자인 결정

브리프가 기존 디자인 시스템을 지정했고 신규 색상 토큰 도입은 정책상 금지이므로 새 팔레트를 만들지 않았다.
카드 상단 브랜드 밴드에 좌측 GNB 와 같은 `--clr-nav-background` 를 써서 로그인 전후 화면이 같은 제품으로 읽히게 하고,
강조는 제출 버튼(`--clr-primary-500`) 한 곳으로 제한했다. 그라데이션·장식 요소는 넣지 않았다.

## 검증

- `npm run build` — 통과 (`tsc -b` + vite build, 1.17s).
- `npm run lint` — 저장소 전체 68 error / 5 warning 이 **기존부터** 존재하나, 이번 신규·수정 경로(`src/pages/sign-in/**`, `src/app/router/routes.tsx`)에서는 지적 0건.
- 시각 QA(브라우저 캡처)는 정책상 사용자 요청이 없어 수행하지 않았다.
