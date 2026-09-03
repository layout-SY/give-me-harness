# 계획

## 요청 요약
- 프로젝트 전역을 `src/ARCHITECTURE.md` FSD 계약으로 점검하고, 위배 항목을 관심사 세그먼트(`api`/`model`/`hook`/`lib`/`ui`)로 재배치한다.

## 작업 유형
- refactor / audit-first

## 범위 (1차, 승인 후)
- `pages/cp-survey`와 `entities/cp-survey`를 세그먼트 표준 템플릿으로 재배치한다.
- public API(`index.ts`) 경로만 유지하고 내부 파일만 이동한다. 화면 동작 변경 없음.

## 제외 범위 (1차)
- 다른 CP 페이지·엔티티 일괄 이동
- 레거시 엔티티 public API 신설 (`users`/`dao` 등)
- widget/feature 배럴 신설
- cross-entity enum 승격
- fixture 화면의 controller-view 패턴 전환

## 섹션
1. 전역 위반 목록 확정 (본 문서)
2. `cp-survey` 페이지: `ui`/`hook`/`model`/`lib` 분리
3. `cp-survey` 엔티티: query/mutation을 `model/` → `hook/` 이동

## 필요 에이전트
- Refactorer

## 필요 스킬
- policy/refactoring, policy/coding-convention, policy/hook-extraction
- src/ARCHITECTURE.md

## 리스크 / 가정
- 전 도메인 일괄 이동은 범위 불명확 대규모 수정이므로 금지한다. 템플릿 1도메인 후 복제한다.
- 동작 보존이 우선이며 import 경로만 바뀐다.

## 승인 요청
이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?
