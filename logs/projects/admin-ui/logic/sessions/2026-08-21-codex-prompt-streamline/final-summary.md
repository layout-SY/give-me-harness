# Codex 프롬프트 경량화 요약

## 변경 결과

- 재사용 탐색 경로를 `src/shared/ui`, `src/widgets`, 대상 도메인·페이지, reference/memory로 통일했다.
- stale component/custom-hook reference 경로를 실제 source로 교체했다.
- fresh browser·Playwright QA 의무를 Node API/module 또는 HTTP driver 검증으로 교체했다.
- 도메인 실행을 `Planner → Generator → Watcher → Closure`로 명시했다.
- Claude Code API 비가용 중에는 Watcher를 실행하지 않고 `paused_after_generator`로 보류하며 Closure를 차단한다.
- 실행 hook이 새 탐색 경로를 marker로 인정하도록 수정하고 회귀 테스트를 추가했다.

## 검증

- hook regression: pass
- Python syntax: pass
- TOML parse: pass
- stale governing path: 0건
- positive browser QA mandate: 0건
- mapped source paths: 모두 존재
- whitespace error: 0건
- LSP: Python LSP 미설치 및 기존 설치 거절로 N/A
- no-excuse checker: `uv` 미설치로 skip

## 현재 상태

사용자 지시에 따라 Watcher는 실행하지 않았다. 자동 검증은 통과했지만 Watcher `confirmed`와 Closure 완료는 미청구다.
