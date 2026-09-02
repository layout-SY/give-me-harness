# 평가 로그

## 결론과 현재 판정의 경계

- 정본 Watcher 판정은 `.codex/logs/sessions/2026-09-02-citizen-votes-api/review-log.md`의 승인 pathspec 대상 **PASS**이며, 이 평가는 이를 재심사하거나 약화하지 않는다.
- 아래 항목은 모두 후속 작업을 위한 장기 아키텍처·프로세스 권고다. **현재 작업의 merge·commit을 차단하는 요구사항은 없다.**
- 브라우저·스크린샷·시각 QA와 실제 backend 호출은 사용자 지시로 금지됐으므로 평가 범위에 포함하지 않았다.
- `yarn.lock`은 미소유·승인 범위 밖 동시 변경이므로 열람·수용·수정·평가하지 않았다.

## 우선순위별 장기 개선 사항

### P1. 표준 테스트 진입점 마련

**관찰한 사실**

- `package.json:6-10`에는 `dev`, `build`, `lint`, `preview`만 있고 `test` script가 없다.
- 현재 검증은 `node --test tests/cp-date-input-boundaries.test.mjs tests/citizen-votes-contract.test.mjs tests/citizen-votes-msw.test.mjs`를 직접 실행해 16/16 성공했으며, 정본 Watcher 기록에는 최종 성공과 그 전 20회 연속 안정 실행이 남아 있다.
- 프로젝트 운영 명령은 `npm run test`를 표준 테스트 명령으로 규정한다.

**권고 사항**

- 별도 승인 작업에서 Node test 대상과 loader 사용 방식을 포함한 `npm run test`를 정의하고 CI·로컬 검증이 같은 명령을 사용하게 한다.
- 전체 suite와 citizen-votes 대상 suite를 분리할 필요가 생기면 명명 규칙을 먼저 정하고 script를 추가한다.

**기대 이점**

- 검증 명령 누락과 실행자별 대상 파일 차이를 줄이고, Node 22에서 확인한 안정 경로를 반복 가능한 프로젝트 계약으로 만든다.

**현재 비차단 사유**

- 이번 승인 pathspec은 직접 명령으로 16/16 성공, 반복 안정 실행, build, 대상 ESLint, `npm ci --dry-run --ignore-scripts`, diff-check까지 이미 검증됐다. 표준 script 부재는 재현성 개선 과제이지 현재 동작 결함이 아니다.

### P2. `tsx` 기반 Node 계약 테스트 패턴을 재사용 후보로 등록

**관찰한 사실**

- `tests/citizen-votes-contract.test.mjs:4,10-15`와 `tests/citizen-votes-msw.test.mjs:5,9-17`은 `tsx/esm/api`의 `tsImport`로 TypeScript 모듈을 불러오며, MSW test는 자신이 연 server만 종료한다.
- 이 방식은 Vite server loader를 사용하지 않고 Node `v22.20.0`에서 native teardown crash 없이 최종 실행과 20회 연속 실행을 통과했다.
- 현재 `tsImport` 초기화 패턴은 두 파일에만 존재한다.

**권고 사항**

- `.codex/memory/reusable-assets.md`의 후속 갱신 시 이 패턴을 “Node 내 TypeScript 계약·MSW 테스트” 후보로 등록한다.
- 세 번째 소비 사례가 생기기 전에는 helper를 성급히 추출하지 않고, 반복되는 import/bootstrap/cleanup 계약이 확인된 뒤 최소 helper 또는 recipe로 승격한다.

**기대 이점**

- Vite 개발 server 수명주기와 무관한 빠른 계약 검증 경로를 재사용하면서, 이른 공용 추상화로 인한 불필요한 결합을 피한다.

**현재 비차단 사유**

- 두 테스트 파일의 현재 setup/teardown은 안정 실행으로 검증됐다. 재사용 자산 등록과 추출 시점은 향후 소비 사례를 위한 유지보수 개선이다.

### P2. 조회 orchestration의 비브라우저 회귀 테스트 보강

**관찰한 사실**

- 현재 신규 테스트는 DTO/parser/API 계약(`tests/citizen-votes-contract.test.mjs`)과 observable MSW HTTP 동작(`tests/citizen-votes-msw.test.mjs`)을 검증한다.
- `src/pages/cp-vote/hook/use-cp-vote-list-query-state.ts:18-28`의 page 전이, `src/pages/cp-vote/hook/use-cp-vote-list-controller.tsx:13-18`의 placeholder 중 선택 제한·page 변경 시 선택 초기화, `src/entities/cp-vote/hook/use-cp-vote-detail-query.ts:10-18`의 ID별 `enabled` 분기는 현재 직접적인 동작 테스트가 없다.

**권고 사항**

- 프로젝트에 승인된 React hook/component 테스트 기반이 마련될 때, 브라우저 없이 다음 상태 전이를 우선 검증한다: page 변경 시 선택 초기화, placeholder data 동안 row action 차단, 잘못된 상세 ID의 query 비활성화, 초기 오류 후 retry.
- 테스트만을 위해 새 프레임워크를 이번 작업에 역으로 도입하지 말고, 공용 테스트 기반을 도입하는 별도 범위에서 처리한다.

**기대 이점**

- API schema가 그대로여도 controller 상태 전이가 바뀌는 회귀를 계약 테스트보다 가까운 경계에서 탐지할 수 있다.

**현재 비차단 사유**

- 승인된 조회 계약은 16개 DTO/parser/API/MSW 테스트와 TypeScript build·대상 ESLint를 통과했다. 브라우저 검증은 명시적으로 금지됐고, 현재 저장소에는 이 hook 경계를 위한 표준 test script도 없으므로 후속 테스트 기반 과제다.

### P2. 시민투표 계약 어휘의 단일 출처 검토

**관찰한 사실**

- 상태 어휘는 `src/entities/cp-vote/model/types.ts:3-10`의 `CP_VOTE_STATUSES`와 `src/entities/cp-vote/api/cp-vote.dto.ts:5`의 `z.enum([...])`에 각각 선언돼 있다.
- 정렬 어휘는 `src/entities/cp-vote/api/cp-vote.dto.ts:6-15`에서 검증하고, `src/mocks/cp-vote.handlers.ts:19-28`에서 같은 모든 값의 comparator를 별도로 구현한다. comparator 쪽은 `satisfies Record<CpVoteSort, VoteComparator>`로 누락을 컴파일 시점에 막는다.

**권고 사항**

- 다음 시민참여 API 계약 추가 또는 상태·정렬 값 변경 시, runtime schema와 UI 상수 중 어느 계층을 정본으로 둘지 결정하고 Zod enum·표시 metadata가 그 정본에서 파생될 수 있는지 검토한다.
- 단순히 중복 줄 수를 줄이기 위한 전역 추상화는 만들지 말고, 두 번째 실제 계약 변경에서 동시 수정 비용이 확인될 때 시민참여 도메인 범위로 제한한다.

**기대 이점**

- backend 어휘 변경 시 schema, UI label/color, MSW 정렬 동작 사이의 불일치 가능성을 줄이고 변경 누락을 타입 검사로 더 일찍 드러낸다.

**현재 비차단 사유**

- 현재 다섯 상태와 여덟 정렬 값은 일치하며, strict schema·`satisfies`·contract/MSW 테스트가 현 계약을 보호한다. 이는 미래 변경 비용을 낮추기 위한 구조 개선이다.

### P3. 실제 backend smoke 검증의 별도 운영 단계 정의

**관찰한 사실**

- 이번 작업은 `src/entities/cp-vote/api/cp-vote.api.ts:8-25`의 `/citizen/votes` 목록·상세 GET과 `paramsSerializer: { indexes: null }`을 contract/MSW로 검증했다.
- 사용자 지시에 따라 실제 인증 backend 호출은 수행하지 않았다.

**권고 사항**

- 접근 권한과 안전한 환경이 제공되는 별도 단계에서 read-only smoke 검증의 소유자, 대상 환경, 인증 방식, 확인 항목(응답 envelope, 반복 `sort`, 날짜 offset, 401/404)을 명시한다.

**기대 이점**

- 문서·mock과 배포 환경 사이의 설정 또는 응답 envelope 차이를 릴리스 전에 확인할 수 있다.

**현재 비차단 사유**

- 실제 backend 호출은 이번 승인 범위에서 명시적으로 금지됐다. 현재 계약은 typed parser와 observable MSW HTTP 테스트로 검증됐으므로 이 항목은 권한이 주어진 이후의 운영 보강이다.

### P3. read-only 전환에 맞춘 내부 설명 정리

**관찰한 사실**

- `src/pages/cp-vote/ui/cp-vote-detail-page.tsx:4`의 내부 주석은 아직 “시민투표 상세처리”라고 적혀 있지만, `src/pages/cp-vote/ui/cp-vote-detail-view.tsx:43`은 “시민투표 상세”와 조회 설명을 사용하고 저장·상태 변경 surface는 제거됐다.

**권고 사항**

- 다음 인접 문서/UI 유지보수 때 화면 식별자 주석과 read-only 책임을 맞추고, 원본 기획 문서 표기가 의도적으로 남아야 한다면 현재 API 지원 범위를 함께 명시한다.

**기대 이점**

- 후속 작업자가 지원되지 않는 mutation 화면을 복원해야 한다고 오해할 가능성을 줄인다.

**현재 비차단 사유**

- 실행 동작이나 사용자 노출 문자열이 아닌 내부 주석 불일치다. 현재 UI·controller·API는 일관되게 read-only다.

## 장기 관찰 사항

- transport(`cp-vote.api.ts`) → runtime schema/DTO(`cp-vote.dto.ts`) → parser(`cp-vote.parser.ts`) → TanStack Query → page controller/UI로 책임이 분리돼 있어 다른 read-only 관리 화면에도 참고할 수 있는 흐름이다.
- `parseCpVoteList`는 응답 보존과 `pageCount` 계산만 수행하고, `parseCpVoteDetail`은 집계 불변식까지 runtime에서 검증한다. backend 응답을 화면 모델로 넘기기 전에 실패시키는 경계가 명확하다.
- unsupported mutation/search surface를 삭제한 결정은 현재 공개 GET 계약보다 UI 기능이 앞서 나가지 않게 했다. 쓰기 계약이 실제로 제공되기 전까지 이 read-only 경계를 유지하는 것이 안전하다.

## 목록에 등록할 재사용 가능 자산 후보

1. **typed read-only API 흐름**: `src/entities/cp-vote/api/`, `src/entities/cp-vote/hook/`, `src/pages/cp-vote/hook/`의 transport-schema-parser-query-controller 분리.
2. **Node TypeScript 계약 테스트 패턴**: `tests/citizen-votes-contract.test.mjs`의 `tsImport` 기반 schema/parser/API 검증.
3. **observable MSW 계약 패턴**: `tests/citizen-votes-msw.test.mjs`의 실제 `fetch`, 반복 query parameter, pagination 상한, 400/401/404 검증과 명시적 server cleanup.

후보 등록은 재사용 가능성을 기록하는 제안이며, 이번 평가에서 공용 코드나 자산 목록을 수정하지 않는다.

## 기술 부채 요약

| 우선순위 | 부채 | 현재 보호 장치 | 후속 시점 |
| --- | --- | --- | --- |
| P1 | 표준 `npm run test` 부재 | 직접 16/16 및 반복 안정 실행 | 다음 테스트/CI 정비 작업 |
| P2 | hook/controller 상태 전이의 직접 테스트 부재 | build, 대상 ESLint, API·MSW 계약 테스트 | 공용 비브라우저 React 테스트 기반 승인 시 |
| P2 | 상태·정렬 계약 어휘의 복수 선언 | strict Zod schema, `satisfies`, contract/MSW 테스트 | 다음 계약 값 변경 또는 두 번째 소비 사례 |
| P3 | 실제 backend smoke 단계 미정 | typed parser와 MSW HTTP 검증 | 접근 권한과 안전한 환경 제공 시 |
| P3 | 상세 page 내부 주석의 이전 “상세처리” 표현 | 실제 API/controller/UI는 read-only | 다음 인접 유지보수 |

## 프로세스 개선 사항

- pathspec 기반 검증과 소유권 분리를 유지한다. 이번 Watcher 기록처럼 승인 파일과 미소유 동시 변경을 분리하면 공유 worktree에서도 작업 판정과 stage 범위를 명확히 할 수 있다.
- loader 교체처럼 런타임 종료 안정성을 다루는 변경은 “최종 1회 성공”뿐 아니라 반복 실행 결과와 마지막 dependency sync 이후 재실행을 함께 남기는 방식을 재사용한다.
- 실제 backend 또는 브라우저 검증이 금지된 작업은 수행하지 않은 검증을 PASS 근거로 추정하지 않고, 허용 조건이 생겼을 때 실행할 별도 운영 gate로 기록한다.

## 최종 권고

현재 scoped PASS를 유지하고 승인 pathspec의 commit 절차를 진행해도 된다. 후속 개선은 **P1 표준 테스트 진입점**, **P2 테스트 패턴 재사용 등록·orchestration 테스트·계약 어휘 단일 출처 검토**, **P3 backend smoke 운영 단계·내부 설명 정리** 순으로 별도 승인 범위에서 다룬다.
