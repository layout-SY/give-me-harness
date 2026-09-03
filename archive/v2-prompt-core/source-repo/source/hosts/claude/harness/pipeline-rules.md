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
