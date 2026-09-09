# 구현 로그

## 현재 결과

새 워크트리에서 토론 API 계약·상태·화면 연결·MSW 통과와 회귀 테스트를 구현했다. 최종 전체 테스트는 559개 중 554개 통과·5개 실패다. 남은 5개는 기준 실행부터 실패하던 투표 테스트다. 에이전트의 빌드 실행은 PreToolUse에 차단됐다. 이후 사용자가 직접 실행한 빌드 결과에서 `useCitizenParticipationQueries.ts:129`의 TS2379 한 건을 확인했다. 사용자가 Codex `/resume` 이전 대화 목록 문제를 우선 요청하여 타입 오류 수정과 작업 완료 판정은 대기 상태다.

## 승인된 범위

- branch: `task/citizen-discussion-api-resume`, parent·merge target: `sy-main`.
- 생성 계약: `7279d610ed7aad373703ff54dd9d715798298e6e2bcc8aedf5b4d45061f66d66`.
- 시민참여 api·hook·model·mocks·index.ts·testing.ts와 시민참여 pages, 현재 세션 산출물.
- 기존 워크트리와 그 미커밋 변경은 수정하지 않았다.

## 변경 사항

| 경로 | 변경 | 목적 |
| --- | --- | --- |
| api/discussion | 임시 목록·상세·참여 DTO, Zod parser, ApiResult 매핑 | 외부 응답을 토론 계약으로 검증 |
| api/comment/comment.dto.ts | optional stance | 댓글 의견 선택 정보 보존 |
| hook/useCitizenParticipationQueries.ts | 토론 전용 query | 내 활동·페이지별 캐시와 요청 취소 |
| hook/useCitizenParticipationMutations.ts | completed 조건, 선택 캐시 반영, 토론 댓글 등록 후 관련 무효화 | 미완료 응답 오표시와 목록·상세 수치 불일치 방지 |
| hook/useDiscussionParticipation.ts | 제출 조건·중복 방지·실패 선택 보존 | 토론 상태를 화면 이벤트에서 분리 |
| hook/useCitizenCommentActions.ts | isCommentAllowed 입력 | 화면 비활성과 실제 요청 조건 일치 |
| pages/model/useDiscussionDetailController.ts | 댓글·참여·좋아요·신고·이동 확인 연결 | 기존 UI props/callback 재사용 |
| pages/model/presentation.ts | 전용 DTO 매핑, stance 표시, 누락 집계 비노출 | 진행 중 비공개와 종료 결과 보존 |
| pages/ui/CitizenListRoutes.tsx·CitizenParticipationDetailRoutes.tsx | 토론 전용 query·controller 연결, id별 상세 상태 재생성 | 토론별 상태 격리 |
| mocks/browserHandlers.ts·testing.ts | 토론 전체 HTTP 경로 passthrough를 wildcard 앞에 등록 | 브라우저 토론 요청을 실제 API로 전달 |

## 테스트와 수정 과정

- 신규 회귀 테스트는 API 9개, 참여 hook 9개, 브라우저 MSW 통과 10개, 상세 controller 5개, 집계 누락 표시 1개로 총 34개다.
- 실제 Axios 요청으로 URL·query·body·응답 검증·실패 envelope·취소를 관측했다.
- 로컬 HTTP 서버를 열어 브라우저용 MSW가 토론 GET·POST·DELETE 요청을 가로채지 않고 upstream으로 전달하는지 확인했다. 실제 운영 API를 호출한 검증은 아니다.
- 완료·실패·미완료 응답·서버 선택 복원·중복 제출·로그인·등록 조건·댓글 stance·등록 후 갱신·미저장 이동 확인을 검증했다.
- 구현 중 목록 route의 닫는 중괄호 누락과 테스트 lint 오류를 발견해 수정했다.
- 기존 토론 완료 테스트는 로그인 조건을 준비하고 비동기 대기 방식을 수정했다. 단독 통과 후 전체 실행에서는 선행 투표 실패의 미완료 act와 렌더가 토론 테스트에 영향을 주는 현상을 확인했다.
- 같은 결과 route 테스트 파일의 대기를 제한된 polling으로 바꾸고 실패 시에도 afterEach에서 unmount·query 정리·router dispose를 실행하게 했다. 기존 동작 assertion은 유지했다. 이후 전체 실행에서 토론 완료 테스트도 통과했다.

## 실행 근거

| 명령 | 결과 |
| --- | --- |
| 승인 SHA로 branch_workflow.py create | 새 V3 branch·격리 worktree 생성 성공 |
| npm ci --ignore-scripts | 성공, package·lockfile 수정 없음 |
| 변경 전 npm run test | 70파일, 525개 중 519통과·6실패 |
| 토론 API·hook·MSW·표시 관련 5파일 테스트 | 40개 통과 |
| 토론 결과 route·controller 선택 실행 | 8개 통과, 선택 조건 밖 투표 3개 제외 |
| 최종 npm run test | 74파일 중 71통과·3실패, 559개 중 554통과·5실패 |
| npm run lint | 테스트 정리 변경 후 최종 실행 성공, 오류·경고 없음 |
| git diff --check | 성공 |
| npm run build | 최초 차단 후 사용자 독립 승인 확보, 동일 명령 재요청도 PreToolUse 차단으로 미실행 |
| 사용자가 직접 실행한 npm run build | 사용자 제공 결과: useCitizenParticipationQueries.ts:129, exactOptionalPropertyTypes에 따른 TS2379 한 건 |

## 남은 기존 실패

- citizenParticipation.api.test.ts: 투표 POST 1개. API `/ballots`와 mock `/responses` 불일치.
- mocks/handlers.test.ts: 투표 참여 3개. `/ballots`가 generic mutation handler로 연결되어 필요한 choice를 받지 못함.
- CitizenResultRoutes.test.tsx: 투표 완료 1개. 완료 결과를 받지 못해 기존 assertion 실패. 테스트 종료 정리는 보완됐으며 토론 테스트에 실패를 전파하지 않는다.

## 다음 작업

사용자는 정확한 `npm run build`에 대해 독립된 `명령 실행 승인` 메시지로 승인했다. 중앙 훅 재거부 후 읽기 전용으로 확인한 승인 SHA는 새 워크트리가 아닌 세션 시작 폴더를 기준으로 계산된 값이었다. 바인딩된 런타임에는 Codex Bash hook의 `workdir` 누락과 PostTool에서의 경로 복원 처리가 있다. 다만 이번 재거부의 직접 원인이 경로, 승인 이벤트 전달, 30분 만료 또는 중복 검사 중 무엇인지는 확정하지 않는다. 상세 증거와 후속 담당 경계는 handoff.md에 기록했다.

사용자 제공 빌드 오류는 토론 목록 query key에 전달하는 Zod 추론 객체의 optional undefined와 ContentListQueryDto의 optional 속성 계약 충돌이다. 아직 수정하지 않았다. 우선 요청한 `/resume` 이전 대화 조회 문제의 조사 결과는 handoff.md에 기록했다. 이후 승인된 토론 구현의 타입 오류 수정과 필요한 검증을 이어간다. 아직 Watcher 판정·최종 8종 문서 완료·commit·merge·close를 수행하지 않았다. 기존 투표 실패의 별도 수정이나 병합 여부는 현재 토론 구현 승인과 구분한다.
