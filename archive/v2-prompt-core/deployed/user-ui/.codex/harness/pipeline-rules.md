<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/hosts/codex/harness/pipeline-rules.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 파이프라인 규칙

1. 대상 자산과 스킬을 탐색한다.
2. 범위, 역할, 검증 방법을 계획한다.
3. 명시적인 승인을 기다린다.
4. 한 구간을 구현한다.
5. Watcher가 PASS 또는 FAIL을 반환한다.
6. Evaluator가 장기적인 발견 사항을 별도로 기록한다.
7. 문서화와 최종 요약을 완료한다.

어떤 역할도 앞선 게이트를 건너뛰거나 침묵을 승인으로 해석해서는 안 된다.
