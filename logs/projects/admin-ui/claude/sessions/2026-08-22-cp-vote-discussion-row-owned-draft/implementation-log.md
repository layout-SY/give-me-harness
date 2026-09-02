# 구현 기록

## 상태
- `paused_after_generator`
- 사용자 승인 B안의 Generator 구현과 정적 검증을 완료했다.
- Watcher를 실행할 수 없어 Closure 및 완료 처리는 보류한다.

## 변경 파일
- `src/pages/cp-vote/ui/use-cp-vote-list-process.tsx`
- `src/pages/cp-discussion/ui/use-cp-discussion-list-process.tsx`
- `.codex/logs/sessions/2026-08-22-cp-vote-discussion-row-owned-draft/implementation-log.md`

## 구현 결론
- 두 목록 process의 `useStatusTransition`에 `resetKey: selectedRow?.id ?? null`을 전달해 상태 초안을 선택 행 ID에 귀속했다.
- 공개 기준 초안을 Vote는 `{ voteId, index } | null`, Discussion은 `{ discussionId, index } | null`인 readonly 로컬 타입으로 모델링했다.
- 공개 기준 index는 현재 행 소유 초안이 있으면 초안 값을, 아니면 현재 행의 persisted disclosure 값을 사용한다.
- 선택 행이 없을 때는 기존 외부 계약대로 index `0`을 유지한다.
- `changeDisclosure`는 선택 행이 없으면 조기 반환하고, 있으면 행 ID와 index를 함께 저장한다.
- mutation payload와 `canSave`는 현재 선택 행에 대해 파생된 공개 기준만 사용한다.
- `reset`, 명시적 행 선택, mutation 성공 시 공개 기준 초안을 제거한다.
- process 반환 interface와 controller/view 계약은 변경하지 않았다.

## 보존한 불변식
1. 상태 초안과 공개 기준 초안은 각각 생성한 행 ID에서만 유효하다.
2. 같은 query에서 선택 행이 fallback되면 새 행의 persisted disclosure index가 즉시 사용된다.
3. 선택 행이 없을 때 Dropdown index는 `0`이다.
4. mutation 대상 ID와 mutation payload에 반영되는 현재 행 초안의 소유 ID가 일치한다.
5. 저장 실패 시 현재 행 소유 초안은 유지하고, 저장 성공 시 제거한다.

## 검증
- LSP diagnostics: TypeScript language server가 설치되어 있지 않고 기존 설치 거절 상태여서 실행 불가 제약을 확인했다.
- 1차 `yarn eslint ... && yarn build`: scoped ESLint 통과 후 nullable draft narrowing 오류 2건으로 build 실패.
- draft가 `null`이 아님을 명시적으로 좁혀 수정했다.
- 최종 scoped ESLint: 통과.
- 최종 `yarn build`: 통과 (`tsc -b && vite build`). 기존 Vite tsconfig-paths 안내와 500 kB 초과 chunk 경고만 출력됐다.
- scoped `git diff --check`: 통과.
- pure LOC: Vote 110, Discussion 111로 두 파일 모두 200줄 이하이다.
- Bun no-excuse audit: 로컬에 `bun`이 설치되지 않아 실행하지 못했다. scoped ESLint와 `tsc -b`로 대체했다.
- 테스트: 프로젝트에 test runner script가 없어 추가하거나 실행하지 않았다.
- Vote 브라우저 회귀:
  - `VOTING` 필터에서 VT-001에 `CLOSING_SOON` 상태 draft와 공개 기준 index `-1` draft를 만들었다.
  - fixture의 공개 기준 선택지가 하나뿐이어서 기존 Dropdown callback을 React runtime에서 직접 호출해 index `-1` 입력을 재현했다. 이 계측은 제품 source에 포함되지 않는다.
  - 외부 process 요청으로 VT-001을 `COMPLETED`로 변경한 뒤 같은 QueryClient의 활성 query를 refetch했다.
  - VT-002 fallback 후 상태는 placeholder, 공개 기준은 VT-002 persisted `종료 후 자동 공개`, 저장은 비활성 상태였다.
- Discussion 브라우저 회귀:
  - `OPEN` 필터에서 DS-001에 `CLOSED` 상태 draft와 공개 기준 index `-1` draft를 만들었다.
  - 외부 process 요청 후 같은 query를 refetch해 DS-002 fallback을 유도했다.
  - DS-002에서 상태 placeholder, persisted `종료 후 공개`, 저장 비활성 상태를 확인했다.
- 최종 browser console: error 0건, warning 0건.
- 1391×1043 Vote·Discussion fallback 캡처를 검증했다.
- 1차 독립 시각 검토에서 Vote 캡처가 fallback 전 상태라 `REVISE`를 받았고, 제품 수정 없이 정확한 VT-002 fallback 상태로 재캡처했다.
- fresh complete 캡처 세트의 최종 독립 Visual QA Oracle 2회가 모두 `PASS`, 차단 0건을 반환했다.

## 실행 경로
- 구성된 Planner는 외부 provider credit 소진으로 시작하지 못해 동일 read-only 역할 계약의 독립 planning 경로를 사용했다.
- 구성된 Generator도 같은 외부 차단으로 시작하지 못해 동일 구현 범위와 출력 계약의 독립 Generator 경로를 사용했다.
- Oracle은 브라우저·source evidence의 독립 교차 검토만 수행했으며 프로젝트 Watcher를 대체하지 않는다.

## 아키텍처 자체 검토
- 단일 책임: 각 process hook은 해당 목록의 선택·draft·mutation 상태만 소유한다.
- 경계 순수성: API·DTO·query·View·shared UI 계약을 변경하지 않았다.
- 타입 안전: readonly 로컬 value type을 사용했고 `any`, type assertion, non-null assertion, suppress comment를 추가하지 않았다.
- 추상화: 기존 Proposal 패턴을 두 도메인 내부에서 재사용했으며 신규 공용 helper나 hook을 만들지 않았다.
- 파생 상태: effect 동기화 없이 현재 행 ID와 draft 소유 ID 비교로 현재 렌더부터 잘못된 draft를 배제한다.

## 잔여 위험 및 다음 게이트
- test runner 부재로 자동 회귀 테스트는 없다. 실제 브라우저 same-query fallback과 정적 검증으로 보완했다.
- 기존 build chunk 크기 경고는 이번 변경 범위 밖이다.
- Vote 날짜 placeholder 마지막 음절 줄바꿈은 기존 시각 부채이며 별도 backlog로 유지한다.
- Watcher의 독립 판정 전에는 `confirmed` 또는 완료 상태로 전환할 수 없다.

## Portfolio evidence
- 문제: 행 ID를 포함하지 않은 상태·공개 기준 초안이 same-query fallback 후 다른 행의 표시·저장 payload와 결합될 수 있었다.
- 선택: `resetKey`만 추가하는 A안 대신 상태와 공개 기준 모두 행 소유권을 갖는 승인 B안을 적용했다.
- 적용: 신규 공용 추상화 없이 기존 Proposal의 행 소유 선택 패턴을 Vote·Discussion process 내부에 제한적으로 재사용했다.
- 결과: 현재 행 ID가 일치하는 초안만 UI 파생값, `canSave`, mutation payload에 참여하도록 정적 구조를 변경했다.
- 검증 근거: scoped ESLint, TypeScript 포함 project build, scoped whitespace 검사, 두 도메인 same-query fallback, console 0건, 독립 Visual QA 2회 통과. Watcher는 미실행 상태로 명시했다.
