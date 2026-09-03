<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/hosts/codex/workflows/feature-workflow.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 기능 구현 워크플로

Planner는 관련 스킬과 `src/shared/ui/`를 탐색하고, 탐색 및 계획 문서를 작성한 뒤 승인을 요청해야 한다. 필요한 경우 Publisher가 UI 계약을 정의해야 한다. Generator는 승인된 섹션만 구현해야 한다. Watcher는 검사를 실행하고 PASS/FAIL을 반환해야 한다. Evaluator는 향후 개선 사항을 기록해야 한다. 최종 인계 전에 검증된 대화·실행·설계 근거를 `portfolio-log.md`에 추합하고 모든 문서화를 완료해야 한다.
