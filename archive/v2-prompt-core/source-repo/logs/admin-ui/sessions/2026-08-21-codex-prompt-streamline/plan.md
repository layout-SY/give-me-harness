# Codex 프롬프트 경량화 계획

## 결론

사용자 승인에 따라 재사용 탐색 경로, 비브라우저 QA, 도메인 실행 상태를 현재 저장소 구조와 실행 가능성에 맞춘다. 도메인 목표 순서는 `Planner → Generator → Watcher → Closure`로 유지하되 Claude Code API 비가용 중에는 Generator 이후 `paused_after_generator`로 멈춘다.

## 범위

1. `src/components`·`src/hooks` 중심의 오래된 탐색 경로를 `src/shared/ui`, `src/widgets`, 대상 도메인·페이지, reference/memory 기준으로 교체한다.
2. fresh browser·Playwright 기반 API QA 의무를 Node API/module 또는 HTTP driver 검증으로 교체한다.
3. Watcher 비가용을 반려가 아닌 `watcher_unavailable` 외부 의존성 상태로 정의하고 Closure를 차단한다.
4. 실행 훅의 exploration marker와 회귀 테스트를 새 경로에 맞춘다.

## 제외

- 제품 UI·API 코드 수정
- 역사적 `.codex/logs/**` 및 `.omo/evidence/**` 재작성
- Claude Code API 가용성 자동 감지 구현
- Watcher 실행 및 Closure confirmed 주장

## 검증

- Python hook 회귀 테스트
- Python AST와 agent TOML 파싱
- stale 탐색 경로 및 browser QA 강제 문구 검색
- 실제 source path 존재 검사
- `git diff --check`
