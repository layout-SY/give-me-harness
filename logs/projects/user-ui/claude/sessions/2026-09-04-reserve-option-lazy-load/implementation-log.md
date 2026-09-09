# Implementation Log

## Task Summary
드롭다운 어댑터에 열림·로딩·빈 목록 계약을 추가해 예약 옵션을 "목록이 열릴 때" 조회할 수 있게 만들고, 전역 팝업 폭을 고정 모바일 셸에 맞췄다. 실제 조회는 Logic 역할이 채우도록 props 계약까지만 열어 두고, 미리보기 라우트에서 그 계약이 동작하는지 확인할 수 있게 했다.

## Reused Assets
- HeroUI `Select`의 상속 prop `onOpenChange`(react-stately 계약)
- RAC `ListBox`의 `renderEmptyState`
- 기존 토큰 `--app-mobile-max`, `--text-muted`, `--space-2`, `--space-3`

## New Files / Updated Files
- 신규 `src/shared/ui/dropdown/dropdown.css` — `.dropdown-field`(폭 100%), `.dropdown-empty-state`(빈 상태 문구)
- 수정 `src/shared/ui/dropdown/dropdown.tsx` — `onOpenChange` / `isLoading` / `emptyLabel` 추가, 빈 목록 자동 비활성 제거, 빈 상태 렌더, `aria-busy` 래퍼
- 수정 `src/shared/ui/popup/popup.css` — `width: min(var(--app-mobile-max), calc(100% - 2rem))`
- 수정 `src/features/meeting-reservation/model/types.ts` — `ReservationOptionField` 추가
- 수정 `src/features/meeting-reservation/ui/MeetingReservePage.tsx` — `loadingFields`, `onThemeOptionsOpen`, `onDateOptionsOpen`, `onTimeSlotOptionsOpen`, `EMPTY_OPTION_LABELS`, `openTrigger`
- 수정 `src/pages/meeting-reservation/ui/MeetingReserveRoute.tsx` — 옵션을 빈 배열로 시작해 열림 시 채우는 미리보기, 날짜 변경 시 슬롯 무효화
- 수정 `src/features/meeting-reservation/ui/MeetingReservePage.test.tsx` — 검증 2건 추가

## Key Logic
- **열림만 전달**: `openTrigger(onOpen)`은 `isOpen === true`일 때만 콜백을 호출한다. 닫힘은 전달하지 않아 소비자가 매 열림·닫힘마다 조건문을 쓰지 않는다.
- **조회 중 목록 비우기**: `const visibleItems = isLoading ? [] : items;` — 예약 날짜를 바꾼 뒤 이전 슬롯 목록이 잠시 노출되는 것을 어댑터 차원에서 막는다.
- **비활성 조건 변경**: `isDisabled={disabled ?? false}`. 이전 `disabled || items.length === 0`은 지연 로딩의 첫 열림 자체를 막았다. "선택 가능한 항목 없음"은 이제 열린 목록 안의 문구(`role="status"`)로 표현한다.
- **`aria-busy` 위치**: HeroUI `Select.Trigger`는 props를 RAC `Button`으로 넘기고 RAC가 DOM 속성을 필터링해 `aria-busy`가 렌더되지 않았다(테스트로 확인). 감싸는 `div.dropdown-field`에 표시했다.
- **팝업 폭**: `dialog`는 top layer라 `#root` 셸 밖에서 그려진다. 폭 상한을 셸 토큰으로 직접 고정했다.

## Validation / Request Handling
- `npx vitest run src/features/meeting-reservation` → 2 files / 10 tests 통과
- `npm run lint` → 통과
- `npm run build` (`tsc -b && vite build`) → 통과. 중간에 `exactOptionalPropertyTypes: true` 위반(TS2375, `isDisabled: boolean | undefined`)이 나와 `disabled ?? false`로 수정했다.
- `npm run test` → 503 passed / 6 failed. 실패 6건은 전부 `citizen-participation` 투표 API·MSW·라우트 테스트로 직전 세션과 동일한 목록이며, 이번 변경 파일과 import 연결이 없다.

## Risks
- 기존 실패 6건이 `sy-main` 기준선에서도 재현되는지는 여전히 미확인이다(확인에 사용자 전용 Git 명령 필요).
- 팝업 폭 변경은 `ReportPopup`에도 적용된다. 브라우저 렌더는 확인하지 않았다(정책상 시각 QA는 사용자 요청 시에만).
- 미리보기의 `setTimeout` 지연 로딩은 요청 취소·경합 처리가 없다. 빠르게 여닫으면 늦게 도착한 결과가 덮어쓸 수 있다. 실제 hook에서는 취소가 필요하다.

## Handoff Note
- Ready for watcher review
