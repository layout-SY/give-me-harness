# Codex 프롬프트 경량화 평가 로그

## 결론

이번 변경은 저장소 구조와 프롬프트의 불일치를 제거하고 browser 준비 비용을 없앤다. 다만 Watcher 가용성을 자동 탐지하지 않으므로 orchestrator가 현재 환경 상태를 명시적으로 관리해야 한다.

## 구조적 개선

1. 실제 source와 reference 문서 경로를 분리했다.
2. browser QA를 제거하면서 API/parser/state 검증 자체는 유지했다.
3. 외부 의존성 비가용과 품질 반려를 서로 다른 상태로 분리했다.

## 잔여 위험

- `watcher_unavailable`은 prompt 계약이며 현재 hook이 Claude Code API 상태를 자동 감지하지 않는다.
- legacy reference 중 실제 구현이 사라진 자산은 향후 삭제 또는 대체 reference 정리가 필요하다.
- Watcher `confirmed` 전에는 Closure와 완료를 주장할 수 없다.

## 권장 후속

- Claude Code API 복구 시 `paused_after_generator` 작업만 Watcher로 이관한다.
- API 상태를 기계적으로 판정할 안정된 신호가 생길 때만 runtime hook 추가를 검토한다.
