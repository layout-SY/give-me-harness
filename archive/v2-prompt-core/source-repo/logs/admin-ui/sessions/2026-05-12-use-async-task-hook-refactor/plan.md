# 계획

## 요청 요약
- `useDiscussDetailFetch`에 있던 async loading 템플릿을 공용 hook으로 외부화한다.
- 공용 hook은 id, DAO, pubsub, Dialog를 알지 않게 하고 도메인 hook에서 한 번 더 감싼다.

## 작업 유형
- refactor

## 범위
- `src/hooks/use-async-task/useAsyncTask.ts`
- `src/hooks/use-async-task/index.ts`
- `src/pages/dao/discuss-posts-management/detail/hook/useDiscussDetailFetch.tsx`

## 제외 범위
- id-aware 공용 hook
- Dialog/pubsub/success message 포함 공용 action hook
- 다른 도메인 일괄 적용
- pubsub 계약 변경

## 섹션
1. Planner: 공용화 수준 결정
2. Refactorer: `useAsyncTask` 생성 및 도메인 hook 적용
3. Watcher: 과추상화, 의존 방향, 타입/검증 결과 확인

## 필요 에이전트
- planner
- refactorer
- watcher

## 필요 스킬
- policy-orchestration
- policy-refactoring
- policy-hook-extraction
- policy-abstraction-strategy
- policy-coding-convention

## 리스크 / 가정
- 공용 hook은 async task 실행과 loading 상태만 담당한다.
- 도메인 정책은 `useDiscussDetailFetch`에 남긴다.

## 승인 요청
사용자가 "오케이. 이대로 워크플로우 진행."으로 승인했다.
