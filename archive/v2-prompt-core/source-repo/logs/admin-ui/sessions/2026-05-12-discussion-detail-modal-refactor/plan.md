# 계획

## 요청 요약
- `discuss-posts-management` 상세 모달에서 `useDiscussDetailFetch` 내부 반복 액션 흐름을 도메인 로컬 템플릿 패턴으로 정리한다.
- pubsub 이벤트 계약은 유지하고, `_id.modal.tsx`가 open 이벤트와 상세 fetch를 조립하는 컨테이너 역할을 맡는다.

## 작업 유형
- refactor

## 범위
- `src/pages/dao/discuss-posts-management/detail/_id.modal.tsx`
- `src/pages/dao/discuss-posts-management/detail/hook/useDiscussDetailFetch.tsx`
- `src/pages/dao/discuss-posts-management/detail/useDetailModal.ts`

## 제외 범위
- pubsub 전면 리팩토링
- `src/hooks/use-pub-sub/events.ts` 계약 변경
- 댓글 상세 모달 리팩토링
- 공용 hook 신규 추출

## 섹션
1. Planner: refactor 분류, 범위 제한, 에이전트 순서 결정
2. Refactorer: 상세 액션 실행 템플릿 도입, async 흐름 정리
3. Watcher: 책임 분리, 중복 제거, 검증 결과 확인

## 필요 에이전트
- planner
- refactorer
- watcher

## 필요 스킬
- policy-orchestration
- policy-refactoring
- policy-hook-extraction
- policy-coding-convention
- hook-use-pub-sub
- policy-review-checklist

## 리스크 / 가정
- 현재 pubsub 계약은 유지한다.
- 템플릿 패턴은 도메인 로컬 helper로 제한한다.
- 삭제 성공 후 모달을 닫는 정책 변경은 이번 범위에 포함하지 않는다.

## 승인 요청
사용자가 `작업 진행`으로 승인했다.
