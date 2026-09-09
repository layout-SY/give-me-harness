# Review Log

## Review Target
`task/reserve-option-lazy-load`의 working tree 변경 7건 (`git -C … diff -- src` + untracked `src/shared/ui/dropdown/dropdown.css`)

## Result
- pass

## Checklist Review
- SKILL compliance: 승인된 branch scope(`src/features/meeting-reservation`, `src/pages/meeting-reservation`, `src/shared/ui/dropdown`, `src/shared/ui/popup`) 안에서만 변경했다. UI 역할 경계 준수 — API 호출·파싱·도메인 검증을 UI 파일에 넣지 않았고, 실제 조회는 props 계약으로 열어 두었다. `@heroui/react` import는 어댑터 내부에만 있다. 새 색 토큰 없음, 뷰포트 분기 없음(`DESIGN.md` 고정 모바일 셸 계약 준수).
- Reuse check: 새 라이브러리를 넣지 않고 HeroUI/RAC가 이미 노출하는 `onOpenChange`와 `renderEmptyState`를 사용했다. 스타일은 기존 토큰만 참조한다.
- Validation check: `npx vitest run src/features/meeting-reservation`(10 passed), `npm run lint`(통과), `npm run build`(통과), `npm run test`(503 passed / 6 failed — 기존 실패와 동일 목록).
- Payload completeness: 요구된 A·B·C·D가 모두 반영됐다. 필드별 열림 콜백 3종, `loadingFields`, `emptyLabel`, 팝업 폭 모두 확인.
- Performance concern: `openTrigger`가 렌더마다 새 함수를 만들지만 대상은 드롭다운 3개이고 `Select`는 memo 경계가 아니다. 영향 없음.
- Duplicate code concern: 드롭다운 3곳의 prop 배선이 반복되나 직전 세션 `grill-me-review.md`의 판단(사용처 4번째에서 `ReservationSelectField` 추출)을 그대로 유지했다. 반복 폭이 3줄 늘었으므로 추출 시점 판단 근거를 `evaluation-log.md`에 갱신했다.

## Violations
1. (리뷰 중 수정) 빈 상태 문구에 `role="status"`를 붙였으나, RAC가 빈 상태를 `role="option"`(`react-aria-components/dist/private/ListBox.mjs:222`)으로 감싸므로 listbox 옵션 안에 live region이 중첩되는 구조였다. 제거하고 래퍼의 `aria-busy`만 남겼다.
2. (구현 중 수정) `Select.Trigger`에 `aria-busy`를 전달했으나 RAC가 DOM 속성을 필터링해 렌더되지 않았다. `div.dropdown-field`로 옮겼다.
3. (구현 중 수정) `isDisabled={disabled}`가 `exactOptionalPropertyTypes: true`에서 TS2375로 실패했다. `disabled ?? false`로 수정했다.

## Required Fixes
1. 없음

## 확인이 필요한 판단 (차단 아님)
1. 빈 목록의 표현이 "비활성 컨트롤"에서 "열리는 빈 목록 + 문구"로 바뀐다. 지연 로딩의 전제 조건이지만 UX 변화이므로 사용자 확인 대상이다.
2. 팝업 폭 변경이 `citizen-participation`의 `ReportPopup`에도 적용된다. 브라우저 렌더는 확인하지 않았다.
3. `npm run test`의 기존 실패 6건이 `sy-main`에서도 재현되는지는 여전히 미확인(사용자 전용 Git 명령 필요).

## Repeat Issue
- false

## Escalation
- none
