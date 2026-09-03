<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/hosts/codex/workflows/escalation-workflow.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 에스컬레이션 워크플로

작업이 차단되면 시도한 조치, 근거, 정확한 차단 요인, 필요한 결정을 기록해야 한다. 근거에 기반한 재시도가 한 번 실패하면 Planner에게 돌아가야 한다. 보안, 데이터 손실, 의존성 또는 아키텍처와 관련된 결정은 계속 진행하기 전에 사용자의 확인을 받아야 한다.
