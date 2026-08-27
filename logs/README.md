# 중앙 세션 산출물 아카이브

소비자 프로젝트에서 생성된 필수 산출물 8종의 별도 Git 사본을 보관한다.

```text
logs/projects/
  user-ui/
    logic/sessions/
    claude/sessions/
  admin-ui/
    logic/sessions/
    claude/sessions/
```

- `logic`: 프로젝트의 `.codex/logs/sessions/`에서 수집한 Codex·OpenCode 산출물.
- `claude`: 프로젝트의 `.claude/logs/sessions/`에서 수집한 Claude Code 산출물.
- 대상 파일: `plan.md`, `exploration.md`, `implementation-log.md`, `grill-me-review.md`, `review-log.md`, `evaluation-log.md`, `final-summary.md`, `portfolio-log.md`.
- 같은 파일은 byte 단위 내용이 달라졌을 때만 원자적으로 교체한다.
- 원본 삭제는 중앙에 전파하지 않으며 심볼릭 링크와 대상 목록 밖 파일은 복사하지 않는다.
- 수집기는 Git add·commit을 실행하지 않는다.

수동 수집은 중앙 저장소에서 다음과 같이 실행한다.

```bash
bin/agent-policy collect-logs --project all --channel all
```
