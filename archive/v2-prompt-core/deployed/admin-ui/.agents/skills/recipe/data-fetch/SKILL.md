---
name: recipe-data-fetch
description: 전송, 연산, 훅, UI 계층을 사용해 타입이 지정된 데이터 조회 화면을 조립합니다.
---

<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/common/skills/recipe/data-fetch/SKILL.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 데이터 조회 레시피

1. `src/shared/ui/`와 `reference` 스킬을 검색합니다.
2. DTO와 전송 연산을 정의합니다.
3. 로딩/오류/취소를 처리하는 상태 훅을 추가합니다.
4. 기존 테이블, 페이지네이션, 폼, 모달 어댑터가 있으면 이를 조합합니다.
5. 새로고침, 빈 상태, 오류, 제출 결과를 검증합니다.
