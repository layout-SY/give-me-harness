# Plan — calendar-picker 리팩토링 (evaluator 진단 이관)

> work_type: refactor / 도메인: `src/features/calendar-picker`
> 참고 계약: `src/ARCHITECTURE.md`, `.claude/logs/dependency/2026-07-03-fsd-layer-contract.md`,
> 신규: `.claude/logs/dependency/2026-07-06-calendar-picker-fsd-segment-relocation.md`,
> `.claude/logs/artifacts/2026-07-06-calendar-picker-fsd-structure.md`

## 0. 리팩터링 요청 선판정 (policy-hook-extraction §0)

evaluator 진단을 3-질문으로 재검증:

| 대상 | Q1 (React 없이 순수함수?) | Q2 (다른 곳에서도 재사용?) | Q3 (빼면 거의 순수렌더?) | 판정 |
|---|---|---|---|---|
| `ui/utils/date-range.ts` (기존 순수함수) | 이미 예 | 슬라이스 내부(behaviors 2곳) 재사용 중 | — | **세그먼트명만 교정** (`utils`→`lib`), 분리 자체는 이미 완료됨 |
| `calendar-picker.tsx` L200-253 (daysInMonth/firstDay/totalCells + cell class 계산) | **예** — 입력(year,month,start,end,today,isDateDisabled)만으로 결정되는 순수 파생 | 아니오(단일 사용) | — | Q1 단독 통과로 충분 → `lib` 추출 확정 (재사용 무관, 테스트·가독성 이득 확정적) |
| `useCalendarBehavior`/`useFreeRangeBehavior`/`useWeekFromClickBehavior`/`useCalendarPicker`/`useDateRangeState` (기존 훅) | 아니오 (상태/부수효과 본질) | 도메인 전용 | — | **분리 유지, 재구성 금지** — 이미 상태성 기준에 맞는 도메인 훅. 위치(세그먼트)만 `model/`로 교정 |

**결론**: evaluator 진단은 안티패턴이 아니며 정당하다. "세그먼트 재배치"는 순수 위치 교정(행위 0 변화), "buildCalendarCells 추출"은 Q1 단독 통과로 정당한 lib 분리다. **behavior 파이프라인 해체·훅 인라인화·공용 제네릭 훅 신설은 3-질문 어디에도 해당하지 않으므로 수행하지 않는다** (evaluator "하지 말 것" 항목과 일치).

## 1. FSD 결정 (planner 확정)

- 레이어/의존 방향: 변경 없음 (`features/calendar-picker → shared`만 허용, 기존 유지).
- 공용화 수준: **슬라이스 내부(도메인 내) 공용화만**. 글로벌/타 도메인 공용화 대상 아님.
- 세그먼트 재배치 상세: `.claude/logs/artifacts/2026-07-06-calendar-picker-fsd-structure.md` 참조 (ui/model/lib 3분할, public API는 `ui/index.ts` 유지 — `image-manager` 형제 컨벤션과 일치).
- 상세 의존성/문서동기화 근거: `.claude/logs/dependency/2026-07-06-calendar-picker-fsd-segment-relocation.md`.

## 2. 범위

### in (이번 작업 범위)
- **P1-a**: 세그먼트 재배치 (`ui/types.ts`→`model/types.ts`, `ui/pub-sub.events.ts`→`model/pub-sub.events.ts`, `ui/hook/*`→`model/*`, `ui/utils/date-range.ts`→`lib/date-range.ts`) + 슬라이스 내부 상대경로 전량 remap (목록: `exploration.md` §3) + 문서 동기화 (`ARCHITECTURE.md` L43, `2026-07-03-fsd-layer-contract.md` L95).
- **P1-b**: `calendar-picker.tsx`의 `renderCells`(L200-253) 순수 파생 로직을 `lib/calendar-cells.ts`의 `buildCalendarCells(...)`로 추출. 시그니처는 `.claude/logs/artifacts/2026-07-06-calendar-picker-fsd-structure.md` 참조. **동일 동작 보존**(behavior 0 변화) — 렌더링 결과(className, 비활성 여부)는 픽셀 단위로 동일해야 함.

### out (이번 범위 제외 — 후속)
- **P2** (useCalendarBehavior useMemo deps 정리 / useDateRangeState의 미사용 setRange 제거·setFormState 노출 축소): **이번 범위에서 제외**. 사유 — P2는 실제 런타임 동작(메모이제이션 시점, 소비 표면적)을 변경하는 개선이라 세그먼트 재배치(행위 0 변화)와 리스크 성격이 다르다. 구조 이동과 동시에 섞으면 회귀 원인 분리(rollback 단위)가 어려워진다. 별도 세션/PR로 분리 진행 권장.
- evaluator가 명시한 "하지 말 것" 전체(behavior 파이프라인 해체, 훅 인라인화 강요, 공용 제네릭 훅 신설)는 범위 외 확정.

## 3. 섹션 분해 및 실행 순서

| 섹션 | 내용 | 담당 | 참조 SKILL | 게이트 |
|---|---|---|---|---|
| 1 | P1-a: 파일 이동(`git mv` 또는 이동+삭제) + import 경로 remap(위 표 전량) + `ui/index.ts` 재노출 경로 수정 | refactorer | `policy-refactoring`, `coding-convention` | watcher: `tsc --noEmit` 0 errors, 파일 위치가 `.claude/logs/artifacts/...structure.md`와 일치 |
| 2 | P1-a 문서 동기화: `src/ARCHITECTURE.md` L43, `2026-07-03-fsd-layer-contract.md` L95 경로 갱신 | refactorer | `documentation` | watcher: grep 결과 구 경로(`ui/pub-sub.events.ts`) 잔존 0건 |
| 3 | P1-b: `buildCalendarCells` 순수 함수 추출 + `calendar-picker.tsx`의 `renderCells`를 결과 소비로 축소 | refactorer | `policy-hook-extraction`(§0 근거), `policy-refactoring` | watcher: 렌더 결과 className 로직 diff 없음(동작 동일성), `tsc --noEmit` 0 errors |
| — | (섹션 1~3 종료 후) 최종 통합 검증 | watcher | `review-checklist` | `yarn lint && tsc --noEmit` 통과, 신규 결함 0 |

- 섹션 1→2→3 순차 실행(1,2는 병렬 가능하나 refactorer 단일 세션 내 순차 권장 — 파일 이동이 먼저 끝나야 경로 문자열이 확정되어 문서 동기화 가능).
- 각 섹션 종료 시 watcher 게이트 통과 필요. 섹션 간 승인 재요청 없음(전체 계획을 한 번에 승인받아 진행).

## 4. required_agents / required_skills

- required_agents: `refactorer`, `watcher`
- required_skills: `policy-hook-extraction`(§0 판단 근거), `policy-refactoring`, `coding-convention`, `documentation`, `review-checklist`
- publisher 필요 여부: **불필요** (UI 표현/스타일 변경 없음, 순수 구조 이동 + 내부 로직 추출).

## 5. 리스크 및 완화

- 상대경로 remap 누락 시 빌드 즉시 실패 → `tsc --noEmit`이 1차 안전망(현재 베이스라인 0 errors 확보 완료, `exploration.md` §6).
- `pub-sub.events.ts`의 `declare module` 선언병합은 파일 위치 무관하게 `src/**` 컴파일 범위 내 병합되므로 이동 자체로 인한 타입 손실 없음(문서 표기만 갱신 필요).
- 외부 소비자 없음(`pages/` 미배선) → 슬라이스 경계 밖 파손 위험 0 (exploration.md §2).
