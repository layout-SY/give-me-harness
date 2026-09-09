# Plan

## Request Summary
- 사용자 요청: 프로젝트의 meeting 관련 서비스 내용을 파악하고, 화면정의서 `VO_V2_STEP02_M01_VO_MEETING_RESERVE_MOBILE`(회의 예약 모바일)과 `VO_V2_STEP03_P01_VO_RESERVE_COMPLETE_POPUP`(예약 신청 완료 팝업) 두 화면의 UI 작업만 먼저 진행.
- 확인된 역할: ui (inject `--role ui`). Git 통합 담당자: claude. 산출물 책임: owner.
- 사용자 결정 사항: ① 라우트는 "최소 연결"로 포함 ② `sy-main`에서 분기.

## Work Type
- feature (신규 UI 슬라이스 생성)

## Scope
- `src/features/meeting-reservation/**` — 신규 feature 슬라이스(model/types, ui/layout, ui/parts, 화면 2종, CSS 2종, 테스트 2종)
- `src/pages/meeting-reservation/**` — 라우트 컴포넌트(미리보기 연결)
- `src/shared/config/meetingReservationRoutes.ts` — 라우트 상수
- `src/app/routing.ts` — `/meeting/reserve` 등록
- `.claude/logs/sessions/2026-09-04-meeting-reserve-ui/**` — 산출물

## Out of Scope
- 예약 API·DTO·파서, 폼 검증 로직, 슬롯 점유·승인 상태 전이 → Logic 역할 인계
- 나머지 15개 화면(STEP04~STEP24)
- `src/features/meeting/**`(Agora RTC 회의 진행 기능) 수정
- 시각 QA·캡처(사용자 요청 없음)

## Sections
1. 화면정의서 2건 분석(텍스트 추출 + 페이지 렌더 확인)
2. 재사용 자산 조사 — `src/shared/ui/**`, `src/features/citizen-participation/ui/**`, `DESIGN.md`
3. feature 슬라이스 신설 및 화면 2종 구현(controlled props 계약)
4. `/meeting/reserve` 최소 라우트 연결
5. 테스트 작성 후 `npm run lint` / `npm run build` / `npm run test` 검증

## Required Agents
- 없음. UI 역할 단독 수행(하위 에이전트 미사용).

## Required Skills
- `policy/task-role-routing`(ui reference), `policy/git-branch-strategy`, `policy/documentation`
- `frontend-design` — 신규 화면이므로 적용. 다만 화면정의서와 `DESIGN.md`가 시각 방향을 고정하므로 "브리프가 방향을 고정하면 브리프를 따른다" 규칙에 따라 기존 토큰·패턴을 재현.

## Risks / Assumptions
- 예약 도메인이 기존 `src/features/meeting`(RTC)과 성격이 달라 별도 슬라이스로 분리 — 후속 15개 화면도 같은 슬라이스에 누적된다는 전제.
- 화면정의서에 지정 참여자 "제거" 컨트롤이 없어 UX 공백이 있음. 최소 크기의 제외 버튼을 추가하고 사용자 확인 대상으로 남김.
- `src/shared/ui/dropdown`은 index 기반 API라 value↔index 변환이 페이지에 필요.
- `src/index.css`가 승인 scope 밖이므로 새 전역 색 토큰을 추가하지 않고 `color-mix`로 기존 `--accent` 파생.

## Approval Request
이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?
