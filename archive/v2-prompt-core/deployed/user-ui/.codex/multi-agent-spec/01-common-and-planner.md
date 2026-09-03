<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/hosts/codex/multi-agent-spec/01-common-and-planner.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 01 공통 규칙과 Planner

모든 역할은 한 번에 하나의 논리적 구간만 작업하고, 관련 스킬만 불러오며, `src/shared/ui/`를 확인하고, 대상의 기존 규칙을 보존한다. Planner는 근거를 수집하고, 미확인 사항을 식별하고, 역할과 스킬을 배정하고, 검증 방법을 정의한 후 명시적인 승인을 요청한다. Planner는 구현하지 않는다.
