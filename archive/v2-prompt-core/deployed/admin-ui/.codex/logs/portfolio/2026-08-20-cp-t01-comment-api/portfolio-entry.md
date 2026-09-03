# 포트폴리오 경험 기록

## 작업 개요
- 구현/수정 내용: Comment 목록·처리를 typed API/query/mutation/stateful MSW 수직 slice로 전환하고 독립 Watcher 검증 및 closure를 완료했다.
- 구현 이유: fixture 기반 화면과 미등록 POST를 실제 API 계약 기반 흐름으로 바꾸고, 응답·cache·UI의 상태 일치를 검증하기 위해서다.
- 작업 유형: CP admin API remediation, Comment tranche.

## 문제 상황
- **출처**: Todo 4 수동 failing-first baseline과 브라우저 QA, Todo 5 독립 Watcher.
- **제품/UX**: 목록은 API GET 없이 4개 page fixture를 렌더했고 KPI는 `1,480/42/9/79/214` literal이었다. 처리 POST는 MSW handler가 없어 500이 발생하고 행/KPI가 갱신되지 않았다.
- **기술**: raw `useApi` 처리와 page fixture가 서버 응답·cache와 분리되어 POST 후 동일 세션 읽기 일관성을 증명할 수 없었다.
- **품질**: 초기 구현의 브라우저 실행에서 두 null selection의 optional-chain 비교가 참이 되어 null의 `state`를 읽는 오류가 발견됐다.

## 요구사항 및 의사결정
| 접근법 | 장점 | 단점 | 채택 여부와 이유 |
|---|---|---|---|
| 기존 page fixture와 raw 호출 유지 | 변경량이 작음 | 응답·KPI·cache 불일치와 미등록 POST를 해소하지 못함 | 미채택 |
| Proposal-like Comment 전용 수직 slice | 기존 검증 패턴 재사용, 도메인 계약과 cache 범위가 명확함 | Comment 파일이 추가됨 | 채택: Todo 4 acceptance와 일치하고 generic 계층 없이 경계를 명확히 함 |
| 여러 CP 도메인을 위한 generic abstraction 선행 | 향후 코드량을 줄일 가능성 | 반복 계약이 확정되지 않아 과잉 추상화와 closed vocabulary 위험 | 미채택: T12 장기 평가 전에는 근거 부족 |

**판단 기준**: API 응답 신뢰 경계, 동일 세션 상태 일관성, Comment 범위의 독립 변경, 검증 가능한 최소 추상화.

## 사용 기술과 구체적 목적
| 기술/패턴 | 해결하려는 문제 | 실제 적용 | 미채택 대안/이유 |
|---|---|---|---|
| TypeScript DTO + Zod | transport `unknown`을 신뢰하는 문제 | GET/POST `ApiResult<unknown>`을 unwrap 후 Comment parser로 한 번 파싱 | unsafe assertion은 경계 검증이 없어 미채택 |
| TanStack Query | 목록/cache/후속 GET 일관성 | 모든 필터를 query key에 포함하고 Comment list cache만 update/invalidate | page-local fixture state는 서버 source와 분리되어 미채택 |
| stateful MSW factory | GET/POST 및 음수 계약 재현 | mutable seed, filter/pagination/count, 400/404, POST 후 GET 일치 | stateless fixture는 mutation 지속성을 검증할 수 없어 미채택 |
| in-flight ref + pending disabled | 빠른 재클릭 중복 처리 | rapid double click에서 실제 POST 정확히 1회 | disabled만 의존하면 같은 event turn 경쟁을 막는 근거가 약함 |

## 적용 내용
### 결과 1: Comment API 수직 slice
- entity에 DTO/parser/query key/list query/process mutation을 두고 page는 parsed query 결과만 렌더한다.
- **도출 이유**: Proposal-like 검증된 경계를 따르되 Comment 전용 계약을 generic abstraction으로 섞지 않기 위해서다.

### 결과 2: 응답 기반 KPI·필터·stateful 처리
- KPI 5개는 `count.totalItemCount/reportedCount/suspiciousCount/hiddenCount/todayCount`에서만 가져오고 모든 필터를 GET에 전달한다.
- handler seed와 필터 결과에서 count를 파생하고 POST 상태를 후속 GET에 반영한다.
- **도출 이유**: page literal과 서버 상태의 이중 source를 제거하고 response/cache/DOM을 같은 사실로 맞추기 위해서다.
- **provisional 경계**: 실제 백엔드의 count 산정 규칙은 확정되지 않았으며 현재 의미와 수치는 MSW 계약 기준이다.

### 결과 3: 브라우저 발견 null selection 수정과 중복 처리 차단
- 두 selection 객체 존재를 먼저 확인한 뒤 ID를 비교해 null `state` 접근을 제거했다.
- in-flight ref와 pending disabled로 repeated click을 차단했다.
- **도출 이유**: 정적 검증만으로 놓친 초기 렌더 오류와 동일 event turn 중복 POST를 실제 브라우저에서 방지하기 위해서다.

### 결과 4: 독립 피드백과 cleanup 재시도
- Watcher attempt 1은 Generator root artifact 12개 때문에, attempt 2는 Watcher attempt-1 root artifact 9개 때문에 `needs-fix`였다.
- 각 소유자가 내용을 보존해 evidence로 이동했고 제품 hash는 변하지 않았다. attempt 3에서 root 대상 artifact 0과 제품 hash 일치를 확인해 `confirmed`를 받았다.
- **도출 이유**: cleanup 범위 실패를 제품 동작 실패와 구분하면서도 dirty worktree fidelity를 완료 조건으로 유지하기 위해서다.

## 결과 및 성과
| 측정 항목 | Before | After |
|---|---|---|
| 목록 source | page fixture 4개, GET 0회 | GET 200 parsed query 렌더, 초기 seed 36개/pagination |
| KPI | literal `1,480/42/9/79/214` | 응답 기반 초기 `36/4/9/16/6`; compound filter `1/0/1/0/1` |
| 처리 | 미등록 POST 500, UI 갱신 없음 | POST 200 1회, HIDDEN cache/후속 GET/DOM 및 `1/0/1/1/1` 일치 |
| 실패 계약 | unhandled 요청 | 400 malformed, 404 unknown, 격리 500 Dialog 및 guard 해제 |
| 파일 크기 | 측정 baseline 없음 | 변경 TS/TSX 15개 전부 pure LOC ≤250, 최대 181 |
| 독립 검토 | 없음 | 두 cleanup `needs-fix` 해소 후 Watcher attempt 3 `confirmed` |

- scoped ESLint, `yarn tsc -b --pretty false`, `yarn build`가 모두 exit 0이었다.
- fresh browser console는 Errors 0, Warnings 0이었다.
- 측정하지 않은 사용자 처리 시간, 장애율, 생산성 개선은 성과로 주장하지 않는다.

## 잔여 리스크
- 실제 backend DTO, pagination, KPI/count semantics는 provisional이며 연동 시 대조가 필요하다.
- build 성공과 별개로 기존 bundle `>500 kB` warning이 남아 있다.
- TypeScript LSP가 미설치이고 이전 설치 거절 상태여서 `lsp_diagnostics`는 unavailable이었다.
- test runner는 계획상 실행하지 않았으며 장기 회귀 자동화 평가는 T12 대상이다.

## 회고
- **잘된 판단**: generic abstraction을 선행하지 않고 Proposal-like 수직 경계만 재사용해 Comment scope와 cache 범위를 분명히 했다.
- **독립 피드백의 가치**: 제품 기능이 통과해도 root QA artifact가 남으면 closure가 불완전하다는 것을 두 차례 `needs-fix`가 드러냈다. 이를 제품 실패로 왜곡하지 않고 ownership별 cleanup으로 해결했다.
- **다시 한다면**: Playwright 산출물 destination을 실행 전에 evidence 경로로 고정해 두 번의 cleanup 재시도를 예방한다.
- **다음 작업**: Vote를 시작하기 전 T01의 evidence 경로 규칙과 repeated-click guard 검증을 재사용하되, 공통 abstraction 여부는 T12의 누적 근거로 판단한다.

## 근거
- [Session final summary](../../sessions/2026-08-20-cp-t01-comment-api/final-summary.md)
- [Generator browser QA](../../../../.omo/evidence/cp-admin-api-remediation/t01/generator/browser-qa.md)
- [Watcher attempt 1](../../../../.omo/evidence/cp-admin-api-remediation/t01/watcher/adversarial-verify.json)
- [Watcher attempt 2](../../../../.omo/evidence/cp-admin-api-remediation/t01/watcher/attempt-2/verdict.json)
- [Watcher attempt 3](../../../../.omo/evidence/cp-admin-api-remediation/t01/watcher/attempt-3/verdict.json)
