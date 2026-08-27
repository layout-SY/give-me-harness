# Review Log — calendar-picker 리팩토링 (watcher, round 1)

> 기준선: plan.md, implementation-log.md
> 검증일: 2026-07-06

## 1. 회귀 검증

- `npx tsc --noEmit`(프로젝트 기본, tsconfig.json): 0 errors 확인 (전체 프로젝트).
- `npx tsc --noEmit -p tsconfig.app.json`: calendar-picker에서 TS1294(`model/useDateRangeState.ts:21` const enum) 1건 실측. `git stash`로 리팩터링 이전 상태(`ui/hook/useDateRangeState.ts`) 대비 비교 결과 **동일 코드가 이동만 된 것으로 신규 유입 아님** 확인. 프로젝트 quality 게이트(`tsc --noEmit` 기본 tsconfig)는 이 옵션을 쓰지 않으므로 게이트 대상 아님 — refactorer 주장과 일치.
- `npx eslint src/features/calendar-picker`: 3 problems(1 error, 2 warning) 실측. `git stash`로 원본과 대조한 결과 세 건 모두 원본 `ui/hook/*` 파일에 동일하게 존재하던 이슈(useMemo deps 경고, useWeekFromClickBehavior ref-in-render 에러, calendar-picker.tsx useEffect deps 경고)가 위치만 이동한 것 — **신규 유입 0** 확인.

## 2. 경로 파손 0

- `grep -rn "ui/utils\|ui/hook\|ui/types\|ui/pub-sub" src .claude`: 실제 소스(`src/`) 내 잔존 참조 0건. `.claude/logs/**`의 매치는 모두 과거 시점 기록/artifact 문서(before 표기, 세션 로그)로 실 코드 참조 아님 — 문제 없음.
- `src/ARCHITECTURE.md:42`, `.claude/logs/dependency/2026-07-03-fsd-layer-contract.md:95` 모두 `model/pub-sub.events.ts`로 갱신 확인.
- 외부 소비자 없음 재확인(`pages/` 미배선).

## 3. FSD 세그먼트 정합

- `ui/`: `calendar-picker.tsx/.css`, `DateRangeField.tsx/.css`, `index.ts`만 잔류 — 표현 자산만 존재, 계약 부합.
- `model/`: `types.ts`, `pub-sub.events.ts`, `useCalendarPicker.ts`, `useDateRangeState.ts`, `behaviors/*` — 타입/훅/pubsub 계약 소유, 계약 부합.
- `lib/`: `date-range.ts`, `calendar-cells.ts` — React/pubsub 비의존 순수 함수만 존재, 계약 부합.
- `ui/index.ts` public API 유지(형제 `image-manager` 컨벤션 일치) 확인.

## 4. §0 3-질문 오적용 체크

- `buildCalendarCells`: React import 없음, pubsub 미참조, 인자→반환값만으로 결정되는 순수 파생 함수 확인(`lib/calendar-cells.ts` 실측). Q1 단독 통과 근거 타당.
- 만능 `useXxx` 훅으로의 결합 없음 — 오히려 훅 4종(`useCalendarPicker`, `useDateRangeState`, behaviors 3종)은 그대로 개별 유지되고 위치만 `model/`로 교정됨. 과분리/불필요 추출 없음.
- 뷰-로컬 상태의 불필요한 외부 hook화 없음 — 상태 훅은 원래도 도메인 훅이었고 이번에 신규 훅화된 뷰-로컬 상태 없음.
- 결론: §0 오적용 사례 없음, pass.

## 5. 동작 동일성 (renderCells → buildCalendarCells)

- `git diff ui/calendar-picker.tsx` 실측: className 조립 순서(today→start→end→in-range) 동일, `onClick` 가드(`cell.isInMonth && !cell.isDisabled`)·`disabled`(`!cell.isInMonth || cell.isDisabled`)·표시값(`cell.isInMonth ? cell.day : ""`) 모두 원본과 논리적으로 동치.
- `start &&`/`end &&` → `startTime !== null`/`endTime !== null` 명시화: 원본은 `start`/`end`가 `number | null`(`setHours` 반환값)이었으므로 falsy 조건은 `null` 또는 `0`(1970-01-01 자정, epoch 0)뿐. 실사용 범위(달력 UI 날짜 선택)에서 `start`/`end`가 epoch 0(1970-01-01)이 되는 경우는 실질적으로 발생하지 않으므로 의미 불변 주장 타당. 코드 검토상 문제 없음.
- 결론: 동작 동일성 확인, pass.

## 6. 범위 준수

- `model/useDateRangeState.ts`, `model/behaviors/useCalendarBehavior.ts` 등 diff 확인 결과 import 경로 변경 외 로직 변경 없음 — P2(useMemo deps 정리, setRange 제거) 미수행 확인, 범위 준수.
- evaluator "하지 말 것"(behavior 파이프라인 해체, 훅 인라인화, 공용 제네릭 훅 신설) 수행 흔적 없음.

## 7. 범위 외 발견 사항 (신규 이슈)

- **`git diff --stat` 확인 결과 `src/shared/config/constants.ts`가 함께 수정된 상태**로 워킹트리에 존재함. `LOCAL_STORAGE_ACCESS_TOKEN_KEY`/`REFRESH_TOKEN_KEY`/`LANGUAGE_KEY` 값이 `synthoria-admin-*` → `admin-*`로 변경됨.
  - plan.md/implementation-log.md 어디에도 이 파일 변경에 대한 언급 없음 — 이번 calendar-picker 세그먼트 재배치/`buildCalendarCells` 추출과 무관한 범위 외 변경.
  - 실사용자 영향 가능성 있는 **기능적 변경**(localStorage 키 이름 변경은 배포 시 기존 저장된 토큰 키와 불일치를 유발해 로그인 세션 파손 가능) — behavior-preserving을 표방하는 이번 리팩터링 성격과 상충.
  - 원인 불명(사전 존재하던 미커밋 워킹트리 변경일 가능성 있음). 이번 세션의 refactorer 산출물로 커밋될 경우 무관 변경이 리뷰 없이 병합되는 위험이 있으므로, 커밋 전 **분리 또는 원복** 필요.

## 판정

calendar-picker 세그먼트 재배치 + buildCalendarCells 추출 자체는 항목 1~6 전부 통과. 다만 워킹트리에 무관 파일(`src/shared/config/constants.ts`) 변경이 섞여 있어 이번 산출물 그대로 커밋 시 범위 외 기능 변경이 리뷰 없이 편입되는 위험이 있음 — 이를 반려 사유로 처리.
