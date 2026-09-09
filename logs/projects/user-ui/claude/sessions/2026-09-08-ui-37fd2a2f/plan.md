# 계획

## 목표

Figma `VO_V2_STEP04_P04_VO_RESERVATION_RESTRICTED_POPUP`(node `10:3687`)의 신규 예약 제한 안내 팝업을 UI 컴포넌트로 구현하고 회귀 테스트를 추가한다.

## 작업 유형

- feature

## 범위

- `src/features/meeting-reservation/ui/ReservationRestrictedPopup.tsx` 신규
- `src/features/meeting-reservation/ui/ReservationRestrictedPopup.test.tsx` 신규
- `src/features/meeting-reservation/ui/parts/meeting-reservation-parts.css` 규칙 추가
- `src/features/meeting-reservation/index.ts` export 추가
- `.claude/logs/sessions/2026-09-08-ui-37fd2a2f/` 산출물

## 제외 사항

- 제한 상태 사전 검사(API 조회, 168시간 남은 기간 계산, 재검사 정책): Logic 역할 경계
- 라우트·진입점 연결: 진입 화면인 STEP01 로비 NPC가 아직 미구현이라 연결 지점이 없음
- `src/shared/assets/icons`에 새 공용 아이콘 추가: 승인 scope 밖이며 현재 재사용처가 이 팝업 하나뿐

## 제약 조건

- 새 색상·디자인 토큰을 만들지 않고 `--danger`, `--danger-bg` 등 기존 토큰만 사용한다.
- 기존 `ReserveCompletePopup`의 마크업·접근성 패턴과 동일한 구조를 유지한다.
- 격리 worktree `/Users/okand/SynologyDrive/asan-worktrees/reservation-restricted-popup`에서 작업한다.

## 스킬 및 역할

- 제안 역할: ui
- 역할 판단 근거: inject `--role ui`. 작업이 마크업·CSS·접근성·props 계약에 한정된다.
- 사용자 역할 확인: "나머진 계획대로 진행" (2026-09-09)
- Git 통합 담당자: claude
- 산출물 책임: owner (`ASAN_ARTIFACT_RESPONSIBILITY=owner`)

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| Figma 프레임 조회 | ui | TalkToFigma MCP | 텍스트·구조 계약 확보 |
| 재사용 자산 탐색 | ui | policy-task-role-routing / references/ui.md | Popup·Button·NoticeBox 재사용 결정 |
| 팝업 구현 | ui | — | `ReservationRestrictedPopup.tsx` |
| 테스트 | ui | — | 문구·접근성·콜백 회귀 테스트 |
| 검증 | ui | — | lint·build·test 통과 |

## 검증

- `npm run lint`
- `npm run build`
- `npm run test`

## 위험 요소 및 결정 사항

- 제한 사유·기간 문구가 Figma 하드코딩 값이다. 향후 Logic이 계산값을 넘길 수 있도록 전부 optional props로 노출하고 Figma 문구를 기본값으로 둔다.
- 경고 아이콘을 공용 아이콘으로 승격하지 않고 컴포넌트 안에 인라인한다. 재사용처가 늘면 `src/shared/assets/icons`로 승격을 제안한다.
- 계획 시점에 branch scope의 산출물 경로를 `.claude/logs/sessions/2026-09-09-reservation-restricted-popup`으로 잡았으나, 이 세션의 launcher 바인딩 경로는 `.claude/logs/sessions/2026-09-08-ui-37fd2a2f`다. `scope-proposal` → `update-scope`로 실제 세션 경로에 맞췄다(SHA `f6df81e7d4d13fbe47f557a653b6a685c398a48f52f00d58340047bb944f8d5a`, 사용자 승인 2026-09-09).

## 승인

- 상태: approved
- 필수 문구: `이 역할과 계획대로 진행할까요, 아니면 조정할 부분이 있나요?`
- 사용자 응답: "브랜치 전환해서 작업하고, 격리 워크트리 생성해서 작업해. 나머진 계획대로 진행"
