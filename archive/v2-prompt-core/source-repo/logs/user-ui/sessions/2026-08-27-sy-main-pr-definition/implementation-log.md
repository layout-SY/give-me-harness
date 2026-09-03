# 구현 로그

## 승인된 범위

사용자가 `main` 대비 `sy-main` 작업 정의 PR 문서 작성을 요청했다. 애플리케이션 소스와 패키지 파일은 바꾸지 않았다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `.codex/logs/sessions/2026-08-27-sy-main-pr-definition/pr-definition.md` | `origin/main...sy-main` git 사실과 현재 코드를 근거로 PR 본문 작성 | GitHub에 붙여 넣을 수 있는 정의서 |
| 동일 세션 디렉터리 8종 | 템플릿 복사 후 이 작업 근거로 채움 | 문서화 정책 충족 |

## 결정 사항

- 비교 기준은 `origin/main...sy-main`(로컬 HEAD). `origin/sy-main`만 쓰면 `586908c`가 빠진다.
- 314파일 전체를 나열하지 않고 기능 묶음과 라우트 표로 정리했다.
- 워킹트리 미커밋은 “남은 제한”에만 적고 Summary 범위에서 제외했다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `git rev-list --count origin/main..sy-main` | 114 |
| `git merge-base origin/main sy-main` | `d753f0e` (`origin/main`과 동일) |
| `git diff --stat origin/main...sy-main` | 314 files, +16555, -568 |
| `git diff --stat origin/main...sy-main -- src package.json ...` | 169 files, +11783, -568 |
| `src/app/routing.ts`, `authSession.ts`, `startMocks.ts`, `attach-access-token.ts` 읽기 | 라우트·세션·MSW·Bearer 계약을 문서에 반영 |

## Watcher 인계

문서가 git 카운트·경로·현재 코드와 일치하는지 점검한다. UI 스크린샷·앱 빌드는 이 작업 범위가 아니다.
