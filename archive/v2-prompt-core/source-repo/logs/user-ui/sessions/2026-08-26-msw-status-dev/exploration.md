# 탐색

## 요청

사용자는 모의 서버 사용 여부를 `.env`의 `VITE_API_BASE_URL_STATUS`가 `dev`일 때만으로 제한하라고 했다.

## 대상 관련 사실

- `src/main.tsx`는 앱 렌더 전에 `startMocks()`를 기다린다.
- 기존 `startMocks`는 `VITE_ENABLE_MSW`와 Vite `import.meta.env.DEV`를 썼다. 개발 모드에서는 기본으로 MSW를 켰다.
- 브라우저 worker는 `src/app/mocks/browser.ts`의 `setupWorker`다.
- 단위 테스트는 `msw/node` `setupServer`를 직접 쓰므로 `startMocks`와 무관하다.
- `ImportMetaEnv`는 `src/features/meeting/config/vite-env.d.ts`에 있다.
- `.env`는 gitignore다. `!.env.template` 예외가 있으나 템플릿 파일은 없다.

## 불러온 스킬

- `.agents/skills/SKILL.md`
- `policy/harness`, `policy/coding-convention`, `policy/type-definition`, `policy/documentation`, `policy/portfolio`, `policy/abstraction-strategy`, `policy/codex-native-quality`, `policy/review-checklist`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| 공용 UI | 제외 | 환경 변수로 모의 서버를 켜는 작업이며 UI가 아니다 |

## 제약 조건 및 미확인 사항

- `dev` 외 값(`prod`, 빈 값, 대문자 `DEV`)의 의미는 사용자가 정의하지 않았다. `dev`가 아니면 모의를 켜지 않는다.
- Vite 개발 모드여도 status가 `dev`가 아니면 모의를 켜지 않는다.

## 결론

모의 서버의 단일 스위치는 `VITE_API_BASE_URL_STATUS`. 기존 `VITE_ENABLE_MSW`와 DEV 기본 켜짐은 제거한다.
