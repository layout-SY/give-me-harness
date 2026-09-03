# CP Comment stale-row FSD 산출물

## 레이어 배치
- `src/pages/cp-comment/ui/use-cp-comment-list-data.tsx`: query freshness를 화면용 계약으로 변환
- `src/pages/cp-comment/ui/use-cp-comment-list-process.tsx`: 선택·상태 변경·저장 상호작용 guard
- `src/pages/cp-comment/ui/use-cp-comment-list-controller.tsx`: data/process 조립과 optional View callback 제공
- `src/pages/cp-comment/ui/cp-comment-list.types.ts`: 페이지 View 계약 정렬

## 변경하지 않는 레이어
- `src/entities/cp-comment`: query·mutation 계약 유지
- `src/shared/ui`: 기존 optional row interaction 계약 재사용
- `src/widgets`: 적용 대상 없음

## 신규 자산
- 없음
