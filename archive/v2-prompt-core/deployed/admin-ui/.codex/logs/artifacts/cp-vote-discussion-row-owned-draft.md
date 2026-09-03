# Vote·Discussion row-owned draft FSD 산출물

## 레이어 배치
- `src/pages/cp-vote/ui/use-cp-vote-list-process.tsx`: Vote 선택·draft·mutation 불변식
- `src/pages/cp-discussion/ui/use-cp-discussion-list-process.tsx`: Discussion 선택·draft·mutation 불변식
- `src/features/cp-status-transition/hook/useStatusTransition.ts`: 기존 공용 상태 전이 계약 재사용, 무수정

## 변경하지 않는 레이어
- `entities`: API·DTO·query·mutation 무수정
- `shared`: Dropdown·Button·Table 무수정
- `widgets`: 무수정

## 신규 자산
- 없음
