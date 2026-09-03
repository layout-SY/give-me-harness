# 구현 로그

## 승인된 범위

proposal list 요청/응답 DTO를 확정 구조로 재설계하고, list 요청은 `page`/`size`만 보내며, 내 활동 필터는 `content`·`page`·`size`를 쓰는 별도 activity API로 연결한다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `src/features/citizen-participation/api/proposal/proposal.dto.ts` | `GetProposalListQueryDto`/`GetProposalListResponseDto` 추가 | 확정 JSON과 같은 목록 계약 |
| `src/features/citizen-participation/api/proposal/proposal.api.ts` | `params: { page, size }`만 전송 | 필터 필드가 list URL에 실리지 않음 |
| `src/features/citizen-participation/api/me/me.dto.ts` | `type` 제거, `content?`·`page`·`size` | activity 요청이 페이지 출처를 구분 |
| `src/features/citizen-participation/api/http/citizenParticipation.parser.ts` | `parseProposalList` 추가 | 알 수 없는 목록 값을 좁힘 |
| `src/features/citizen-participation/hook/useCitizenParticipationQueries.ts` | `useProposalListQuery` 분리, activity `enabled` 분기 | list와 내 활동이 다른 query key를 사용 |
| `src/features/citizen-participation/mocks/handlers.ts` | proposal list SUCCESS envelope, activity `content` 페이징 | MSW가 확정 계약을 재현 |
| `src/pages/citizen-participation/ui/CitizenListRoutes.tsx` | 새 훅/DTO 직접 사용 | 사용처가 옛 `ContentListResponseDto`에 의존하지 않음 |
| `src/shared/api/common/api-result/api-result.mapper.ts` | `code === "SUCCESS"` 성공 처리 | 확정 envelope를 기존 `success: true`와 함께 수용 |

## 결정 사항

- 새 목록 DTO를 다시 `ContentListResponseDto`로 되돌리지 않았다.
- 목록 UI `summary`는 응답에 없어 빈 문자열로 매핑했다. `ProposalListPage` 마크업은 바꾸지 않았다.
- MSW proposal fixture id는 `"59"`/`"58"`로 바꿔 숫자 목록 id와 상세 path를 맞췄다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `npx vitest run src/pages/citizen-participation/ui/CitizenDataRoutes.test.tsx src/features/citizen-participation src/pages/citizen-participation/model` | 9 files / 43 tests passed |
| `npm run build` | `tsc -b && vite build` 성공 |
| `npm run lint` | exit 0 |
| `npx vitest run` 전체 | citizen 관련은 통과. 기존 auth/meeting 테스트 3건 실패(이번 변경 경로 밖) |

## Watcher 인계

현재 변경은 proposal list/activity 요청 계약과 목록 사용처 연결이다. UI 시각 QA는 수행하지 않았고, 검증은 테스트·build·lint다.
