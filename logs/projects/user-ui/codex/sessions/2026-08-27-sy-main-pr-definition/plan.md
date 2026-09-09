# 계획

## 목표

`origin/main`과 `sy-main`의 커밋·파일 diff를 근거로, GitHub PR 본문으로 쓸 수 있는 작업 정의 문서를 작성한다.

## 범위

- 비교: `origin/main`(`d753f0e`)...로컬 `sy-main`
- 산출물: `.codex/logs/sessions/2026-08-27-sy-main-pr-definition/pr-definition.md` 및 필수 8종
- 애플리케이션 소스·패키지 파일은 수정하지 않는다

## 제외 사항

- PR 생성, push, 원격 계정 수정
- 미커밋 `AGENTS.md`·`package.json`을 PR 범위에 포함
- `npm run test`/`lint`/`build` 실행(문서 작업이며 앱 변경 없음)

## 제약 조건

- 사용자 응답과 산출물은 한국어
- 이전 세션 산출물을 현재 근거로 재사용하지 않음
- 관찰한 git 사실과 권고를 구분

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 탐색 | Hephaestus | policy/documentation, policy/harness | 브랜치·diff·라우트·인증 계약 확인 |
| 문서 | Hephaestus | policy/documentation, policy/portfolio | PR 정의서와 8종 산출물 |
| 검토 | Watcher(문서) | policy/review-checklist | 문서가 git 사실과 일치하는지 판정 |

## 검증

- `git log origin/main..sy-main`, `git diff --name-status origin/main...sy-main`
- 현재 코드에서 라우트·인증·MSW 계약을 직접 읽음

## 위험 요소 및 결정 사항

- `.codex` 세션 파일이 diff 314개 중 상당수를 차지한다. PR 본문에는 앱 기능을 앞에 두고, 하네스 파일은 규모 주로만 적는다.
- 워킹트리 미커밋은 PR 범위에서 제외한다고 명시한다.

## 승인

- 상태: 사용자가 `정의 PR 문서 만들어`로 문서 작성을 요청함
- 애플리케이션 코드 변경 없음
