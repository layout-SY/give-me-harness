# 계획

## 목표

- 비로그인 사용자가 시민참여 보호 경로에 진입하면 보호 콘텐츠를 노출하지 않고 `로그인 후 이용해 주세요.` 안내를 표시한다.
- 사용자가 안내를 확인한 뒤 원래 상세 URL을 `returnTo`로 보존해 `/login`으로 이동한다.
- current-user 조회 경로를 `GET /citizen/me`에서 `GET /me`로 변경한다.

## 범위

- `src/app/providers`
- `src/shared/api/error`
- `src/features/citizen-participation/api`
- `src/features/citizen-participation/mocks`
- `.codex/logs/sessions/2026-08-31-login-me-routing`

## 제외 사항

- `src/**/ui/**` production UI 변경
- `/citizen/me/activity` 경로 변경
- 시민참여 상태·페이지네이션·상세 실패 처리 변경
- 패키지·빌드 설정 변경

## 제약 조건

- 기존 `Dialog`, `ApiErrorDialogBridge`, `serverErrorQueue`를 재사용한다.
- 인증 정보는 `returnTo`에 포함하지 않는다.
- 보호 콘텐츠는 로그인 안내 확인 전 렌더링하지 않는다.
- 이미지 캡처·GIF·화면 비교를 수행하지 않는다.

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 탐색·계획 | Hephaestus | `skill-index`, `policy-index`, `reference-index` | 재사용 경계와 영향 범위 확정 |
| 회귀 테스트·구현 | Hephaestus | `programming`, `policy-coding-convention`, `policy-type-definition`, `policy-hook-extraction`, `policy-validation` | 승인 동작의 최소 구현 |
| 검증 | Watcher | `policy-review-checklist` | 실행 가능한 근거로 PASS 또는 FAIL 판정 |
| 장기 평가 | Evaluator | `policy-codex-native-quality` | 현재 판정과 분리한 개선 사항 기록 |

## 검증

- 변경 동작을 고정하는 Vitest 회귀 테스트
- 변경 파일 LSP diagnostics
- `npm run lint`
- `npm run build`
- 브라우저에서 모달 확인 전 차단, 확인 후 `/login` 이동, `/me` 요청을 기능 검증

## 위험 요소 및 결정 사항

- `serverErrorQueue`는 재인증 이벤트를 우선 처리하므로 보호 경계에서 같은 위치에 대한 이벤트를 한 번만 발행한다.
- 실제 API는 무인증 상태에서 `/citizen/me`와 `/me` 모두 401을 반환했다. 인증된 `/citizen/me`의 404는 사용자 보고를 계약 근거로 삼는다.
- `/citizen/me/activity`는 다른 리소스 계약이므로 변경하지 않는다.

## 승인

- 상태: approved
- 구현 승인: 사용자 확인 완료
- 브랜치 승인: `task/fix-login-me-routing`, 부모·직접 merge 대상 `sy-main`
- 승인된 부모 HEAD: `032918b78a992776de3b7568ef9b36e7e8a37cba`
- 필수 문구: `이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?`
