<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/hosts/codex/multi-agent-spec.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 멀티 에이전트 명세

이 인덱스는 `AGENTS.md`와 함께 역할 분리의 단일 기준이다.

1. `multi-agent-spec/01-common-and-planner.md`
2. `multi-agent-spec/02-publisher-and-generator.md`
3. `multi-agent-spec/03-refactorer-and-watcher.md`
4. `multi-agent-spec/04-evaluator-and-harness.md`
5. `multi-agent-spec/05-pipeline-and-status.md`
6. `multi-agent-spec/06-documentation-and-core-rules.md`

우선순위: 사용자 지시 > `AGENTS.md` > 이 명세 > 작업 흐름 > 역할 파일 > 스킬. 어떤 하위 계층도 승인이나 Watcher 검토를 우회할 수 없다.
