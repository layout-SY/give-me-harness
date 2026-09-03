---
name: recipe-index
description: 반복 가능한 프런트엔드 조립 흐름을 안내하고 새로운 레시피가 필요한 시점을 판단합니다.
---

<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/common/skills/recipe/SKILL.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 레시피 색인

- `api-authoring`: typed Axios API, DTO/parser, TanStack Query 및 MSW 계약 조립.
- `data-dto`: DTO와 폼-페이로드 설계.
- `data-fetch`: 목록/상세/폼 데이터 흐름 조립.
- `i18n`: 사용자 노출 문자열 현지화.

반복되는 다단계 흐름에만 새로운 레시피를 추가합니다. 횡단 규칙은 `policy`로, 원자 단위의 재사용 가능 자산은 `reference`로 추가합니다.
