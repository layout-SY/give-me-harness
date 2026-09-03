# Codex 프롬프트 경량화 구현 로그

## 결론

운영 문서, agent prompt, workflow, harness, executable hook, reference/recipe, OMO plan을 같은 정책으로 정렬했다. 제품 코드는 수정하지 않았다.

## 적용 내용

- `AGENTS.md`와 Planner/Publisher/Generator/Watcher 계약에 실제 재사용 탐색 루트를 반영했다.
- `track-posttooluse.py`가 `src/shared/ui`, `src/widgets`, component/custom-hook reference, reusable memory 탐색을 marker로 인정하도록 수정했다.
- 탐색 템플릿과 reference/recipe의 stale 구현 경로를 실제 source path로 교체했다.
- 구현이 사라진 legacy 자산은 존재하지 않는 경로를 유지하지 않고 재탐색 필요 상태로 표시했다.
- API authoring과 두 CP remediation plan의 browser QA를 Node API/module 또는 HTTP driver 검증으로 교체했다.
- 도메인 순서를 `Planner → Generator → Watcher → Closure`로 고정하고 Watcher API 비가용 상태와 Closure 차단을 추가했다.
- `src/shared/ui`와 `src/widgets` 탐색 marker 회귀 테스트를 추가했다.

## 변경하지 않은 내용

- 과거 evidence와 세션 로그
- 제품 UI·API·MSW 코드
- Claude Code API health check 또는 자동 감지 hook

## 상태

Watcher는 사용자 지시대로 실행하지 않았다. 현재 품질 상태는 자동 검증 완료, `paused_after_generator`이며 Closure confirmed를 주장하지 않는다.
