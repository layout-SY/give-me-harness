# 탐색

## 요청 요약

`CitizenAuxiliaryRoutes.tsx` 67–70행 부근에서 `Unsafe assignment of an error typed value`가 난다. 원인을 제거하고 검증한 뒤 짧게 설명한다.

## 대상 관련 사실

- 오류 위치는 `proposalActivityQuery = useMyProposalActivityQuery(...)`와 `proposalResponse = proposalActivityQuery.data`다
- CLI `eslint`는 해당 파일을 통과했지만, 편집기/ReadLints는 `useMyProposalActivityQuery`를 오류 유형으로 봤다
- 훅 파일 내부 최초 오류는 `citizenParticipationKeys.proposalList(query)`가 해결되지 않는 호출이었다
- `CitizenListRoutes.tsx`의 `useProposalListQuery`/`useMyProposalActivityQuery`도 같은 오류 유형을 공유했다
- `toProposalListItem`이 편집기에서 옛 `ContentListItemDto` 시그니처로 보이던 것은 pages가 feature barrel을 통해 불완전한 모듈 그래프를 보고 있었기 때문이다
- `useCitizenContentListQuery`는 같은 훅 파일에서 오류가 없었고, 명시 `UseQueryResult<z.infer<...>>`와 `proposalList` 키가 없는 쪽만 안전했다

## 관련 스킬

- `policy/harness`, `policy/coding-convention`, `policy/type-definition`, `policy/documentation`, `policy/portfolio`, `policy/review-checklist`

## `src/shared/ui/` 재사용 후보

없음. 공용 UI가 아니라 훅·DTO·import 경계의 타입 오류다.

## 제약 조건

- production UI 마크업은 바꾸지 않는다
- `any`와 eslint disable로 가리지 않는다
- 런타임 API 계약은 유지한다

## 미확인 사항

- typescript-eslint `projectService`가 루트 `tsconfig.json`(빈 `files`)에 파일을 붙이는지는 재현하지 못했다
- 전체 세션 token 소비량은 이 작업만으로 분리 측정하지 않았다

## 결론

표시 로직 버그가 아니라, (1) Zod `z.infer` + `useQuery` 추론, (2) feature barrel 재export, (3) presentation이 UI 페이지 타입을 다시 끌어오는 순환이 `useMyProposalActivityQuery`를 오류 유형으로 만든 것이다.
