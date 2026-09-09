# 탐색 — 예약 상세 UI

## 읽은 정책

- `.agent-policy/common/skills/policy/task-role-routing/SKILL.md`
- `.agent-policy/common/skills/policy/task-role-routing/references/ui.md`

## 재사용 자산 (`src/shared/ui`)

| 자산 | 확인 내용 | 상세에서의 사용 |
| --- | --- | --- |
| `status/status-badge.tsx` | tone 6종(`positive`/`neutral`/`warning`/`danger`/`info`/`muted`), 빈 라벨은 `-` 렌더 | 상태 배지 |
| `button/button.tsx` | `className`으로 variant 결정(`primary`/`danger`/`outline`…), `fullWidth` 기본 true | 예약 취소, 코드 복사 |
| `loading/loading.tsx` | 목록 페이지와 동일한 로딩 표시 | 로딩 분기 |

## 인접 구현

- `ui/layout/ReservationScreen.tsx` — `actionBar` prop이 있으면 하단 고정 바와 여백을 함께 적용.
- `ui/layout/ReservationHeader.tsx` — `onBack`이 있을 때만 `.vo-header__back` 버튼 노출.
- `ui/parts/ReservationCard.tsx` — 상태 6종 유니온과 tone·label 맵을 소유하고 있었음 → 추출 대상.
- `ui/MeetingReservationListPage.tsx` — 로딩·오류·빈 목록 분기 순서와 `{...(prop === undefined ? {} : { prop })}` 전달 관례.
- `ui/parts/meeting-reservation-parts.css` — 모든 `.vo-*` 스타일을 한 파일에 한 줄 규칙으로 모으는 양식.
- `ui/ReservationRestrictedPopup.test.tsx` — `createRoot` + `act` 수동 렌더 테스트 양식.

## 디자인 제약

- `DESIGN.md`: 고정 480px 모바일 셸, 뷰포트 미디어 쿼리 금지, 신규 색 토큰 금지, 12px는 메타데이터 한정.
- `docs/`에 STEP06 화면정의서가 없어 항목 구성은 예약 폼(`MeetingReserveFormValues`)과 목록 카드 필드를 근거로 정했다.
