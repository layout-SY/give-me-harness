# 계획

## 요청 요약
- 사용자 활동 상세 페이지를 vote/survey와 같은 page/controller/view + entity query 패턴으로 맞춘다.

## 작업 유형
- hybrid (페이지 구조 리팩터 + 상세 조회 entity/MSW 결선)

## 범위
- `src/pages/cp-activity-log/ui/` 사용자 활동 상세
- `src/entities/cp-activity-log/` 상세 조회 API·DTO·parser·query
- `src/mocks/cp-activity-log.handlers.ts` 및 handlers 등록

## 제외 범위
- `cp-activity-log-page.tsx` 목록
- 처리 저장/mutation (읽기 전용)
- 공용 CP 상세 추상화 훅

## 섹션
1. 상세 조회 entity + MSW를 survey/vote 계약으로 맞추고, 페이지를 controller/view로 분해한다.
   - 담당: Refactorer
   - process 훅 없음. 조회 실패 Dialog·다시 조회는 vote 상세와 동일.

## 필요 에이전트
- Refactorer
- Watcher: 비가용 → `paused_after_generator`

## 필요 스킬
- policy-refactoring, policy-coding-convention, policy-hook-extraction, policy-type-definition, policy-tanstack-query, recipe-api-authoring

## 리스크 / 가정
- 서버 계약은 MSW 임시 계약이다. GET `/v1/cp/activity-logs/users/:userId`
- 목록 페이지는 계속 fixture를 직접 읽는다.

## 승인 요청
사용자 요청에 `진행해`가 포함되어 본 섹션을 실행한다.
