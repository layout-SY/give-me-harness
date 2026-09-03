---
name: policy-review-checklist
description: 구현 정확성, 재사용, 요청 데이터, 성능 및 근거를 검증하는 Watcher 점검표다.
---

<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/common/skills/policy/review-checklist/SKILL.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 리뷰 점검표

목표 충족 범위, 승인 근거, 불러온 스킬, `src/shared/ui/` 재사용, 타입 안전성, 검증 및 요청 데이터 완전성, 중복 로직, 렌더링 비용, 접근성, 빌드 및 정적 분석 결과, 문서화를 확인한다. 파일 수준의 근거와 함께 PASS 또는 FAIL을 보고한다.
