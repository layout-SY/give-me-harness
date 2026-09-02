# 구현 로그

## 승인된 범위

- 종료 후 결과 공개와 진행 중 비공개
- 종료 mock 데이터 추가
- Vote·Discussion 제출 후 사용자 완료 상태 표시

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `api/common/content.dto.ts` | `myVoteChoice`, `myDiscussionChoice` 추가 | 상세 재조회 후 개인 선택 유지 |
| `api/vote/vote.dto.ts` | request/response Zod 계약 | `{ id, completed, choice }` 파싱 |
| `api/discussion/discussion.dto.ts` | 찬성·반대·중립 request/response 계약 | 선택값을 실제 POST body에 전달 |
| `hook/useCitizenParticipationMutations.ts` | domain response 파싱과 detail invalidate | typed mutation 결과 제공 |
| `mocks/handlers.ts` | participation choice 상태 저장 | POST 후 GET 일관성 유지 |
| `mocks/fixtures.ts` | `vote-2`, `discussion-2` 종료 항목 | 31/69, 30/45/25 화면 데이터 |
| `model/presentation.ts` | closed 전용 ratio 매핑 | 진행 중 결과 비공개 |
| `model/resultRatios.ts` | Vote 기존 계산 재사용·Discussion 3-way 계산 | item별 ratio 생성 |
| `CitizenParticipationDetailRoutes.tsx` | selected choice·`hasSubmitted` 연결 | 제출 후 완료 상태 표시 |

## 결정 사항

- 전체 집계 count 계약은 변경하지 않았다.
- 개인 제출 상태만 domain별 응답과 상세 필드로 추가했다.
- UI 완료 상태 이름은 전체 종료와 혼동하지 않도록 `hasSubmitted`를 사용했다.
- project 규칙에 따라 production UI는 Claude Code 결과를 읽어 연결만 수행했다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| focused Vitest 6 files | 31 tests PASS |
| result/API focused Vitest 3 files | 20 tests PASS |
| `npm run lint` | PASS |
| `npm test` | 161 PASS, 범위 밖 3 FAIL |
| `npm run build` | 범위 밖 `text-input.tsx:27` 오류로 BLOCKED |
| pure LOC | 변경 파일 모두 250 이하; `fixtures.ts` 246 |
| `lsp_diagnostics` | TypeScript LSP 미설치·설치 거절 상태로 실행 불가 |

## Watcher 인계

- 자동 Watcher/Evaluator는 세션의 Anthropic 크레딧 부족으로 사용할 수 없어 역할 계약과 체크리스트를 직접 적용했다.
