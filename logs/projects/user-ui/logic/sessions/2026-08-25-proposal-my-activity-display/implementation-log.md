# 구현 로그

## 승인된 범위

「내 활동 보기」토글 → `GET /me/activity?content=proposal&page=&size=` → 확정 목록 응답 파싱 → 제안 카드 표출.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `useCitizenParticipationQueries.ts` | `useMyProposalActivityQuery` 추가 | activity 본문을 `parseProposalList`로 좁힘 |
| `me.api.ts` | `page`/`size`/`content`만 params로 복사 | 미확정 필드가 activity URL에 안 실림 |
| `handlers.ts` | `content=proposal`이면 SUCCESS + 목록 DTO | 토글 경로가 실서버와 같은 본문을 받음 |
| `CitizenListRoutes.tsx` | 토글 on에서 전용 훅 + `toProposalListItem` | 제목/작성자/상태를 카드에 표시 |
| `CitizenAuxiliaryRoutes.tsx` | 제안 필터도 같은 DTO 매핑 | 내 활동 화면 제안 필터가 깨지지 않음 |
| `CitizenDataRoutes.test.tsx` | `?myActivity=true` 표출 테스트 | activity query key와 제목이 보이는지 확인 |

## 결정 사항

activity 응답 스펙이 없어 확정된 proposal list `data` 형태를 그대로 썼다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `npx vitest run src/pages/citizen-participation src/features/citizen-participation` | 12 files / 56 tests passed |
| `npm run build` | 성공 |
| `npm run lint` | 성공 |

## Watcher 인계

토글 표출은 라우트 테스트로 확인했다. 브라우저 시각 QA는 하지 않았다.
