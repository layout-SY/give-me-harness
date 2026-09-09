# Exploration

## Target Paths
- `src/shared/ui/` (button, text-input, text-area, dropdown, popup, status, tabs, date-range-picker)
- `src/features/meeting/**` (기존 meeting 도메인 성격 확인)
- `src/features/citizen-participation/ui/**` (동일한 모바일 폼 화면 패턴)
- `src/app/routing.ts`, `src/shared/config/citizenParticipationRoutes.ts`
- `DESIGN.md`, `src/index.css` (토큰), `docs/meeting-architecture.md`
- `docs/design/가상오피스/가상오피스/*.pdf` (화면정의서 17종, 이번 대상 2종)

## Existing Reusable Assets Found
- Found: `src/shared/ui/button/button.tsx` (HeroUI 어댑터, `className`으로 variant 매핑)
  - Suggested Reuse: 예약 신청 CTA, 참여자 검색·추가·팝업 확인 버튼
  - Reason: 프로젝트의 유일한 버튼 진입점이며 variant·로딩·비활성 상태를 이미 제공
- Found: `src/shared/ui/text-input/text-input.tsx`, `text-area/text-area.tsx`
  - Suggested Reuse: 팀/기업명, 회의명, 닉네임 검색, Agenda
  - Reason: InputGroup 한 겹 테두리·clear 버튼·`error` 데이터 속성이 화면정의서 필드 형태와 일치
- Found: `src/shared/ui/dropdown/dropdown.tsx`
  - Suggested Reuse: 테마 / 예약 날짜 / 1시간 시간 슬롯
  - Reason: 화면정의서의 세 필드 모두 `▾` 단일 선택 트리거로 표현됨
- Found: `src/shared/ui/popup/*`
  - Suggested Reuse: 예약 신청 완료 팝업
  - Reason: `<dialog>` + backdrop 클릭·ESC·모션 감소 처리가 이미 구현됨
- Found: `src/features/citizen-participation/ui/layout/*`, `parts/FieldGroup.tsx`, `citizen-layout.css`
  - Suggested Reuse: 구조·클래스 명명·토큰 규칙을 그대로 참고
  - Reason: 동일한 고정 모바일 셸 + sticky 하단 CTA + 카드형 폼 패턴
- Found: `src/shared/assets/icons/chevron-left.icon.tsx`, `check.icon.tsx`
  - Suggested Reuse: 헤더 뒤로가기, 완료 팝업 체크 마크

## Assets Not Suitable for Reuse
- Asset: `src/features/citizen-participation/ui/layout/CitizenScreen.tsx` 등 CP 레이아웃 컴포넌트를 직접 import
  - Why not suitable: FSD상 feature 간 직접 의존이 되고, 해당 파일은 다른 작업 범위의 소유물이다. 동일 구조를 `vo-` 접두사로 예약 슬라이스 안에 재구성했다. 두 슬라이스에서 안정화되면 `src/shared/ui`로 승격을 제안한다.
- Asset: `src/shared/ui/date-range-picker`
  - Why not suitable: 화면정의서의 예약 날짜는 범위가 아닌 단일 값 드롭다운이다.
- Asset: `src/shared/ui/status/status-badge.tsx`
  - Why not suitable: 완료 팝업의 "승인대기"는 Chip 배지가 아니라 tint 카드 안의 강조 텍스트로 표현된다.
- Asset: `src/features/meeting/**`
  - Why not suitable: Agora RTC 회의 "진행" 기능으로 예약 도메인과 책임이 다르다. `.meeting-app` 범위 토큰도 공유하지 않는다.

## New Asset Necessity
- Needed: `src/features/meeting-reservation/` 신규 슬라이스
  - Why: 예약 흐름(STEP02~STEP24)에 해당하는 화면이 저장소에 전혀 없고, 기존 meeting 슬라이스는 RTC 세션 전용이다.
- Needed: `ReservationScreen` / `ReservationHeader` / `BottomActionBar` / `ReservationField` / `SegmentedChoice` / `ParticipantPicker` / `NoticeBox`
  - Why: `src/shared/ui`에 셸·헤더·세그먼트 컨트롤·참여자 선택·안내 박스에 해당하는 어댑터가 없다. 세그먼트 컨트롤은 CP의 `ChoiceGroup`(찬반 투표용 체크 마크 포함)과 시각·의미가 달라 재사용할 수 없었다.
