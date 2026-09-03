# 계획

## 목표

브랜치에서 AI 세션·하네스 문서 커밋을 제외하고, 이후 같은 산출물이 커밋되지 않도록 `.gitignore`에 넣는다.

## 범위

- `sy-main`에서 미푸시 AI 문서 커밋 3개 제거
- 앱 커밋 2개(`날짜 범위 선택`, `시민참여 API 계약`) 유지
- `.gitignore`에 `.codex/logs/`, `docs/admin-ui-harness-gap-analysis.md` 추가
- 제외한 세션 폴더는 워킹트리에 로컬로 복원(추적하지 않음)

## 제외 사항

- 원격 `origin/sy-main`에 이미 추적 중인 `.codex/logs` 언트래킹(`git rm --cached`)
- `.agents/`, `AGENTS.md`, `CLAUDE.md`, `.codex/templates/` 등 하네스 소스 무시
- 원격 강제 푸시

## 제약 조건

- 사용자 지시: AI 관련 커밋 내용을 gitignore하고 해당 커밋을 브랜치에서 제외
- 대화형 rebase(`git rebase -i`) 사용 금지
- 미푸시 브랜치이므로 `reset --hard origin/sy-main` 후 cherry-pick으로 재작성

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 히스토리 재작성 | Hephaestus | harness | AI 문서 커밋 제외, 앱 커밋 유지 |
| gitignore | Hephaestus | documentation | 세션 산출물 비추적 |
| 문서 | Hephaestus | documentation, portfolio | 로컬 세션 산출물 8종 |

## 검증

`git log origin/sy-main..HEAD`가 앱 2커밋 + gitignore 1커밋만 보이는지, `git status`에 세션 폴더가 untracked로 다시 나타나지 않는지 확인

## 위험 요소 및 결정 사항

- `reset --hard`는 로컬 히스토리를 바꿈. 미푸시라 원격과 충돌하지 않음
- origin에 이미 있는 `.codex/logs`(약 122파일)는 gitignore만으로는 추적 해제되지 않음

## 승인

- 상태: approved
- 승인 문구: `커밋된 내용에서 AI 관련 내용들은 .gitignore 하고 싶고, 해당 커밋들은 브랜치에서 제외 됐음 좋겠어`
