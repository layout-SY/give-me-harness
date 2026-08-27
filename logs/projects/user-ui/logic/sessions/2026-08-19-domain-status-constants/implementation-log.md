# 구현 로그

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `model/constants.ts` | 세 uppercase `as const` 집합과 파생 타입 추가 | 도메인 이름별 고정 계약 |
| `api/common/content.dto.ts` | detail 개인 선택 schema가 도메인 상수 재사용 | lowercase 응답 거부 |
| `api/vote/vote.dto.ts` | VoteChoice schema 재사용 | Vote request/response uppercase |
| `api/discussion/discussion.dto.ts` | OpinionStance schema 재사용 | Discussion request/response uppercase |
| `mocks/fixtures.ts` | Proposal fixture uppercase 적용 | parser와 mock 일치 |
| `mocks/handlers.ts` | Vote·Opinion 저장소 분리 | Vote에 `NEUTRAL` 저장 불가 |
| `index.ts` | domain 타입과 UI value 타입 이름 분리 | `VoteChoice` 이름 충돌 제거 |
| `CitizenParticipationDetailRoutes.tsx` | domain↔UI 양방향 map | production UI 수정 없이 제출 유지 |
| `presentation.ts` | uppercase ProposalStatus 표시 변환 | 기존 lowercase UI 표시 계약 유지 |
| 관련 테스트 | uppercase fixture·요청·응답 적용 | 경계 회귀 고정 |

## 검증 근거

| 검증 | 결과 |
| --- | --- |
| focused Vitest | 4 files, 25 tests PASS |
| route Vitest | 1 file, 6 tests PASS |
| `npm run lint` | PASS |
| `npm run build` | PASS, Vite chunk-size warning만 존재 |
| `npm test` | 162 PASS, 범위 밖 3 FAIL |
| 모듈 직접 실행 | 세 상수 객체가 요청한 uppercase JSON으로 출력됨 |
| `lsp_diagnostics` | TypeScript LSP 미설치·설치 거절 상태로 실행 불가 |
| no-excuse script | Bun 미설치, Node의 node_modules type stripping 제한으로 실행 불가 |

## LOC

- `mocks/fixtures.ts`: pure LOC 246, 경고 구간
- `presentation.ts`: pure LOC 236, 경고 구간
- 그 외 변경 파일: pure LOC 214 이하
