# 구현 로그

## 승인된 범위

`/citizen/votes/{voteId}/comments` 요청·응답 DTO와 관련 API, parser, query, cache, mock, test, feature export를 수정했다. production UI는 수정하지 않았다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `api/vote/vote.dto.ts` | sort vocabulary, query·item·response schema/type 추가 | 허용 정렬과 원본 응답을 런타임 검증 |
| `api/vote/vote.api.ts` | `getVoteCommentList`와 기본 query 직렬화 추가 | page 1, size 20, `createdAt,desc` 기본 전송 |
| `api/comment/comment.dto.ts` | 좋아요 필드를 선택형으로 변경 | vote 댓글의 필드 부재 표현 |
| `api/comment/comment.api.ts` | 일반 댓글 GET에서 votes 컬렉션 제외 | 잘못된 transport 계약 사용을 타입으로 차단 |
| `api/http/citizenParticipation.parser.ts` | `parseVoteCommentList` 추가 | numeric ID와 pagination을 기존 화면 모델로 변환 |
| `model/queryKeys.ts` | page·size·sort를 댓글 key에 포함 | 조건별 캐시 분리 |
| `hook/useCitizenParticipationQueries.ts` | vote 전용 client·parser 분기 | 기존 hook 호출부 유지 |
| `hook/useCitizenParticipationMutations.ts` | 좋아요 capability가 있는 댓글만 cache 갱신 | undefined 산술과 vote cache 오염 방지 |
| `mocks/commentHandlers.ts` | vote 전용 store, 정렬, page, draft 404, 작성·신고 처리 | backend 계약과 동일한 mock 표면 |
| `mocks/voteCommentFixtures.ts` | DTO schema 기반 fixture 추가 | mock 계약 이탈 방지 |
| `presentation.ts` | 선택형 좋아요 속성 조건부 매핑 | `exactOptionalPropertyTypes` 준수 |
| 신규·기존 테스트 | API, parser, mock, query key 기대값 갱신 | 신규 경계와 기존 댓글 회귀 고정 |
| `index.ts` | parser, constants, DTO types export | feature 공개 계약 완성 |

## 결정 사항

- 서버 응답을 공용 DTO로 위장하지 않고 vote 전용 DTO로 먼저 파싱한다.
- UI가 사용하는 ID는 기존 계약 보존을 위해 문자열로 정규화한다.
- 좋아요를 지원하지 않는 vote 댓글은 `likeCount/liked`를 생성하지 않는다.
- mock에서 vote 댓글 작성 후 같은 조회 endpoint에 반영되도록 별도 store를 사용한다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| 신규 테스트의 최초 실행 | `getVoteCommentList is not a function`으로 의도한 RED 확인 |
| 대상 `npx vitest run ...` | 5 files, 36 tests PASS |
| `npm run build` | PASS, 기존 bundle size warning만 존재 |
| `npm run lint` | PASS |
| `npm test` | 216 PASS, meeting API의 기존 실패 2건으로 전체 exit 실패 |
| `lsp_diagnostics` | TypeScript LSP 미설치로 실행 불가 |
| no-excuse script | `bun` 미설치 및 Node node_modules type stripping 제한으로 실행 불가 |

## Watcher 인계

- 판정: PASS
- 차단 발견: 없음
- 비차단 권고: 정렬 결과·잘못된 Zod 응답·hook dispatch 직접 테스트 확대

## 추가 구현 — nullable 제안 작성자

### 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `api/proposal/proposal.dto.ts` | 목록 `author` schema와 DTO를 nullable로 변경 | 실제 backend 응답을 전체 손실 없이 파싱 |
| `model/citizenParticipation.test.ts` | non-null 기존 assertion과 mixed nullable 응답 회귀 추가 | 실제 장애 shape를 parser 경계에 고정 |
| `pages/.../model/presentation.ts` | `item.author?.nickname ?? ""` 적용 | 지원 상태 항목의 null 접근 예외 제거 |
| `pages/.../model/presentation.test.ts` | `RECEIVED + author:null` 매핑 회귀 추가 | 빈 작성자 문자열 fallback 고정 |

### RED → GREEN 근거

- parser RED: `items[1].author`, `Invalid input: expected object, received null`.
- schema GREEN: `citizenParticipation.test.ts` 11 tests PASS.
- presentation RED: `Cannot read properties of null (reading 'nickname')`.
- 최종 GREEN: 대상 2 files, 18 tests PASS.

### 검증 근거

| 검증 | 결과 |
| --- | --- |
| 대상 Vitest | 2 files, 18 tests PASS |
| `npm run build` | PASS, 기존 bundle size warning만 존재 |
| `npm run lint` | PASS |
| `npm run test` | 211 PASS, 기존 meeting API 2건 FAIL |
| 직접 module driver | backend 형태 4건 parse, UI 지원 상태 3건 매핑 |
| `git diff --check` | PASS |
| `lsp_diagnostics` | linked worktree가 도구 cwd 밖이라 실행 불가, `tsc -b`로 대체 |
| no-excuse script | 프로젝트 TypeScript 6.0.3에 없는 TypeScript 7 `unstable/*` API 요구로 실행 불가 |
