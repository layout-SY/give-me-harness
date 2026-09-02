# 계획

## 목표

- 댓글 작성 가능 여부를 `/me` query 성공과 분리하고 localStorage·URL query의 auth token 존재로 판단한다.
- token이 없으면 원래 위치를 보존해 `/login`으로 이동하고, token 요청의 401은 기존 세션 만료 Dialog와 로그인 복귀 흐름을 사용한다.

## 범위

- `authSession` token presence 및 URL bootstrap
- auth presence React hook
- 보호 route의 direct login redirect
- Vote·Discussion·Policy 댓글 route의 `/me` 인증 의존 제거
- 확인 버튼·Escape 401 Dialog 종료와 `returnTo` 회귀 테스트

## 제외 사항

- backend token 유효성 선검증 및 401 자동 재요청
- 다른 탭 localStorage 변경 동기화
- 새로운 Dialog 또는 Zustand auth store 도입
- 시각 디자인·스타일 변경

## 제약 조건

- 기존 `authSession` external store와 `ApiFailureReporter → serverErrorQueue → ApiErrorDialogBridge`를 재사용한다.
- production UI는 Claude Code가 수정하고 사용자가 `UI 작업 완료`를 확인한 뒤 Hephaestus가 통합 검증한다.
- 브라우저 자동화·스크린샷·시각 QA는 프로젝트 정책상 수행하지 않는다.

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 계보·승인 | Hephaestus | `policy-git-branch-strategy` | `task/token-presence-auth-flow` 격리 |
| 탐색·설계 | Hephaestus, Explore | `policy-harness`, `policy-hook-extraction`, `policy-validation` | 중복 인증 원인과 기존 401 흐름 확정 |
| 인증 논리 | Hephaestus | `programming`, `policy-coding-convention` | external store·bootstrap·route boundary 구현 |
| production UI | Claude Code | `project-ui` | 세 댓글 route에 token presence 연결 |
| 검토 | Watcher, Evaluator | `policy-review-checklist`, `policy-codex-native-quality` | 현재 PASS 판정과 장기 권고 분리 |
| 문서 | Hephaestus | `policy-documentation`, `policy-portfolio` | 8종 정본 산출물 작성 |

## 검증

- failing-first 대상 테스트 후 관련 auth/UI suite 실행
- `npm run test`, `npm run lint`, `npm run build`
- Watcher 최종 PASS 및 Evaluator 비차단 권고 확인

## 위험 요소 및 결정 사항

- token presence는 권한 증명이 아니라 요청 가능 상태다. 최종 유효성은 backend 401이 판단한다.
- URL credential 노출 시간을 줄이기 위해 bootstrap을 모든 비동기 startup보다 먼저 실행한다.
- access 또는 refresh token 중 하나라도 non-empty이면 presence를 true로 본다.

## 승인

- 상태: approved
- 브랜치 승인: `branch:task/token-presence-auth-flow|parent:sy-main@5e2a97e495c473f348dc25a58163bdf0ea3b293e|merge:sy-main`
- 구현 승인: 사용자의 continuation 지시 후 승인 scope에서 진행
- 필수 문구: `이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?`
