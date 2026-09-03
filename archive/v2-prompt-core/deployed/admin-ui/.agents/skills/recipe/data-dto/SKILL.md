---
name: recipe-data-dto
description: 타입이 지정된 요청, 응답, 쿼리, 폼-페이로드 DTO 경계를 조립합니다.
---

<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/common/skills/recipe/data-dto/SKILL.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 데이터 DTO 레시피

전송 계약을 점검하고, 불변 데이터 형태를 정의하며, 생성/수정/쿼리 DTO를 분리하고, 폼 상태를 명시적으로 매핑한 뒤 필수/선택 의미가 서버 계약과 일치하는지 검증합니다. 전송 타입과 UI 속성의 생명주기가 다르면 서로 분리합니다.
