## 10. 문서화 규격

### 문서 소유권

- Claude Code orchestrator는 `.claude/logs/**`만 작성한다.
- Hephaestus는 `.codex/logs/**`를 단일 작성자로 소유한다.
- 양쪽 세션은 상대 로그를 수정하지 않는다.

### Claude UI 작업 문서

- `plan.md`: UI 범위, 수정 가능 경로와 props/callback 계약
- `exploration.md`: `src/shared/ui/`, `DESIGN.md`, 인접 UI 탐색 결과
- `implementation-log.md`: 변경한 UI 파일과 정적 검증
- `review-log.md`: Watcher 직접 판정
- `final-summary.md`: `UI_COMPLETE` 인계 내용과 UI 제한 사항

## 11. 핵심 운영 규칙

- Planner는 UI 범위를 정하고 Publisher는 계약을 정의하며 Generator/Refactorer는 UI만 수정한다.
- Watcher는 별도 reviewer 없이 직접 판정한다.
- 기능 로직과 공유 통합 파일은 Hephaestus가 소유한다.
- 충돌 시 양쪽 작업을 중지하고 사용자가 파일 소유권을 결정한다.
- UI 완료 후에만 Hephaestus가 최신 UI에 기능을 연결한다.
