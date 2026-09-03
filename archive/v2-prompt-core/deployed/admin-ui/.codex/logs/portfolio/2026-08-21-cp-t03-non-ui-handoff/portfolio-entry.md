# 포트폴리오 경험 기록

## 작업 개요
- 구현/수정 내용: 이미 구현·독립 확인된 T03 Discussion non-UI 계약을 문서/증거로 종료하고 UI ownership을 Claude에게 분리 인계.
- 구현 이유: non-UI 완료가 UI/visual 완료로 확대 해석되지 않으면서 다음 tranche를 안전하게 시작할 기준이 필요했다.
- 작업 유형: documentation-only closure / ownership handoff.

## 문제 상황
- 문제 출처: 사용자 소유권 변경 + 기존 독립 Watcher 측정.
- 대상 도메인·서비스: CP Discussion local provisional API/MSW.
- 기존 문제와 영향: 3개 non-UI operation은 confirmed였지만 T03 UI diff와 shared visual finding이 같은 tranche에 남아 있어 완료 경계가 불명확했다.

## 고민 과정

| 접근법 | 장점 | 단점 | 선택 여부와 이유 |
|---|---|---|---|
| T03 전체를 UI 포함 완료 처리 | 단순한 상태 표기 | 사용자 소유권과 미완료 visual 범위를 왜곡 | 미채택 |
| 현재 UI diff를 되돌리고 non-UI만 남김 | diff 분리 가능 | 사용자의 “KEEP current T03 UI diff” 결정 위반 | 미채택 |
| 기존 증거를 source/runtime로 분류하고 frozen baseline + Claude handoff 작성 | 완료 경계와 후속 write guard가 명확 | 문서/증거 관리 필요 | 채택 |

**판단 기준**: 사용자 ownership 결정 보존, 측정값만 사용, 제품 write `0`, Watcher/Evaluator 역할 분리.

## 사용 기술과 구체적 목적

| 기술/패턴/아키텍처 | 해결하려는 문제 | 적용 위치와 목적 | 미채택 대안/이유 |
|---|---|---|---|
| JSON evidence index | source/runtime 주장 혼합 방지 | operation·negative·parser·state·quality 출처 통합 | 서술 문서만 사용 시 기계 검증 어려움 |
| SHA-256 frozen manifest | dirty worktree에서 이후 write 식별 | 302-file aggregate + 39 dirty path 개별 hash | clean checkout 강제는 기존 변경 훼손 |
| ownership boundary | UI/non-UI 완료 혼동 방지 | Claude-owned 경로·blocker·미청구 범위 명시 | UI patch 처방은 요청 범위 밖 |

## 적용 내용
- 실제 구현·수정·리팩터링: 제품 변경 없음. 세션 문서 6개, portfolio 1개, closure evidence 5개 작성.
- AI 하네스 변경: 없음. active plan/Boulder/ledger를 수정하지 않음.
- 구조 변화 도식: `기존 Generator + independent Watcher → closure index → non-UI confirmed / Claude UI deferred`.

## 결과

### 결과 1: non-UI 증거 종료
- 3 operations와 `400/404/500`, malformed-success Zod rejection, same-session state, unhandled CP `0`, quality gates를 출처별로 인덱싱했다.
- **도출 이유**: 측정된 기능 결과만 다음 T04 의존성으로 사용할 수 있게 하기 위해서다.

### 결과 2: ownership 결정 후 frozen baseline
- 302개 frozen file aggregate SHA-256, dirty 39개 경로의 상태/개별 SHA-256, Git HEAD/branch를 기록했다.
- **도출 이유**: 기존 UI/shared/package dirty diff를 보존하면서 이후 Hephaestus write `0`을 비교할 기준이 필요했기 때문이다.

### 결과 3: Claude UI handoff
- page/UI/shared/widgets/routes/navigation/controls/loading·error·empty/visual/global contrast를 Claude 소유로 명시했다.
- **도출 이유**: 사용자가 현재 T03 UI diff 유지와 Claude 소유를 직접 선택했기 때문이다.

## 성과
- before: non-UI `confirmed`와 UI/visual deferred 범위가 기존 T03 증거 여러 위치에 분산.
- after: 필수 12개 closure 파일과 단일 evidence index/ownership boundary로 분리.
- 검증 결과: scoped ESLint/tsc/build exit `0`, pure LOC 최대 `168`, runtime unhandled CP `0`은 기존 independent evidence에서 확인; 이번 closure 제품 write `0`.
- 사용자 후속 피드백: 현재 T03 UI diff를 보존하고 Claude가 계속 소유하도록 확정.
- 잔여 리스크: provisional backend 계약, Claude-owned shared navigation first-paint overlay 및 informative/KPI contrast.

## 회고
- 잘된 판단: UI를 되돌리거나 완료로 합산하지 않고 ownership decision 이후 상태를 baseline으로 동결했다.
- 다시 한다면 바꿀 점: 최초 tranche부터 non-UI와 UI evidence root를 분리해 후속 ownership 변경 비용을 줄인다.
- 다음 작업에 적용할 인사이트: dirty worktree에서는 “clean”이 아니라 결정 시점의 status+hash 보존과 scope-specific zero-write 비교가 더 정확하다.
