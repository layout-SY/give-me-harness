# 구현 기록

## 승인된 범위

제안 상세 GET DTO와 시민참여 API `/citizen` 접두사.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `api/proposal/proposal.dto.ts` | `getProposalDetailResponseSchema`, author nullable | 확정 JSON과 동일 |
| `api/proposal/proposal.api.ts` | `GetProposalDetailResponseDto`, RESOURCE `/citizen/proposals` | 상세 GET 계약 |
| 나머지 `*.api.ts` | RESOURCE `/citizen` | path 접두사 통일 |
| `citizenParticipation.parser.ts` | `parseProposalDetail` | 훅 파싱 |
| `useCitizenParticipationQueries.ts` | `useProposalDetailQuery`, proposal을 공용 상세 훅에서 제외 | 타입 순환 없이 전용 훅 |
| `presentation.ts` | 새 DTO → UI 필드 매핑, author null → `""` | 화면 계약 유지 |
| `CitizenReadDetailRoutes.tsx` | `useProposalDetailQuery` | 상세 화면 연결 |
| MSW handlers/fixtures | `/citizen`, `toProposalDetailResponse` | 201 Location과 GET 상세 일치 |
| 테스트 | path·필드·author null | 예시 JSON 단언 |

## 결정 사항

- `reviewResult`는 응답에 없어 표시용으로 status 라벨만 쓴다
- 목록 author 필수 계약은 바꾸지 않는다

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `npx tsc -b` | 성공 |
| eslint 변경 파일 | 성공 |
| vitest API+pages+feature(샌드박스) | handlers 17건 Invalid URL, 나머지 55 통과 |
| vitest handlers+api+presentation (`all`) | 33 passed |
