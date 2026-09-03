# Dependency & Architecture Decision — calendar-picker FSD Segment Relocation

> 작성일: 2026-07-06
> 도메인: `src/features/calendar-picker`
> 근거: evaluator 진단(이관) — "행위 파이프라인·의존 방향은 건강, 세그먼트 배치만 표준 불일치"
> 관련 계약: `src/ARCHITECTURE.md`(L38-44), `.claude/logs/dependency/2026-07-03-fsd-layer-contract.md`(L85-100, ADR-2)

---

## 1. 결정 요약

- **레이어(features)·의존 방향(features → shared)은 변경하지 않는다.** 이번 작업은 슬라이스 **내부 세그먼트 재배치**(behavior-neutral) + **순수 조각 lib 추출** 1건뿐이다.
- **하지 않는 것(명시적 억제)**: behavior 파이프라인 해체, `useCalendarPicker`/`useDateRangeState` 인라인화, 공용 제네릭 훅 신설 — evaluator가 "불필요/안티패턴 소지"로 판정.

## 2. 세그먼트 재배치 (Before → After)

| 자산 | Before | After | 근거 |
|---|---|---|---|
| `types.ts` | `ui/types.ts` | `model/types.ts` | 도메인 타입은 `model` 소유 (표준 세그먼트) |
| `pub-sub.events.ts` | `ui/pub-sub.events.ts` | `model/pub-sub.events.ts` | `entities/dao/model/pub-sub.events.ts`와 위치 일치 — calendar만 예외였음 |
| `hook/useDateRangeState.ts` | `ui/hook/` | `model/useDateRangeState.ts` | 상태 소유 도메인 훅 |
| `hook/useCalendarPicker.ts` | `ui/hook/` | `model/useCalendarPicker.ts` | 상태/부수효과(pubsub) 소유 도메인 훅 |
| `hook/behaviors/*` (3파일) | `ui/hook/behaviors/` | `model/behaviors/` | 정책 합성 훅 — model 소유 |
| `utils/date-range.ts` | `ui/utils/date-range.ts` | `lib/date-range.ts` | 순수함수, `utils`는 비표준 세그먼트명 → `lib` |
| (신규) `calendar-cells.ts` | 없음(`calendar-picker.tsx` L200-253 인라인) | `lib/calendar-cells.ts` | 순수 파생 로직 추출 (hook-extraction §0 Q1 통과) |
| `calendar-picker.tsx`, `DateRangeField.tsx`, `*.css` | `ui/` | `ui/` (유지) | 표현 컴포넌트만 `ui`에 남김 |
| `index.ts` (public API) | `ui/index.ts` | `ui/index.ts` (유지) | 형제 슬라이스(`image-manager/ui/index.ts`) 컨벤션과 일치 — 슬라이스 루트 index.ts 미도입 |

## 3. 공용화 수준

- 전 자산 **도메인 내 공용화(feature 슬라이스 내부)** 유지. 글로벌 공용화 대상 아님 (evaluator: 공용 제네릭 훅 신설 금지).
- `lib/calendar-cells.ts`도 calendar-picker 슬라이스 로컬 순수 함수로 배치 — 타 도메인 재사용 사례 없음(공통화 조건 미충족, `policy-refactoring` 금지 항목 "사용처 1곳만 있는 코드를 선제 추출"과는 무관 — 이건 추출 자체가 아니라 슬라이스 내부 재배치).

## 4. 외부 소비자 영향

- `grep -rn "features/calendar-picker" src` 결과, 슬라이스 외부에서 실제 import하는 코드 없음 (주석 참조 1건만 존재, `src/shared/lib/pub-sub/events.ts:7`). `pages/`가 아직 비어 있어 이 feature는 미배선 상태 — **외부 파손 위험 0**.
- `pub-sub.events.ts`의 `declare module "~/shared/lib/pub-sub/events"` 선언 병합은 파일의 물리적 위치와 무관하게 `src/**` 컴파일 포함 범위 내에서 전역 병합되므로, `model/`로 이동해도 병합 자체는 깨지지 않음. 단 **문서상 경로 표기**(ARCHITECTURE.md L43, 2026-07-03 계약 L95)는 실제 파일 위치와 어긋나므로 갱신 필요.

## 5. 문서 동기화 대상 (신규 경로 반영)

- `src/ARCHITECTURE.md` L43: `features/calendar-picker/ui/pub-sub.events.ts` → `features/calendar-picker/model/pub-sub.events.ts`
- `.claude/logs/dependency/2026-07-03-fsd-layer-contract.md` L95: 동일 경로 갱신 (ADR-2 항목)

## 6. tsc 베이스라인

- 실측(2026-07-06, `tsc --noEmit`): **0 errors**. (ARCHITECTURE.md에 기록된 "16건"은 갱신 시점 이후 해소된 것으로 보임 — 문서 stale 가능성, 별도 확인 필요하나 이번 작업 범위 아님.)
- 게이트 기준: 재배치 후 **신규 결함 0** (0 → 0 유지가 목표).
