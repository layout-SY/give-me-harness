# Final Summary — calendar-picker 리팩토링

> 작성일: 2026-07-06
> 파이프라인: evaluator(진단) → planner(계획) → refactorer(실행) → watcher(게이트) → 사후 정정(사용자 피드백)
> 상세: `plan.md` · `exploration.md` · `implementation-log.md` · `review-log.md`

## What Changed
- **FSD 세그먼트 재배치**: `ui/` 아래 평평하게 쌓였던 자산을 표준 세그먼트로 분리.
  ```
  features/calendar-picker/
  ├── ui/     calendar-picker.tsx, DateRangeField.tsx, *.css, index.ts
  ├── hook/   useCalendarPicker.ts, useDateRangeState.ts, behaviors/*
  ├── model/  types.ts, pub-sub.events.ts
  └── lib/    date-range.ts, calendar-cells.ts
  ```
- **순수 함수 추출(P1-b)**: `calendar-picker.tsx` `renderCells`의 순수 파생 로직 → `lib/calendar-cells.ts`의 `buildCalendarCells(...)`. 렌더는 결과 map만 수행.
- **계약 문서 동기화**: `src/ARCHITECTURE.md`, `.claude/logs/dependency/2026-07-03-fsd-layer-contract.md` — pub-sub 경로(`ui/→model/`) + **`hook/` 세그먼트 규약 명문화**("훅은 model이 아니라 hook에 둔다").

## Why It Changed
- evaluator 진단: 기능/의존은 건강, **세그먼트 배치만** 표준 불일치(순수함수·훅·타입이 `ui/`에 혼재). 추상화·의존 방향은 손대지 않음(과리팩토링 방지).
- 사용자 피드백: 훅은 `model/`이 아닌 전용 `hook/` 세그먼트에 둔다(초기 재배치 정정).

## Reused Assets
- 기존 훅/behavior/유틸 전량 보존(이동만). 로직 변경 0.
- `shared/lib/date.util`, `shared/lib/pub-sub` 등 shared 의존 그대로.

## Impacted Areas
- calendar-picker 슬라이스 내부 파일 이동 + 상대 import 전량 remap. 외부 소비자 없음(pages 미배선) → 슬라이스 경계 밖 영향 0.
- 계약 문서 2건.

## Remaining Risks
- **범위 외 미커밋 변경**: `src/shared/config/constants.ts`(localStorage 키 `synthoria-admin-*`→`admin-*`)가 워킹트리에 존재. 본 리팩터와 무관한 사전 편집(리브랜딩 성격)으로, 원복하지 않고 보존. **커밋 시 calendar-picker와 분리 권장.**
- P2(useCalendarBehavior useMemo deps, useDateRangeState setRange)는 런타임 성격이 달라 별도 세션으로 이월.
- 선재 이슈: `useDateRangeState.ts` const enum(TS1294, app tsconfig 전용), eslint 3건 — 모두 원본부터 존재, 범위 외.

## Verification
- `tsc --noEmit`(tsconfig.json, 프로젝트 게이트): **0 errors** (전체). 재배치·hook 이동 후에도 회귀 0.
- 구 경로(`ui/utils`, `ui/hook`, `ui/types`, `ui/pub-sub`) 잔존 참조 0.
- `buildCalendarCells` 순수성(React/pubsub 무의존) + renderCells 동작 동일성 확인(watcher 항목 1~6 통과).

## Follow-up
- watcher 1회차 반려는 범위 외 constants.ts 혼입이 유일 사유였고, 그 정체(무관 사전 편집)를 규명·분리함. calendar-picker 리팩터 자체는 전 항목 통과.
- 필요 시 watcher 재게이트로 형식 승인(pass) 획득 가능.
- P2 개선은 backlog 이월 후보.
