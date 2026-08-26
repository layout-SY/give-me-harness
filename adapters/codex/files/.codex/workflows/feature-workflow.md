# 기능 구현 워크플로

Planner는 관련 스킬과 `src/shared/ui/`를 탐색하고, 탐색 및 계획 문서를 작성한 뒤 승인을 요청해야 한다. 필요한 경우 Publisher가 UI 계약을 정의해야 한다. Generator는 승인된 섹션만 구현해야 한다. Watcher는 검사를 실행하고 PASS/FAIL을 반환해야 한다. Evaluator는 향후 개선 사항을 기록해야 한다. 최종 인계 전에 검증된 대화·실행·설계 근거를 `portfolio-log.md`에 추합하고 모든 문서화를 완료해야 한다.
