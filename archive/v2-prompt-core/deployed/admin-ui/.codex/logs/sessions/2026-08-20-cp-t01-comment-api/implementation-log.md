# 구현 로그

## 작업 요약
- Comment 목록/처리를 source → API → parse → query/mutation → render 흐름으로 전환했고, stateful MSW와 동일 세션 후속 GET으로 읽기/쓰기 일관성을 확보했다.
- 본 Todo 6 closure에서는 제품 코드를 수정하지 않았으며 아래는 완료된 Todo 4의 사실 기록이다.

## 재사용 자산
- shared `ApiClient`, `unwrapApiResult`, `withAbortSignal`, TanStack Query와 Proposal-like 수직 slice 패턴을 재사용했다.
- 신규 shared 자산은 추가하지 않았다.

## 신규 파일 / 수정 파일
- Comment entity API/DTO/parser/query/mutation/types/fixture/index, Comment page/config/page-local hook, Comment MSW handler와 통합 handler 등록점까지 제품 파일 15개가 Todo 4 범위였다.
- 정확한 경로 목록은 [Generator 계약 및 파일](../../../../.omo/evidence/cp-admin-api-remediation/t01/generator/contracts-and-files.md)에 고정되어 있다.

## 핵심 로직
1. **Typed contract와 parse 경계**
   - GET/POST DTO와 Zod schema를 정의했다.
   - API는 GET/POST 모두 `ApiResult<unknown>`을 반환하고, query/mutation에서 `unwrapApiResult` 후 `parseCpCommentList`/`parseCpComment`를 수행한다.
   - GET에는 `AbortSignal`을 전달한다.
2. **목록 조회와 화면 상태**
   - query key에 page/size/tab/sourceType/author/sourceTitle/commentId를 모두 포함했다.
   - page fixture import와 하드코딩 KPI를 제거했다.
   - 응답의 목록·pagination·count를 렌더하고, 탭/유형/작성자/원문 제목/댓글 ID 필터를 GET query에 매핑했다.
3. **처리 mutation과 캐시**
   - 선택 ID와 처리 상태를 page-local stateful hook에서 관리한다.
   - rapid double click은 in-flight ref와 pending disabled로 차단되어 실제 POST가 정확히 1회 발생했다.
   - 성공 응답으로 Comment list cache를 갱신하고 Comment list만 invalidate/refetch한다.
   - 동일 복합 query의 후속 GET과 DOM이 `NORMAL → HIDDEN`, hidden count `0 → 1`로 일치했다.
4. **Stateful MSW**
   - handler factory마다 fixture clone 기반 Comment-local mutable store를 생성한다.
   - GET validation/filter/pagination/응답 기반 KPI 5개, POST body validation/state update를 제공한다.
   - malformed state 400, unknown ID 404를 제공하며, 격리 route로 500 실패 Dialog와 in-flight 해제를 확인했다.

## 실제 before / after
| 항목 | Before | After |
|---|---|---|
| 목록 | page가 4개 fixture 행 직접 렌더, GET 없음 | GET `/v1/cp/comments` 200 응답을 Zod parse 후 query로 렌더 |
| KPI | `1,480/42/9/79/214` literal | 초기 응답 `36/4/9/16/6`, 필터 응답 count를 그대로 렌더 |
| 처리 | POST handler 없음, 500 Request Handler Error, UI 갱신 없음 | stateful POST 200, exactly-one, cache 갱신·후속 GET·DOM 일치 |
| 실패 | unhandled POST | 400/404 계약 및 격리 500 실패 Dialog |

## 구현 중 수정한 결함
- TypeScript 최초 실행에서 filter item `value`가 `string`으로 widening된 오류를 `CommentSourceFilterValue` 명시로 수정했다.
- 실제 브라우저에서 null selection의 `state` 접근 오류를 발견해 존재 여부를 먼저 좁히도록 수정했다.

## 검증 / 요청 처리
- 변경 TS/TSX 15개 pure LOC 범위: 4~181, 모두 250 이하.
- 최종 scoped ESLint: exit 0.
- `yarn tsc -b --pretty false`: exit 0.
- `yarn build`: exit 0; 기존 `vite-tsconfig-paths` 안내와 bundle `>500 kB` warning 유지.
- LSP: TypeScript LSP 미설치·기존 사용자 거절 상태로 `lsp_diagnostics` unavailable.
- test runner: 승인된 전략에 따라 실행하지 않았고 deterministic stateful MSW와 fresh browser 검증을 사용했다.

## 리스크
- backend DTO와 KPI/count semantics는 provisional이고 기존 bundle warning과 LSP unavailable 상태가 남는다.

## Artifact cleanup
- Generator attempt 1이 workspace root에 남긴 QA 산출물 12개를 내용·hash 보존 상태로 `generator/browser-artifacts/`에 이동했다.
- 제품 파일 hash 15개는 cleanup 전후 동일했고 cleanup 중 제품 수정·QA 재실행은 없었다.

## 핸드오프 메모
- Todo 5 Watcher attempt 3 `confirmed` 완료. Todo 6 문서 closure 이후에만 다음 tranche를 시작할 수 있다.

## 근거
- [Generator quality gates](../../../../.omo/evidence/cp-admin-api-remediation/t01/generator/quality-gates.md)
- [Generator browser QA](../../../../.omo/evidence/cp-admin-api-remediation/t01/generator/browser-qa.md)
- [Generator cleanup receipt](../../../../.omo/evidence/cp-admin-api-remediation/t01/generator/attempt-2/cleanup-receipt.json)
- [Generator product hashes](../../../../.omo/evidence/cp-admin-api-remediation/t01/generator/attempt-2/product-hashes.json)
