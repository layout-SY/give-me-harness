# 탐색 기록

## 결론
- Comment는 기존 Proposal 계열의 경계 패턴을 따라 도메인 전용 수직 slice로 구성하는 것이 적합했고, 새 generic abstraction은 필요하지 않았다.
- 기존 page fixture·하드코딩 KPI·raw `useApi` 경로는 재사용 대상이 아니라 제거 대상이었다.

## 대상 경로
- `src/entities/cp-comment`: API, DTO/Zod parser, query key, list query, process mutation, fixture/types.
- `src/pages/cp-comment/ui`: 목록 렌더, 필터/선택/처리 상태를 보유하는 page-local hook과 config.
- `src/mocks`: Comment-local stateful handler와 기존 통합 handler 등록점.
- 선행 Proposal API/query/mutation/parser 패턴과 shared `ApiClient`, `unwrapApiResult`, `withAbortSignal`.

## 발견한 기존 재사용 자산
- `ApiClient<unknown>` + `unwrapApiResult` + Zod parser 경계: transport 응답을 신뢰하지 않고 Comment schema로 한 번 파싱.
- TanStack Query query/mutation 및 Comment 전용 query key: 목록 캐시 범위를 명시.
- `withAbortSignal`: GET 취소 신호 전달.
- Proposal과 유사한 entity → API/parse → query/mutation → page render 수직 구조.

## 재사용이 어려운 자산
- `CP_COMMENT_LIST_FIXTURE`의 page 직접 import: 서버 응답과 화면 상태가 분리되어 제거.
- page literal KPI `1,480/42/9/79/214`: 응답과 불일치할 수 있어 제거.
- generic Comment/Vote 공통 abstraction: 아직 반복 계약과 변화 축이 입증되지 않아 만들지 않음.

## 신규 자산 필요성
- Comment 전용 DTO/parser/query/mutation/stateful handler는 필요했으나 shared 신규 자산은 필요하지 않았다.
- 신규 generic abstraction은 반복 계약이 확정되지 않아 보류했다.

## provisional contract와 KPI/count 규칙
- GET query: `page`, `size`, `tab`, `sourceType`, `author`, `sourceTitle`, `commentId`.
- POST payload: `{ state: 'NORMAL' | 'HIDDEN' | 'REPORT_REJECTED' }`.
- KPI 5개는 응답 `count.totalItemCount/reportedCount/suspiciousCount/hiddenCount/todayCount`만 렌더한다.
- 현재 stateful MSW는 mutable seed에 GET 필터를 적용한 결과에서 count를 산출하고, POST 상태 변경을 후속 GET에 반영한다. 실제 백엔드의 신고·가입정보 의심·오늘 신규 산정 기준은 미확정이므로 이 규칙은 provisional이다.

## 브라우저 탐색에서 발견한 결함
- `processSelection`과 `selectedRow`가 모두 null일 때 optional chain 비교가 `undefined === undefined`가 되어 null의 `state`를 읽는 런타임 오류가 발생했다.
- 두 객체의 존재를 먼저 좁힌 뒤 ID를 비교하도록 수정했고 fresh browser에서 재현되지 않았다.

## 공용 자산 판단
- 신규 shared component/hook/util을 추가하지 않았다.
- 따라서 `.codex/memory/reusable-assets.md` 갱신은 N/A이다.

## 근거
- [Generator baseline](../../../../.omo/evidence/cp-admin-api-remediation/t01/generator/baseline.md)
- [Generator browser QA](../../../../.omo/evidence/cp-admin-api-remediation/t01/generator/browser-qa.md)
- [Generator 계약 및 파일](../../../../.omo/evidence/cp-admin-api-remediation/t01/generator/contracts-and-files.md)
