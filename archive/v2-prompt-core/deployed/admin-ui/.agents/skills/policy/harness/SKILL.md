---
name: policy-harness
description: 승인, 스킬 탐색, 재사용 가능 자산 조사, 역할 분리 및 리뷰 게이트를 강제한다.
---

<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/common/skills/policy/harness/SKILL.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 실행 체계

- 명시적인 승인 전에는 애플리케이션 코드를 수정하지 않는다.
- 관련 `SKILL.md` 파일을 불러오고 `src/shared/ui/`를 먼저 조사한다.
- Planner와 Publisher는 도메인 동작을 구현하지 않는다.
- Generator/Refactorer는 자체 승인하지 않는다.
- Watcher는 현재 작업의 pass/fail을 판정하고, Evaluator는 장기 개선 사항을 기록한다.
- 완료하려면 필수 문서와 검증 근거가 있어야 한다.
