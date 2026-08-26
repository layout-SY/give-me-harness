## 8. 권장 전체 파이프라인

### UI 기능 작업

- 사용자 → Planner → Publisher → UI Generator → Watcher → `UI_COMPLETE`
- 사용자가 UI 완료를 Hephaestus에 중계
- Hephaestus가 최신 UI를 다시 읽고 기능을 통합

### UI 리팩터링 작업

- 사용자 → Planner → UI Refactorer → Watcher → 완료 인계

### UI·기능 병렬 작업

- Claude Code: production UI와 controlled props/callback
- Hephaestus: hook/util/API/parser/validator/store 및 상태 전이
- 동일 파일을 수정하지 않으며 통합은 `UI_COMPLETE` 확인 후 Hephaestus가 수행

### 평가 작업

- 사용자가 명시적으로 요청한 경우에만 Evaluator 실행
- 별도 리뷰 plugin/agent 없이 직접 읽고 권고 반환

## 9. 상태 전이 규격

- Planner: `draft -> ready_for_approval`
- UI Generator/Refactorer: `approved -> in_progress -> ui_complete | hold`
- Watcher: `ui_complete -> approved | rejected | escalated`
- 사용자 중계: `approved -> ui_confirmed`
- Hephaestus 통합: `ui_confirmed -> integrated`

`UI_COMPLETE` 이전에는 Claude production UI에 Hephaestus 기능을 연결하지 않는다.
