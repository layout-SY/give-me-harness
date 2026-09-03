<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/hosts/claude/workflows/hybrid-workflow.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# Hybrid Workflow

## 단계별 흐름

1. Planner가 요청을 Claude Code UI 범위와 Hephaestus 기능 범위로 분리한다.
2. Claude Code는 UI 경로, Hephaestus는 hook/util/API/검증 경로를 병렬로 구현한다.
3. Claude Code는 기능 로직 없이 controlled props/callback 경계를 제공한다.
4. Watcher가 Claude UI 변경만 직접 판정한다.
5. Claude Code가 `UI_COMPLETE`를 사용자에게 전달한다.
6. Hephaestus는 사용자에게 `Claude Code의 UI 작업이 완료되었나요?`라고 확인한다.
7. 사용자가 완료를 확인하면 Hephaestus가 최신 UI 파일을 다시 읽고 기능을 연결한다.

## 충돌 규칙

- 동일 파일을 양쪽 세션에서 동시에 수정하지 않는다.
- `App.tsx`, `main.tsx`, feature barrel, package·빌드 설정과 `.codex/logs/**`는 Hephaestus가 소유한다.
- 충돌이 필요하면 두 작업 모두 중지하고 사용자가 파일 소유권을 결정한다.
