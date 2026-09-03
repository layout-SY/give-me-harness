# 로그인 기능 Watcher 검토

## 판정

PASS

## 근거

- 로그인 API와 mutation hook 테스트 2개가 통과했다.
- 임시 로그인 form handler와 App `/login` route 테스트가 통과했다.
- 특수문자가 포함된 token fixture로 `access-token` query의 URL 인코딩과 값 보존을 확인했다.
- 실제 응답에서 profile 필드 세 개가 누락되는 fixture가 schema 수정 전 동일 Zod 오류로 실패하고 수정 후 통과했다.
- 시민참여 DTO 분리 회귀 테스트와 auth surface 테스트를 포함한 17개 테스트가 통과했다.
- auth 의존 그래프의 strict TypeScript 검증과 대상 ESLint가 통과했다.
- `npm run build`와 `npm run lint`가 통과했다.
- `as any`, `as unknown`, `@ts-ignore`, `@ts-expect-error` 사용이 없다.
- 추가 auth 파일은 모두 250 유효 LOC 이하이다.

## 남은 게이트

현재 `/login`은 사용자가 승인한 임시 테스트 페이지다. Production 로그인 UI로 교체할 때 최신 UI 계약을 다시 확인해야 한다.
