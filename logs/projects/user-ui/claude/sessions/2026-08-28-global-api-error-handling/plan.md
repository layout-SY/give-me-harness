# 계획

## 목표

서버 오류는 기존 Dialog로 표시하고 contract·transport 오류는 안전하게 진단하며, `/login` 외 경로를 유효 세션으로 보호하고 401 이후 안전한 내부 URL 복귀를 제공한다.

## 범위

`src/shared/api`, `use-api`, app providers/routing/App, Auth 비-UI 계층, Meeting API, 현재 세션 문서다.

## 제외 사항

`src/shared/ui/**`, LoginPage 마크업·CSS, package/lockfile, 시민참여 보호 hook, 중앙 관리 경로는 수정하지 않는다.

## 제약 조건

기존 Dialog 계약과 native callback을 보존하고 민감 payload·token·header를 console/modal에 노출하지 않는다. screenshot·영상·시각 비교를 만들지 않는다.

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 브랜치·승인 | Hephaestus | policy-git-branch-strategy, policy-harness | 승인 scope가 고정된다 |
| 타입·API·인증 | Hephaestus | policy-coding-convention, policy-type-definition, recipe-api-authoring | 단일 typed failure 흐름이 구성된다 |
| 검증 | Watcher | policy-review-checklist | F1·F4 독립 판정이 남는다 |
| 문서 | Hephaestus | policy-documentation, policy-portfolio | 필수 8종 산출물이 완성된다 |

## 검증

Todo별 targeted Vitest, `npm run lint`, `npm run test`, `npm run build`, 실제 Chromium QA, 부모 HEAD 대비 scope 검사를 수행한다.

## 위험 요소 및 결정 사항

Axios·fetch·Query·Auth의 중복 처리와 stale refresh, active 401 중 expiry, unsafe returnTo를 주요 위험으로 두고 공통 reporter/queue와 session revision으로 해결한다.

## 승인

- 상태: approved
- 구현 및 브랜치 계약 승인 후 `task/global-api-error-handling`에서 실행했다.
