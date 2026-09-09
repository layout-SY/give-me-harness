# 최종 요약

## 결론
- async loading 템플릿을 `useAsyncTask` 공용 hook으로 외부화했다.
- id/current entity/action 정책은 `useDiscussDetailFetch` 내부 래핑으로 유지했다.

## 변경 파일
- `src/hooks/use-async-task/useAsyncTask.ts`
- `src/hooks/use-async-task/index.ts`
- `src/pages/dao/discuss-posts-management/detail/hook/useDiscussDetailFetch.tsx`
- `.agents/skills/reference/custom-hooks/use-async-task/SKILL.md`
- `.agents/skills/reference/custom-hooks/SKILL.md`
- `.codex/memory/reusable-assets.md`

## 검증
- `yarn lint`
- `./node_modules/.bin/tsc --noEmit`

## 후속 후보
- DAO proposal detail 등 반복 loading 패턴에 `useAsyncTask` 점진 적용
- 병렬 요청 카운팅이 필요한 화면이 확인되면 `useAsyncTask` 정책 확장 검토
