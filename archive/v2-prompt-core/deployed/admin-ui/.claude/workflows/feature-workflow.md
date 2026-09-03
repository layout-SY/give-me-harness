<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/hosts/claude/workflows/feature-workflow.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# Feature Workflow

## 진입점

사용자가 Claude Code에 배정한 production UI 작업만 처리한다.

## 단계별 흐름

1. Planner가 UI 범위와 수정 가능 경로를 확정한다.
2. `src/shared/ui/`, `DESIGN.md`, 인접 UI 양식과 필요한 props/callback 계약을 탐색한다.
3. 사용자의 명시적 승인을 확인한다.
4. Publisher가 controlled UI 구조와 Hephaestus 연결 지점을 정의한다.
5. Generator가 Claude Code 소유 UI 파일만 구현한다.
6. Watcher가 별도 리뷰 agent/plugin 없이 변경 경로, 계약, 접근성과 build/lint 근거를 직접 판정한다.
7. Generator가 `UI_COMPLETE` 형식으로 사용자에게 인계한다.
8. 사용자가 UI 완료를 Hephaestus에 전달하고, Hephaestus가 최신 UI에 기능을 통합한다.

## 제한

- API, hook, util, parser, validator, store 및 상태 전이를 구현하지 않는다.
- `src/App.tsx`, `src/main.tsx`, feature barrel, package·빌드 설정과 `.codex/logs/**`를 수정하지 않는다.
- 이미지 캡처, 시각 QA, code-review, pr-review-toolkit 또는 별도 리뷰 에이전트를 실행하지 않는다.
- 현재 프로젝트 스킬은 `.agents/skills/**`를 사용하고 legacy `.claude/skills/**` 경로를 구현 근거로 사용하지 않는다.
