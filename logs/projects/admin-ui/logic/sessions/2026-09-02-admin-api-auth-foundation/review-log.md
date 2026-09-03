# 검토 로그

## Watcher 판정

PASS

## 검토 범위

- source: `task/admin-api-auth-foundation`
- parent·직접 merge 대상: `sy-main@ad687ac00c897163046d27b2f48bf9f2ae55d5b3`
- 핵심 재검토: silent refresh 401과 SIGBUS 원인 문서화
- 제외: production `/sign-in`, route guard, browser·capture·시각 QA, sibling spinner 변경

## 점검 결과

| 점검 | 결과 | 근거 |
| --- | --- | --- |
| 승인·범위 | 통과 | dirty 경로와 최종 25개 병합 파일이 승인 scope에 포함됐다. |
| 공용 UI 재사용 | 통과 | `ApiErrorDialogBridge`가 기존 `src/shared/ui/dialog`를 재사용한다. |
| silent refresh 401 | 통과 | reporter가 401을 presentation보다 먼저 `reauthenticate` queue로 보낸다. |
| sign-in 401 분리 | 통과 | `useApi`가 typed behavior를 전달하고 sign-in만 `error`로 opt-out한다. |
| 인증 세션 | 통과 | token presence, revision, stale refresh, URL bootstrap을 한 경계에서 처리한다. |
| 민감 정보 | 통과 | allowlist failure·diagnostics와 고정 401 presentation을 사용한다. |
| 타입 | 통과 | auth parser와 behavior option에 명시적 타입을 적용하고 `any` 억제를 추가하지 않았다. |
| 회귀 테스트 | 통과 | reporter 7/7, 신규 25/25, 전체 직렬 73/73이다. |
| build·lint·diff | 통과 | build 성공, targeted ESLint 0 errors·기준선 warning 1건, diff check 통과다. |
| 문서 | 통과 | RED→GREEN, 상충 SIGBUS 관찰, 도구 제한과 최종 검증을 기록했다. |

## 이전 발견 처리

1. 높음: silent refresh 401 차단
   - 해결: 401 분기 순서 수정, `UnauthorizedBehavior` 전달, sign-in opt-out
   - 검증: failing-first 실제 queue `[]`, 수정 후 reporter 7/7과 신규 25/25
2. 중간: cache-only SIGBUS 원인 단정
   - 해결: no-cache에서도 이동한 실패 기록을 보존하고 원인을 기존 Vite/Rolldown native child 불안정으로 제한

## 병합 후 확인

- `task/admin-api-auth-foundation`의 13개 커밋은 `sy-main`에 fast-forward 반영됐다.
- target HEAD: `25f41f202d7bf042ae0cfddce9032b99bb904c72`
- 사후 build, 신규 25/25, 전체 73/73, targeted ESLint, diff check가 통과했다.
- 차단 또는 필수 후속 조치는 없다.
