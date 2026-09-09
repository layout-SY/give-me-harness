# 계획

## 목표

목록의 「내 활동만 보기」에서 `/me/activity` 별도 API를 제거하고, 제안 목록과 같이 각 목록 요청의 `mine=true|false` query로 통일한다.

## 범위

- 제안·투표·토론·정책 목록 전송에 `mine`을 항상 `true` 또는 `false`로 붙인다
- 목록 라우트의 `useMyActivityQuery` / `useMyProposalActivityQuery` 분기를 제거한다
- `useMyProposalActivityQuery`를 삭제하고, 내 활동 페이지의 제안 필터는 `useProposalListQuery({ mine: true })`를 쓴다
- MSW 목록 `mine=true` 필터를 제안 외 타입에도 적용하고, activity의 제안 전용 목록 DTO 분기를 제거한다

## 제외 사항

- 내 활동 페이지(`/me/activity`) 자체와 `content` 없는 전체 활동 조회
- 설문 목록 `mine` (토글이 없다)
- 정렬 UI, 목록 카드 summary 제거
- 투표·토론·정책 목록 응답 DTO 재설계

## 제약 조건

- 명시 승인 후 구현. 사용자 지시: `변경해`
- `mine=false`는 전체 목록, `mine=true`는 토큰 사용자 항목이다
- 인증 설정은 `mine===true`일 때만 붙인다

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| DTO/전송 | Hephaestus | recipe-api-authoring, recipe-data-dto, type-definition | 목록 URL에 `mine=true|false` |
| 훅/라우트 | Hephaestus | data-fetch-layer, hook-extraction | 목록이 단일 list query |
| MSW/테스트 | Hephaestus | recipe-api-authoring | 별도 activity 목록 필터가 사라짐 |
| 문서 | Hephaestus | documentation, portfolio | 세션 산출물 8종 |

## 검증

`npx vitest run` (관련 스위트), `npm run build`, `npm run lint`

## 승인

- 상태: approved
- 승인 문구: `변경해`
