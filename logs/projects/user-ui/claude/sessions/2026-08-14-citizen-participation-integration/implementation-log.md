# 시민참여 production UI 통합 구현 기록

## 완료

- `src/shared/config/citizenParticipationRoutes.ts`: 5개 detail pattern 추가.
- `src/features/citizen-participation/index.ts`: 13개 page/popup 및 controller barrel 구성.
- `src/features/citizen-participation/model/presentation.ts`: main/list/detail/comment/activity projection 구현.
- `src/features/citizen-participation/integration/useCitizenRouteState.ts`: URL page/filter/search와 service navigation 구현.
- `CitizenMainRoute.tsx`, `CitizenListRoutes.tsx`: main과 5개 목록 query 연결.
- `CitizenReadDetailRoutes.tsx`, `CitizenParticipationDetailRoutes.tsx`: 5개 detail/comments와 vote/discussion mutation 연결.
- `CitizenAuxiliaryRoutes.tsx`: proposal controlled state와 my activity query/navigation 연결.
- `src/app/routing.ts`: 13개 production route 등록.

## 보존

- `src/features/citizen-participation/ui/**`와 `src/shared/ui/**`는 수정하지 않았다.
