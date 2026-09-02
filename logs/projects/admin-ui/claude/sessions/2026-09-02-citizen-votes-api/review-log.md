# 검토 로그

## Watcher 판정

FAIL

현재 시민투표 목록·상세 조회 구현 자체는 승인된 실제 GET 계약과 일치하지만, 제거된 legacy mutation schema를 기존 회귀 테스트가 계속 호출하여 저장소 테스트가 실패한다. 이 회귀가 해소되기 전에는 현재 작업을 완료로 승인할 수 없다.

## 검토 기준과 범위

- 현재 브랜치: `task/connect-citizen-votes-api`
- 분기 기준·직접 merge 대상: `sy-main`
- 승인 시점 부모 HEAD 및 현재 merge-base: `e26b263afe2478cbabd3e34fdc82306e0715d059`
- 승인 근거: `plan.md:54-59`의 구현·브랜치 승인 기록
- 승인 범위: `src/entities/cp-vote`, `src/pages/cp-vote`, `src/mocks/cp-vote.handlers.ts`, `tests/citizen-votes-contract.test.mjs`, `tests/citizen-votes-msw.test.mjs`, `.codex/logs/sessions/2026-09-02-citizen-votes-api`
- 확인 자료: 현재 `git diff`, 변경된 시민투표 소스와 삭제 파일 diff 전체, 신규 query-state 파일, 두 테스트, `handoff.md`, `plan.md`, `exploration.md`
- 적용 스킬: `policy-git-branch-strategy`, `policy-review-checklist`, `policy-documentation`, `git-master`

## 발견 사항

| 심각도 | 경로 | 발견 사항 | 필수 조치 |
| --- | --- | --- | --- |
| 높음 | `tests/cp-date-input-boundaries.test.mjs:17-29`, `tests/cp-date-input-boundaries.test.mjs:37-67`, `src/entities/cp-vote/api/cp-vote.dto.ts:48-60` | 현재 변경은 명세가 없는 `updateCpVoteProcessSchema`를 올바르게 제거했지만, 기존 날짜 경계 테스트가 이 export를 계속 배열에 등록하고 `safeParse`를 호출한다. `node --test tests/cp-date-input-boundaries.test.mjs`를 독립 실행한 결과 2/2가 `Cannot read properties of undefined (reading 'safeParse')`로 실패했다. 승인된 조회-only 전환이 저장소 회귀 테스트와 불일치하는 현재 작업 차단 사항이다. | unsupported mutation schema를 복원하지 말고, 별도 범위 승인을 받아 `tests/cp-date-input-boundaries.test.mjs`에서 시민투표 legacy mutation 날짜 검증을 제거하거나 실제 조회 계약 검증으로 교체한다. 이후 해당 테스트와 시민투표 대상 테스트를 다시 실행한다. |

## 점검 근거

| 점검 | 결과 | 파일 수준 근거 |
| --- | --- | --- |
| 승인·범위 | 충족 | Git branch config의 parent·merge target은 `sy-main`, parent HEAD와 merge-base는 승인값과 일치했다. 현재 변경은 승인된 시민투표 경로와 세션 산출물 경로 안에 있다. |
| 정확한 API URL·read-only 범위 | 충족 | `src/entities/cp-vote/api/cp-vote.api.ts:8-25`는 `GET /citizen/votes`, `GET /citizen/votes/{voteId}`만 제공한다. legacy process API·mutation hook·process/search controller와 UI 저장 표면은 diff에서 삭제됐고, 대상 현재 소스에서 `/v1/cp/votes`, write method 및 처리 저장 참조가 검색되지 않았다. |
| query·정렬·취소 | 충족 | `src/entities/cp-vote/api/cp-vote.dto.ts:6-16,48-54`는 허용 정렬 필드와 기본 page 1/size 20/sort를 고정하고 size를 100으로 제한한다. `src/entities/cp-vote/api/cp-vote.api.ts:21-25`의 `paramsSerializer.indexes: null`이 배열 sort를 반복 query parameter로 직렬화하며 signal을 `withAbortSignal`에 전달한다. 목록·상세 query hook도 TanStack Query의 `signal`을 client까지 전달한다. |
| Zod·타입·ID·pagination | 충족 | `src/entities/cp-vote/api/cp-vote.dto.ts:18-46`이 실제 5개 상태와 목록·상세 필드를 파싱하고 집계 합계를 검증한다. `src/entities/cp-vote/api/cp-vote.parser.ts:5-17`은 `pageCount = max(1, ceil(total/size))`를 계산한다. `src/entities/cp-vote/hook/use-cp-vote-detail-query.ts:10-18`과 `src/entities/cp-vote/model/query-keys.ts:3-9`는 양의 정수 ID 또는 `null` key를 사용한다. 변경 범위 검색에서 `any`, 타입 억제, non-null assertion을 찾지 못했다. |
| 데이터 요청 계층·오류 계약 | 충족 | API가 HTTP 세부 사항, parser가 외부 응답 검증, query hook이 서버 상태·취소, controller/UI가 오류 Dialog·retry·navigation을 담당한다. `src/mocks/cp-vote.handlers.ts:73-126`은 정상 목록·상세와 400/401/404 envelope를 HTTP status/body로 반환한다. |
| query key·화면 상태 | 충족 | `src/entities/cp-vote/model/query-keys.ts:3-9`의 목록 key는 전체 params, 상세 key는 정규화 ID를 포함한다. `src/pages/cp-vote/hook/use-cp-vote-list-data.tsx:25-53`은 placeholder 여부로 이전 페이지와 현재 페이지를 구분하며 초기 오류에는 retry를 제공한다. `src/pages/cp-vote/hook/use-cp-vote-list-controller.tsx:8-45`는 page 변경 시 선택을 초기화하고 숫자 ID로 상세 경로를 연다. 상세 controller는 오류 Dialog, 재조회, 목록 이동을 유지한다. |
| 실제 필드·scope drift | 충족 | `src/entities/cp-vote/model/types.ts:28-43`과 두 UI는 계약에 명시된 목록·상세 필드만 소비한다. 작성자·댓글·이력·공개 정책 등 placeholder backend 필드와 지원하지 않는 검색·상태 변경 표면은 제거됐다. 상태는 `DRAFT`, `UPCOMING`, `IN_PROGRESS`, `CLOSED`, `CANCELLED`만 정의한다. |
| 공용 UI 재사용 | 충족 | `src/pages/cp-vote/ui/cp-vote-list-view.tsx:3-9,23-82`, `src/pages/cp-vote/ui/cp-vote-detail-view.tsx:3-9,41-60`은 기존 `Table`, `Loading`, `Button`, `DefinitionList`, `SectionCard`, `RatioBar`, `ActionBar`를 재사용하며 `src/shared/ui`를 변경하지 않았다. |
| UI·접근성 정적 검토 | 충족 | 신규 자체 interactive primitive는 없고 기존 `Button`·`Table` 계약을 유지한다. loading, disabled/loading retry, row 선택, 상세 열기, 목록 이동이 연결돼 있다. 승인 제약에 따라 브라우저·스크린샷·시각 QA는 수행하지 않았으므로 런타임 포커스·반응형·시각 상태는 잔여 한계로 분리한다. |
| MSW 테스트 teardown·관찰성 | 충족 | `tests/citizen-votes-msw.test.mjs:22-25`는 `await server.close()` 후 `mockServer?.close()` 순서로 Vite를 먼저 닫는다. 같은 파일 `27-113`은 실제 `fetch` 결과의 HTTP status와 envelope code/body/pagination/detail/error를 단언한다. |
| 정적 검증 | 부분 충족 | build와 변경 파일 ESLint, `git diff --check`는 성공했다. 전체 lint의 73 errors/5 warnings는 모두 시민투표 변경 밖의 기존 경로에서 발생했다. 다만 위 발견 사항의 기존 회귀 테스트 실패는 현재 작업 차단 사항이다. |

## 직접 실행한 명령과 결과

- `GIT_MASTER=1 git status --short --branch && GIT_MASTER=1 git branch --show-current && GIT_MASTER=1 git rev-parse sy-main && GIT_MASTER=1 git merge-base HEAD sy-main && ...branch config 조회`: 브랜치·parent·merge target·승인 HEAD·scope가 제시된 계약과 일치했다.
- `GIT_MASTER=1 git diff --name-status && GIT_MASTER=1 git diff --stat && GIT_MASTER=1 git diff -- <승인 범위>`: tracked 변경 22개(수정 17, 삭제 5)와 diff를 확인했다. 신규 query-state 및 테스트 2개는 status와 현재 파일을 별도로 확인했다.
- `npm run build`: 성공. `tsc -b`와 Vite build 완료; 기존 대형 chunk 경고만 출력됐다.
- `npm exec eslint -- src/entities/cp-vote/... src/mocks/cp-vote.handlers.ts src/pages/cp-vote/... tests/citizen-votes-contract.test.mjs tests/citizen-votes-msw.test.mjs`: 변경된 비삭제 TypeScript/TSX/MJS 20개 모두 성공, 출력 없음.
- `node --test tests/citizen-votes-contract.test.mjs tests/citizen-votes-msw.test.mjs`: 14/14 성공.
- `GIT_MASTER=1 git diff --check`: 성공, 출력 없음.
- `npm run lint`: 실패, 78 problems(73 errors, 5 warnings). 출력 경로는 모두 현재 citizen-vote 변경 범위 밖이며 대상 ESLint 성공과 분리했다.
- `node --test tests/cp-date-input-boundaries.test.mjs`: 실패, 2/2 실패. 두 실패 모두 제거된 `updateCpVoteProcessSchema`에 대한 `safeParse` 호출에서 발생했다.
- LSP 상태 조회: TypeScript 및 ESLint LSP가 설치되지 않았고 active client가 없어 LSP diagnostics는 수행하지 않았다.

## 잔여 한계와 비차단 위험

- 사용자 제약에 따라 브라우저, Playwright, 스크린샷, 시각 QA, Lighthouse, 실제 인증 backend 호출을 수행하지 않았다. 따라서 실제 인증 환경의 wire 호환성과 화면의 시각·키보드 동작은 이번 판정에서 직접 검증하지 못했다.
- 반복 sort의 실제 네트워크 직렬화는 Axios의 저장소 기존 방식인 `paramsSerializer.indexes: null` 설정과 MSW의 반복 parameter 수신 테스트로 확인했으며, 실제 backend에는 호출하지 않았다.
- 상세 비율은 두 count를 각각 반올림하므로 표시 합이 드물게 100이 아닐 수 있다. 원 count도 함께 표시되고 계약 정확성을 훼손하지 않아 비차단으로 판단했다.
- build의 대형 chunk 경고와 전체 lint 오류는 현재 diff 밖의 기준선 문제이며 이번 작업의 차단 사항으로 분류하지 않았다.

## 결론

실제 GET 목록·상세 구현, 타입 경계, read-only UI, MSW 계약은 승인 목표에 부합한다. 그러나 legacy mutation 제거에 맞춰 기존 회귀 테스트를 정리하지 않아 저장소 테스트가 재현 가능하게 실패한다. 위 한 건을 최소 수정하고 동일 검증을 다시 수행한 뒤 새로운 Watcher 판정이 필요하다.
