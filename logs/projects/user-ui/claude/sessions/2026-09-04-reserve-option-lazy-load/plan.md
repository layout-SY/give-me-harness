# Plan

## Request Summary
- 사용자 요청: "예약 옵션 지연 로딩 작업 진행" (2026-09-04)
- 근거 계약: `task/reserve-option-lazy-load` branch 목적 + 직전 세션 `2026-09-04-meeting-reserve-ui/handoff.md`의 A·B·C 항목
- 원 사용자 요구(이전 세션 기록): "사용자가 해당 입력폼에 입력을 원할 때(select라면 select 목록이 뜰 때) API 요청으로 현재 사용 가능한 데이터들이 뜨게끔 할 것."

## Work Type
- feature (UI 계약 확장)

## Scope
- A. `src/shared/ui/popup/popup.css`: `dialog.custom-popup` 폭을 고정 모바일 셸 토큰에 맞춘다.
- B. `src/shared/ui/dropdown/dropdown.tsx`(+ `dropdown.css` 신설): 열림 이벤트·로딩·빈 목록 계약을 어댑터에 추가한다.
- C. `src/features/meeting-reservation`: `MeetingReservePage`에 필드별 열림 콜백과 `loadingFields` props를 추가한다.
- D. `src/pages/meeting-reservation`: TEMPORARY 미리보기를 "열릴 때 조회" 방식으로 바꿔 로딩·빈 상태를 실제로 확인할 수 있게 한다.
- 테스트: `MeetingReservePage.test.tsx`에 빈 목록·로딩 표시 검증 추가.

## Out of Scope
- 실제 예약 API 호출, 요청 취소·캐시·재시도 (Logic 역할)
- 예약 날짜 변경 시 슬롯 무효화의 도메인 책임 (Logic 역할, 미리보기 흉내만 구현)
- 참여자 닉네임 자동 검색 디바운스, `organizationName` 초기화·검증
- 브라우저 시각 QA (정책상 사용자 요청 시에만)

## Sections
1. A 팝업 폭 전역 수정
2. B 드롭다운 어댑터 계약 확장
3. C 페이지 props 계약과 배선
4. D 미리보기 라우트 지연 로딩 전환
5. 테스트 추가 후 lint·build·test 검증

## Required Agents
- 없음. 단일 세션에서 UI 역할로 직접 구현한다.

## Required Skills
- `policy/task-role-routing`(ui reference), `policy/git-branch-strategy`, `policy/documentation`
- `frontend-design` 미적용: 신규 화면이 아니라 기존 화면의 상태 표현 추가이며 `DESIGN.md` 토큰만 사용한다.

## Risks / Assumptions
- `isDisabled`에서 `items.length === 0` 조건을 제거하면 "옵션 없음"의 표현이 비활성 컨트롤에서 열리는 빈 목록으로 바뀐다. 지연 로딩에서는 첫 열림 전 목록이 항상 비므로 이 변경이 전제 조건이다.
- 팝업 폭 변경은 전역이라 `citizen-participation`의 `ReportPopup`에도 적용된다. `DESIGN.md`의 고정 모바일 셸 계약과 같은 방향이라 의도된 변경으로 본다.
- HeroUI `Select`가 하위 `react-stately`의 `onOpenChange`를 그대로 노출한다는 전제(확인: `react-stately/dist/types/src/select/useSelectState.d.ts:39`).

## Approval Request
이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?

- 사용자 승인: "작업 진행" (2026-09-04). D 포함 여부를 함께 물었고 조정 요청 없이 승인되어 A~D 전부 수행했다.
