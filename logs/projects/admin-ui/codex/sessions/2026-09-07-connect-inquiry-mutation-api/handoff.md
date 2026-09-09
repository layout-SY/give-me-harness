# 인계

## Assignment 이동

- 보내는 host·session·role: codex / 01a07998-7844-7330-b1b2-0534f78b1cde / logic.
- 받는 host·session·제안 role: 미정 / 새 ui 세션.

## 역할 라우팅

- 요청 역할(`requested_roles`): logic 구현 및 UI handoff.
- 확인된 역할(`confirmed_roles`): logic.
- 완료 역할(`completed_roles`): logic.
- 다음 제안 역할(`next_role`): ui.
- 역할 판단 근거: 이번 변경은 API·DTO·parser·hook·MSW이며 실제 화면 구조 및 빈 답변 표시는 UI 책임이다.
- 사용자 확인: 5개 backend API로 기존 기능 수정/누락 기능 구현을 요청했고, 미답변 answerContent는 null이며 no-result 컴포넌트를 표시하도록 확인했다. branch proposal 제시 후 `작업 진행`을 승인했다.

## 목표 및 현재 상태

Logic 구현과 검증을 완료하고 사용자 승인으로 sy-main에 병합했다. 병합 후 build 및 CLOSED 기록도 완료했다. 기존 문의 조회 API를 유지하면서 다음 mutation과 hook을 공개했다. 현재 문의 페이지에서 이 hook을 사용하는 연결은 없으며 UI 작업이 필요하다.

| HTTP 계약 | 공개 hook | mutate/mutateAsync 입력 |
| --- | --- | --- |
| DELETE `/admin/inquiries/{inquiryId}` | `useDeleteInquiryMutation()` | `{ inquiryId }` |
| PATCH `/admin/inquiries/{inquiryId}/status` | `useInquiryStatusMutation()` | `{ inquiryId, payload: { status } }` |
| POST `/admin/inquiries/{inquiryId}/answer` | `useCreateInquiryAnswerMutation()` | `{ inquiryId, payload: { content } }` |
| PUT `/admin/inquiries/{inquiryId}/answer` | `useUpdateInquiryAnswerMutation()` | `{ inquiryId, payload: { content } }` |
| DELETE `/admin/inquiries/{inquiryId}/answer` | `useDeleteInquiryAnswerMutation()` | `{ inquiryId }` |

hook·DTO·`INQUIRY_STATUS`는 `~/entities/inquiries`에서 import한다. inquiryId는 number이며 기존 상세 query hook은 route의 string ID를 받는다. mutation에 전달할 ID는 상세 응답의 정수 id를 우선 사용한다. 각 mutation 입력에 AbortSignal을 선택적으로 전달할 수 있다.

## 완료된 작업

- ApiClient PUT, 5개 실제 endpoint와 JSON body, 인증·응답·오류 경계 연결.
- 답변 요청 DTO: PostInquiryAnswerRequestDto / PutInquiryAnswerRequestDto의 `{ content: string }`.
- 상태 요청 DTO: PatchInquiryStatusRequestDto의 `{ status: InquiryStatus }`.
- 상태 값: `OPEN`, `IN_PROGRESS`, `COMPLETED`. 오래된 `RESOLVED`, `CLOSED`는 제거했다.
- 상세 `answerContent`는 `{ id, comment, createdAt } | null`이며 누락된 필드는 허용하지 않는다.
- 정상 mutation data는 string이다. 상세 객체로 해석하거나 상세 캐시에 저장하지 않는다.
- 상태·답변 변경 후 목록 및 해당 상세 조회 취소·무효화. 활성 화면은 재조회 완료를 기다린다.
- 문의 삭제 후 상세 취소·캐시 제거 및 목록 무효화. 다른 상세는 유지한다.
- MSW factory가 변경 상태를 보존하고 공통 handler 배열에 등록된다. 미답변 mock도 null을 반환한다.

## 대기 중인 작업

UI에서 목록·상세 query hook을 연결하고 상태 선택, 문의 삭제, 답변 입력·등록·수정·삭제 이벤트를 표의 hook으로 연결한다. 답변 변경과 문의 상태 변경은 별도 동작이다.

답변 영역의 표시 계약은 다음과 같다.

1. 최초 조회 중에는 기존 로딩 표시를 사용한다.
2. 조회 성공 후 `detail.answerContent === null`일 때 답변 영역에 기존 `NoResults`를 표시한다. 문의 본문은 유지하며 답변 등록 UI를 제공한다.
3. 답변 객체가 있으면 `answerContent.comment`를 표시하고 수정·삭제 동작을 제공한다. 수정 폼은 이 값을 request의 `content`로 매핑한다.
4. 조회 실패·권한 오류·잘못된 ID를 NoResults로 바꾸지 않는다. 공용 오류 처리와 화면의 오류 상태를 유지한다.

표시 분기의 예시이며 UI 파일을 구현한 것은 아니다.

```tsx
import NoResults from "~/shared/ui/no-results/no-results";

// detailQuery.isSuccess 분기 내부의 답변 영역
detailQuery.data.answerContent === null
  ? <NoResults />
  : /* answerContent.comment를 사용하는 답변 표시 UI */ null
```

NoResults의 기본 문구는 `내역이 없습니다.`다. children을 렌더링하지 않으므로 사용자 문구를 children으로 전달하지 않는다. 현재 컴포넌트의 unused children lint는 기존 문제다.

## 결정 사항 및 제약 조건

- hook의 `isPending`이 true인 동안 같은 문의의 관련 mutation 버튼을 비활성화한다. 같은 문의에 동시 mutation을 허용하는 UI는 별도 조율이 필요하다.
- `.mutate(variables, { onSuccess })` 또는 `.mutateAsync(variables)`의 성공 이후에 폼을 닫고 초기화한다. 실패 시 입력을 유지한다. mutateAsync를 사용하면 rejection을 처리해야 하며 공용 Dialog를 중복 호출하지 않는다.
- mutation은 공용 MutationCache의 오류 reporter를 사용한다. UI는 추가 전송 wrapper나 useApi로 감싸지 않는다.
- 문의 삭제 성공 시 현재 상세를 닫거나 목록으로 이동한다. 삭제된 ID의 상세 query를 다시 마운트하지 않는다. 목록 마지막 행 삭제로 빈 페이지가 되면 UI의 pagination을 조정한다.
- 성공 이후 활성 조회가 갱신되며, 재조회 자체가 실패하면 해당 query의 오류로 처리된다. 서버 mutation 성공과 재조회 실패를 구분한다.
- 답변 길이·공백 규칙, 답변 자동 상태 전이, 실제 서버의 중복 답변 오류 명세는 제공되지 않았다. 전송 계층은 content 문자열의 존재·타입을 검증하고 임의의 문자열 변경이나 상태 전이를 하지 않는다.
- MSW의 409 `INQUIRY_ANSWER_EXISTS`, 404 `INQUIRY_ANSWER_NOT_FOUND`, 오류 문구와 답변 id/time 생성은 테스트용 동작이다. UI 조건을 이 mock 전용 코드나 문구에 고정하지 않는다.
- 실제 서버에서 답변 작성/삭제를 호출하지 않았고 브라우저 시각 QA도 수행하지 않았다.

## 소유권과 Git 계약

- task·branch: `task/connect-inquiry-mutation-api` / CLOSED, sy-main에 병합 완료. 작업 branch는 보존했다.
- 인계 commit: `98fc4624d4ff3f1257585373147fb137dcc54058` (`feat : 문의 변경 API와 답변 계약 연결`). 현재 checkout은 sy-main이며 해당 commit에서 Git 작업 폴더는 clean이다.
- parent HEAD: `1d246f55f25a593e26d68a85b54e49f66874b7c1`.
- worktree: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`.
- 계약 SHA-256: `15a8ddfc98c0efd04037cc24229f76f9cd33b2817ee24209e48f04bebbd41b0d`.
- Git 통합 담당자: codex. 산출물 책임: owner.
- 변경 경로: src/entities/inquiries, src/shared/api/api-client.ts, src/mocks/inquiries.handlers.ts, src/mocks/handlers.ts, tests/inquiries-contract.test.mjs, tests/inquiries-msw.test.mjs, tests/inquiries-mutation.test.mjs, 현재 세션 산출물.
- 역할별 파일 소유권: 현재 계약은 Logic scope만 승인됐다. UI 소스 경로는 포함되지 않는다.
- 충돌 여부: 시작 시 clean, 작업 중 다른 변경은 확인되지 않았다.
- 이 handoff가 UI 파일 수정이나 기존 branch의 역할 확장을 승인하지 않는다. 다음 ui 세션은 사용자와 실제 branch 상태를 확인하고 최신 sy-main을 기준으로 UI scope의 별도 계약을 받는다. CLOSED인 기존 Logic branch에서 UI 작업을 시작하지 않는다.
- 이 문서는 `.gitignore`의 `.codex/` 규칙으로 Git 추적에서 제외된다. 다른 worktree로 인계할 때 이 절대 경로를 읽거나 중앙 로그 사본의 수집 여부를 확인해야 한다.

## 관련 경로와 스킬

`src/entities/inquiries/index.ts`, `api/inquiry.api.ts`, `api/inquiry.dto.ts`, `model/inquiry-mutation-options.ts`, `hook/use-inquiry-mutations.ts`, `src/shared/ui/no-results/no-results.tsx`.

현재 중앙 snapshot의 task-role-routing·git-branch-strategy·UI 관련 스킬·data-fetch-layer·type-definition·api-authoring·documentation을 실제 코드와 함께 읽는다. Logic API를 변경해야 하면 현재 소유권과 scope를 재확인한다.

## 명령어 및 결과

- 승인된 branch_workflow create: 성공.
- `node --test tests/*.test.mjs`: 106개 모두 통과(문의 33개).
- `npm run build`: 통과, Vite 경로 플러그인/청크 크기 안내.
- `npm run lint`: 기존 파일의 71 오류·5 경고로 실패. 오류 경로는 sy-main 대비 변경 없음.
- `./node_modules/.bin/eslint src/entities/inquiries src/shared/api/api-client.ts src/mocks/inquiries.handlers.ts src/mocks/handlers.ts`: 통과.
- `git diff --check`: 통과.
- 승인 범위 소스·테스트 14개를 명시적으로 stage하고 `git commit -m 'feat : 문의 변경 API와 답변 계약 연결'`을 실행하여 `98fc462`에 저장했다. stage diff 검사 및 commit 후 Git 상태 확인은 통과했다.
- 완료 계약 `5dba11e389b14c7034d5f5e6e9e4a380911cd5e0bb511269794be64e4ed8298d`을 사용자 승인받아 finish → verify → close를 각각 실행했다. sy-main ff-only 병합, 병합 후 npm run build, CLOSED 기록 모두 성공했다. branch/worktree 삭제 및 원격 push는 수행하지 않았다.

## 실행하지 않은 검증

실제 backend 요청, 실제 화면·브라우저 테스트, 시각 QA. npm test script는 없어 기존 Node test runner로 실행했다. 병합 후에는 승인 계약대로 build를 재실행했으며 소스가 동일한 106개 테스트와 대상 lint는 재실행하지 않았다.

## 다음 조치

UI 담당자는 최신 sy-main 상태와 이 문서를 읽고 별도 ui role/branch scope에서 화면을 연결한다. Logic 작업은 병합과 종료가 완료됐으며 종료 근거는 `.git/asan-agent-policy/closed/connect-inquiry-mutation-api.json`이다.
