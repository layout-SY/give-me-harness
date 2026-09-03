<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/hosts/claude/harness/pipeline-rules.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# Pipeline Rules

- No agent may skip required previous stage.
- No implementation before planner approval.
- No completion without watcher review.
- No new component before exploration of reusable assets.
- No agent may operate outside declared scope.
- Claude Code implementation is limited to the UI paths declared in `CLAUDE.md`.
- Feature logic is handed to Hephaestus through the user; it is not implemented in Claude UI files.
- Production UI completion must include `UI_COMPLETE` and the props/callback handoff.
- No review plugin, review subagent, screenshot, visual QA, or browser capture may run.
