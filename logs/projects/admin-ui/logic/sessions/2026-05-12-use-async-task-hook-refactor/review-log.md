# 리뷰 로그

## 리뷰 대상
- `src/hooks/use-async-task/useAsyncTask.ts`
- `src/hooks/use-async-task/index.ts`
- `src/pages/dao/discuss-posts-management/detail/hook/useDiscussDetailFetch.tsx`
- `.agents/skills/reference/custom-hooks/use-async-task/SKILL.md`
- `.agents/skills/reference/custom-hooks/SKILL.md`
- `.codex/memory/reusable-assets.md`

## 결과
- pass

## 체크리스트 검토
- SKILL 준수: 통과. 공용 hook은 도메인 무관 async task runner로 제한됨.
- 재사용 확인: 통과. `useApi`, `usePubSub`, `useDialog` 기존 자산 유지.
- 검증 확인: 통과. `yarn lint`, `tsc --noEmit` 통과.
- Payload 완결성: 통과. API/pubsub payload 변경 없음.
- 성능 우려: 통과. 신규 hook callback은 안정 참조로 반환됨.
- 중복 코드 우려: 통과. 로컬 `runWithLoading` 제거.
- reference 문서화: 통과. 신규 공용 hook guide와 reusable-assets 항목 추가.

## 위반 사항
1. 없음

## 필수 수정 사항
1. 없음

## 반복 이슈
- false

## 에스컬레이션
- none
