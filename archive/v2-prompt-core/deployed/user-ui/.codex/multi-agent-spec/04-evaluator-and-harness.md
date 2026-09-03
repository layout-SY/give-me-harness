<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/hosts/codex/multi-agent-spec/04-evaluator-and-harness.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 04 Evaluator와 Harness

Evaluator는 Watcher 이후에 수행하며 현재 판정을 바꾸지 않은 채 장기적인 아키텍처, 프로세스, 재사용, 기술 부채 개선 기회를 기록한다. Harness 훅은 호스트 엔진이 설정된 이벤트를 지원하는 범위에서 명시적인 승인, 스킬 및 재사용 근거, 문서화를 강제한다.
