# 구현 로그

## 승인된 범위

제안 생성 POST의 요청 body와 201 Location 성공 계약을 기존 API·폼 매퍼·MSW·작성 라우트 연결에 반영한다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `src/features/citizen-participation/api/proposal/proposal.dto.ts` | 요청 5필드 DTO, Location→`id` 스키마 | 확정 body와 `{ id: number }` |
| `src/features/citizen-participation/api/proposal/proposal.api.ts` | 허용 필드만 복사해 POST | 옛 `body`/`detail`/`effect`가 실리지 않음 |
| `src/features/citizen-participation/api/http/citizenParticipation.parser.ts` | `parseCreateProposalResponse` | Location 데이터를 `{ id }`로 좁힘 |
| `src/features/citizen-participation/model/forms/proposalForm.ts` | UI→API 매핑, 빈 참고는 `null` | 작성 폼이 새 body를 만듦 |
| `src/features/citizen-participation/hook/useCitizenParticipationMutations.ts` | 생성 응답 파서 연결 | mutation `onSuccess`가 `{ id: number }`를 받음 |
| `src/shared/api/unwrap-axios-response.ts` | 201 Location을 SUCCESS `data.location`으로 보존 | interceptor가 헤더를 버려도 id를 복원 |
| `src/shared/api/axios-instance.ts` | 공유 unwrap 사용 | 앱 클라이언트와 테스트가 같은 201 처리를 씀 |
| `src/features/citizen-participation/mocks/handlers.ts` | 201 + Location, 상세는 옛 필드에 저장 | 생략/`null` referenceCase는 상세 `reference` 없음 |
| `src/pages/citizen-participation/ui/CitizenAuxiliaryRoutes.tsx` | `String(id)`로 상세 이동 | 숫자 id가 라우트 문자열과 맞음 |

## 결정 사항

- 201 JSON `{ id }`를 만들지 않았다. Location이 성공 계약의 출처다.
- 클라이언트가 빈 참고 사례를 `referenceCase: null`로 보낸다. 서버 “생략하면 null 저장”과 같은 저장 값이다.
- GET 상세 DTO는 바꾸지 않고 MSW만 `background`→`body`, `content`→`detail`, `expectedEffect`→`effect`로 넣는다.
- `ProposalWritePage` 필드명은 유지한다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `npx vitest run src/features/citizen-participation src/pages/citizen-participation` | 12 files / 71 tests passed |
| `npm run lint` | exit 0 |
| `npm run build` | `tsc -b && vite build` 성공 |

## Watcher 인계

현재 변경은 생성 POST 계약과 작성 라우트의 id 연결이다. `ProposalWritePage` 마크업은 바꾸지 않았다. UI 시각 QA는 수행하지 않았고, 검증은 테스트·lint·build다. Watcher(`[Watcher](6141f965-7963-4ba5-b843-4a1a17eb22eb)`) 판정은 PASS다.
