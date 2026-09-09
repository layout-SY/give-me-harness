# Exploration

## Target Paths
- `src/shared/ui/dropdown/dropdown.tsx`, `src/shared/ui/popup/popup.css`, `src/shared/ui/popup/popup.responsive.css`
- `src/features/meeting-reservation/**`, `src/pages/meeting-reservation/ui/MeetingReserveRoute.tsx`
- `src/index.css`(토큰 확인, 읽기 전용), `DESIGN.md`
- `node_modules/@heroui/react/dist/components/select`, `node_modules/react-aria-components`, `node_modules/react-stately`(계약 확인, 읽기 전용)

## Existing Reusable Assets Found
- Found: `react-stately`의 Select 상태 계약 — `onOpenChange?: (isOpen: boolean) => void` (`react-stately/dist/types/src/select/useSelectState.d.ts:39`)
  - Suggested Reuse: HeroUI `Select`가 `AriaSelectProps`를 그대로 상속하므로(`@heroui/react/dist/components/select/select.d.ts:8`) 어댑터에서 prop 하나만 전달하면 열림 이벤트를 얻는다.
  - Reason: 새 상태 관리나 외부 의존성 없이 지연 로딩 트리거를 만들 수 있다.
- Found: `ListBox`의 `renderEmptyState` (`react-aria-components/dist/types/src/ListBox.d.ts:72`)
  - Suggested Reuse: 로딩·빈 목록 문구를 목록 안에서 렌더한다.
  - Reason: 별도 오버레이나 스피너 컴포넌트를 만들지 않아도 되고 팝오버 안에서 스크린리더에 읽힌다.
- Found: `--app-mobile-max`(`src/index.css:29`), `--text-muted`, `--space-2/3`
  - Suggested Reuse: 팝업 폭과 빈 상태 문구 스타일에 그대로 사용.
  - Reason: `DESIGN.md`가 기능별 자체 픽셀값 대신 `--app-mobile-max` 참조를 요구한다(`DESIGN.md:98`).

## Assets Not Suitable for Reuse
- Asset: `src/shared/ui/loading/loading.tsx`
  - Why not suitable: `position: absolute`로 컨테이너 전체를 덮는 오버레이라, 팝오버 목록 안의 인라인 로딩 문구로 쓰기 어렵다.
- Asset: `src/shared/ui/no-results/no-results.tsx`
  - Why not suitable: 높이 200px에 아이콘을 포함한 목록 전용 빈 화면이라 드롭다운 팝오버에는 과도하다.
- Asset: `Select.Trigger`의 `aria-busy` 전달
  - Why not suitable: HeroUI `SelectTrigger`가 props를 RAC `Button`으로 넘기고 RAC가 DOM 속성을 필터링해 `aria-busy`가 렌더되지 않았다(테스트에서 `null` 확인). 감싸는 `div.dropdown-field`에 표시하는 방식으로 대체했다.

## New Asset Necessity
- Needed: `src/shared/ui/dropdown/dropdown.css`
  - Why: 빈 상태 문구와 래퍼 폭을 위한 최소 스타일이 필요하고, 기존 dropdown 디렉터리에는 스타일 파일이 없었다. 새 색 토큰은 추가하지 않고 기존 토큰만 참조한다.
- Needed: `ReservationOptionField` 타입 (`src/features/meeting-reservation/model/types.ts`)
  - Why: `loadingFields`와 빈 문구 매핑이 같은 필드 집합을 공유해야 하며, 문자열 리터럴을 페이지·라우트 양쪽에 중복 선언하지 않기 위해서다.

## 확인된 제약
- 기존 `Dropdown`은 `isDisabled={disabled || items.length === 0}`이라 목록이 비면 열리지 않는다. 지연 로딩에서는 첫 열림 전 목록이 비어 있으므로 이 조건이 기능을 원천 차단한다.
- `dialog`는 top layer에 그려져 `#root`의 `min(480px, 100%)` 셸 밖에 놓인다. 따라서 팝업 폭 `min(600px, …)`은 데스크톱 폭에서 셸보다 넓어진다.
- `Dropdown` 소비자는 `MeetingReservePage` 1곳, `Popup` 소비자는 `ReserveCompletePopup`과 `citizen-participation/ui/report/ReportPopup` 2곳이다(변경 영향 범위 확인).
