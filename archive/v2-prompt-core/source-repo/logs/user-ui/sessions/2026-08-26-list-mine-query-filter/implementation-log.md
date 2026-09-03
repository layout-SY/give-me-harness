# 구현 로그

## 승인된 범위

목록 「내 활동만 보기」를 `/me/activity`에서 각 목록 API의 `mine=true|false`로 바꾼다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `proposal.api.ts` | `mine`을 항상 `true`/`false`로 전송 | 기본 목록도 `mine=false` |
| `vote.dto.ts` / `vote.api.ts` | `mine?`, 전송·인증 | 투표 목록이 같은 query 계약을 씀 |
| `content.dto.ts` | `mine?` | 토론·정책 목록 query에 포함 |
| `discussion.api.ts` / `policy.api.ts` | 명시 params + 조건부 `customConfig` | `mine=false`도 전송 |
| `queryKeys.ts` / 목록 훅 | `mine`을 key에 고정 | true/false가 다른 캐시 |
| `CitizenListRoutes.tsx` | activity 분기 제거 | 목록이 단일 list query |
| `useCitizenParticipationQueries.ts` | `useMyProposalActivityQuery` 삭제 | 별도 제안 activity 훅 없음 |
| `CitizenAuxiliaryRoutes.tsx` | 제안 탭이 `useProposalListQuery({ mine: true })` | 내 활동 페이지 제안도 목록 API |
| MSW handlers/fixtures | 모든 타입 `mine` 필터, activity 제안 DTO 분기 제거 | 목록 필터가 list endpoint를 재현 |

## 결정 사항

- `mine`이 없거나 false면 전체 목록이다. `mine=false`를 query에 명시한다.
- 설문 목록에는 `mine`을 붙이지 않는다.
- 내 활동 페이지의 전체/투표 등 비제안 필터는 `/me/activity`를 유지한다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `npx vitest run src/pages/citizen-participation/ui/CitizenDataRoutes.test.tsx src/features/citizen-participation src/pages/citizen-participation/model` | 9 files / 66 tests passed |
| `npm run build` | `tsc -b && vite build` 성공 |
| `npm run lint` | exit 0 |

## Watcher 인계

현재 변경은 목록 필터 전송 계약이다. UI 시각 QA는 수행하지 않았고, 검증은 테스트·build·lint다.
