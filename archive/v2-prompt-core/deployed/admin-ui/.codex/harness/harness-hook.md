<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/hosts/codex/harness/harness-hook.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# Harness 훅 계약

훅은 명시적인 승인, 관련 `SKILL.md` 확인, `src/shared/ui/` 또는 재사용 가능 자산 탐색이라는 세 가지 마커를 추적한다. 필요한 마커가 없으면 PreToolUse가 애플리케이션 변경과 미분류 local/MCP 도구를 기본 거부한다. 애플리케이션 변경을 감지할 수 있으면 Stop이 작업 산출물을 확인한다.

브랜치 guard는 `git-branch-strategy` 스킬이 기록한 작업 목적, 부모 HEAD, 직접 merge 대상, 승인 요청 식별자와 파일 범위를 실제 Git 계보와 비교한다. 기준 브랜치 직접 수정, 범위 이탈, 잘못된 merge·강제 삭제를 차단하고 SessionStart의 startup·resume·clear·compact마다 최신 `[BRANCH_CONTEXT]`를 다시 주입한다.
