# 인계

## 목표 및 현재 상태

- 목표: CP 입력 날짜·strictness·board parser 정렬을 5개 atomic commit으로 기록하고 `sy-main`에 fast-forward merge한 뒤 사후 검증·worktree·branch 정리를 완료한다.
- 현재 상태: `task/domain-pattern-alignment-logic`의 5개 atomic commit을 `sy-main@5aa158a42669aef832f0031790ba964a164c88ff`에 ff-only merge하고 사후 필수 gate와 source branch·linked worktree 정리를 모두 완료했다.
- 차단 상태: 없음. 사용자 지시에 따라 GPT Sol과 native OpenCode guard만 사용했으며, merge에 사용한 임시 Claude Code 호환 command 비활성화 설정은 정리 후 제거했다.

## 완료된 작업

- 브랜치 계약: `task/domain-pattern-alignment-logic` → `sy-main@3f5b4d4b31992d421a02bc44b97276e6863ee05e`.
- production TypeScript 10개와 real-module test 4개 구현 완료.
- 필수 gate: 13/13 tests, build, 변경 파일 ESLint, `git diff --check` 성공.
- Watcher `ses_fb9ba9b04ffe1bQ1pIpnp5Hoqn`: definitive PASS, branch 결함 0건.
- Evaluator `ses_fb9a4f29dffeZpFqq53Dt5jOMu`: 현재 차단 결함 없음.
- 필수 8종 문서를 root 정본 `.codex/logs/sessions/2026-08-28-domain-pattern-alignment-logic/`에 보존.
- 사용자가 5개 atomic commit, ff-only merge, 사후 검증, worktree·branch 정리 계약을 승인.
- 승인된 5개 atomic commit 기록 완료:
  1. `9f1fee5334b3bfb1b7522f193890258aac6fd6ad refactor : ISO 달력 날짜 검증 스키마 추가`
  2. `8161de7965726bbe28535daa32a17fc617980054 fix : 시민토론과 투표 날짜 입력 검증 강화`
  3. `e84447799e91aed487cd2f250e0d402b4982dbd5 fix : 댓글과 제안 입력 스키마의 알 수 없는 키 거부`
  4. `3226960bf382047360058bc0b4c32c34e2576918 fix : 게시판과 신고 조회 입력 스키마의 알 수 없는 키 거부`
  5. `5aa158a42669aef832f0031790ba964a164c88ff refactor : 게시판 일괄 숨김 응답 파서를 API 경계로 이동`
- 별도 clean merge worktree를 `sy-main@3f5b4d4b31992d421a02bc44b97276e6863ee05e`로 생성했다.
- `sy-main`을 source HEAD `5aa158a42669aef832f0031790ba964a164c88ff`로 fast-forward했고 post-merge 13/13 tests, build, changed-file ESLint, merged range diff-check가 모두 통과했다.
- source와 merge linked worktree를 제거하고 `git branch -d task/domain-pattern-alignment-logic`로 로컬 source branch를 삭제했다.
- 임시 `/Users/okand/.config/opencode/opencode-cc-plugin.json`과 debug journal을 제거했으며 root의 다른 session 소유 dirty UI 파일 3개를 보존했다.

## 대기 중인 작업

- logic 작업 기준 대기 항목 없음.
- UI Todo 5~7은 별도 GPT Sol 브랜치 계약 승인 전까지 시작하지 않는다.

## 결정 사항 및 제약 조건

- UI Todo 5~7는 이번 branch에서 제외하며 사용자 최신 지시에 따라 Claude Code 없이 별도 GPT Sol 브랜치 승인 후 진행한다.
- 전체 lint의 기존 73 errors·5 warnings와 `npm test` script 부재는 사용자 승인 baseline 위험이다.
- commit 계획:
  1. `refactor : ISO 달력 날짜 검증 스키마 추가`
  2. `fix : 시민토론과 투표 날짜 입력 검증 강화`
  3. `fix : 댓글과 제안 입력 스키마의 알 수 없는 키 거부`
  4. `fix : 게시판과 신고 조회 입력 스키마의 알 수 없는 키 거부`
  5. `refactor : 게시판 일괄 숨김 응답 파서를 API 경계로 이동`
- cleanup 직전 source와 target `sy-main` HEAD는 모두 `5aa158a42669aef832f0031790ba964a164c88ff`이고 두 worktree는 clean이었다. 검증 후 두 linked worktree와 source branch를 제거했다.
- 중앙 시스템 프롬프트·plugin은 프로젝트에서 수정하지 않는다.

## 관련 경로

- 제거한 linked worktree: `/private/var/folders/d0/tpr2m0ld4f57x3zlndrbnxfw0000gn/T/opencode/domain-pattern-alignment-logic`
- 제거한 merge worktree: `/private/var/folders/d0/tpr2m0ld4f57x3zlndrbnxfw0000gn/T/opencode/domain-pattern-alignment-merge`
- project 배포본: `.opencode/plugins/harness.js`, `.opencode/plugins/harness_core.py`, `.opencode/plugins/branch_guard.py`
- 활성 native plugin: `/Users/okand/SynologyDrive/폐기된 외부 정책 저장소/build/admin-ui/opencode-home/plugin/harness.js`
- 실제 선행 차단 코드: `/Users/okand/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/index.js:97178`
- upstream source checkout: `/private/var/folders/d0/tpr2m0ld4f57x3zlndrbnxfw0000gn/T/opencode/oh-my-openagent/packages/omo-opencode/src/hooks/claude-code-hooks/handlers/tool-execute-before-handler.ts:23`
- upstream 회귀 테스트: `/private/var/folders/d0/tpr2m0ld4f57x3zlndrbnxfw0000gn/T/opencode/oh-my-openagent/packages/omo-opencode/src/hooks/claude-code-hooks/handlers/tool-execute-before-handler.test.ts:53`
- 중앙 Claude settings 정본: `/Users/okand/SynologyDrive/폐기된 외부 정책 저장소/source/hosts/claude/settings.json`
- 계획: `.omo/plans/domain-pattern-alignment.md`
- evidence: `.omo/evidence/domain-pattern-alignment/`

## 명령어 및 결과

- source worktree에서 5개 commit과 `git status --short --branch` clean을 확인했다.
- merge worktree에서 `git branch --show-current`: `sy-main`; HEAD `3f5b4d4b31992d421a02bc44b97276e6863ee05e`; clean.
- merge 명령은 parent, task subagent, 별도 `opencode run`에서 모두 Git 실행 전에 `현재 브랜치: task/cp-main-display-order-control`로 차단됐다.
- Todo continuation에서 merge worktree를 다시 확인한 뒤 `GIT_MASTER=1 git merge --ff-only task/domain-pattern-alignment-logic`를 재시도했으나 동일한 branch 오류로 Git 실행 전에 차단됐다. target은 여전히 clean `sy-main@3f5b4d4b31992d421a02bc44b97276e6863ee05e`다.
- OpenCode DB 실패 row: `raw_tool=bash`, `payload_workdir=/private/.../domain-pattern-alignment-merge`, `payload_cwd=NULL`.
- 활성 native plugin과 project 배포본 SHA-256은 모두 `9ed72e2e004d1f293ab19ef8c91d757d1c0e515a9fa7ed0524e11bb6fe05dc11`이고 두 파일 모두 `toolInput.workdir`를 사용한다.
- `oh-my-openagent/dist/index.js:97178-97190`의 `resolvePreToolUseCwd()`는 Bash에서 `toolInput.cwd`만 읽고, 없으면 tracked worktree·session directory로 fallback한다.
- 재시도 직후 활성 bundle `/Users/okand/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/index.js:97182`가 여전히 `nonBlankString(toolInput.cwd)`만 사용하는 것을 재확인했다.
- 후속 배포 뒤 활성 bundle `/Users/okand/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/index.js:97182-97188`이 `toolInput.workdir`를 먼저 읽고 `toolInput.cwd`로 fallback하는 것을 확인했다.
- 수정 반영 후 merge/source worktree Bash 호출은 각각 `/.../domain-pattern-alignment-{merge,logic}/.claude/hooks/harness_hook.py`가 없다는 오류로 command 실행 전에 중단됐다.
- root에는 `.claude/hooks/harness_hook.py`가 있으나 `.gitignore:33-34`가 `.claude/**`를 제외하며 두 linked worktree에는 `.claude` 디렉터리가 없다.
- 중앙 Claude settings 정본은 SessionStart·PreToolUse·Stop 모두 `$(git rev-parse --show-toplevel)/.claude/hooks/harness_hook.py`를 사용한다.
- linked merge worktree에서 `git rev-parse --path-format=absolute --git-common-dir`는 primary repository의 `/Users/okand/SynologyDrive/asan-metaverse-admin-ui/.git`을 반환하므로 그 부모를 사용하면 배포된 hook 경로를 안정적으로 찾을 수 있다.
- root에서 `git -C <merge-worktree> merge ...`를 실행하는 대안은 사용하지 않았다. `branch_guard.py`의 `_git_commands()`가 `-C`를 global option으로 정규화하지 않고 `command_denial()`이 첫 인자를 subcommand로 사용하므로 merge 전용 계보·target 검증을 건너뛸 수 있어 승인된 안전 계약의 우회가 된다.
- `.claude/settings.json:19-29`의 Claude Code `PreToolUse` hook이 이 호환 계층을 통해 native plugin보다 먼저 실행돼 session root 기준으로 차단한다.
- 당시 결론: `workdir` 계약 누락은 해결됐고, 호환 hook의 남은 문제는 ignored 배포 파일을 linked worktree의 `--show-toplevel` 아래에서 찾는 중앙 Claude settings의 경로 계산이었다. 이번 작업에서는 해당 호환 hook을 사용하지 않았다.
- 사용자 지시에 따라 `/Users/okand/.config/opencode/opencode-cc-plugin.json`에서 Claude Code 호환 command를 임시 비활성화해 linked worktree Bash를 실행했고, cleanup 완료 후 설정 파일을 제거했다.
- native OpenCode branch guard 아래에서 `git merge --ff-only task/domain-pattern-alignment-logic`가 성공해 `sy-main` HEAD가 `5aa158a42669aef832f0031790ba964a164c88ff`가 됐다.
- 검증 전용 `node_modules` symlink로 기존 설치 자산을 재사용한 뒤 post-merge 13/13 tests, build, 변경 TypeScript ESLint, merged range diff-check가 모두 통과했다.
- source·merge linked worktree와 source branch, 임시 설정·debug journal을 제거했다. 최종 worktree 목록에는 다른 session의 root worktree만 남았고 기존 dirty UI 파일 3개는 그대로다.

## 다음 조치

- logic 작업의 후속 조치 없음.
- UI Todo 5~7은 별도 GPT Sol 브랜치 계약 승인 후 진행한다.
