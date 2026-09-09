# 최종 요약

## 제공 사항

Figma STEP04 `VO_RESERVATION_RESTRICTED_POPUP`(node `10:3687`)의 신규 예약 제한 안내 팝업 UI와 회귀 테스트.

- `ReservationRestrictedPopup` 컴포넌트: 경고 아이콘, 제목, 제한 사유, 제한 범위 안내 박스, 허용 범위 안내 박스, 확인 버튼
- 문구 4종(`reason`, `restrictionScope`, `note`, `allowedDescription`)을 optional props로 노출하고 Figma 값을 기본값으로 제공
- 확인 버튼은 `onConfirm ?? close` — Figma 정의 04행의 "Popup 닫기 · 추가 화면 이동 없음"과 일치

## 변경 이유

STEP02·STEP03이 `sy-main`에 반영된 뒤 다음 프레임인 STEP04만 미구현 상태였다. 사용자가 다음 프레임 UI 작업을 요청했다.

## 재사용한 자산

`~/shared/ui/popup`, `~/shared/ui/button/button`, `ui/parts/NoticeBox`, `.vo-complete*` CSS, `--danger` / `--danger-bg` 토큰.

## 영향 영역

- `src/features/meeting-reservation/ui/ReservationRestrictedPopup.tsx` (신규)
- `src/features/meeting-reservation/ui/ReservationRestrictedPopup.test.tsx` (신규)
- `src/features/meeting-reservation/ui/parts/meeting-reservation-parts.css` (4줄 추가)
- `src/features/meeting-reservation/index.ts` (export 1줄 추가)

기존 화면의 동작은 바뀌지 않는다. 추가된 CSS는 `.vo-restricted`가 붙은 요소에만 적용된다.

## 제외 사항

- 제한 상태 사전 검사(API 조회, 168시간 남은 기간 계산, 재검사): Logic 역할
- 라우트·진입점 연결: 진입 화면 STEP01(로비 NPC)이 미구현
- 공용 아이콘 승격: 사용처가 하나이고 `src/shared/assets/icons`가 승인 scope 밖

## 검증

| 명령어 | 결과 |
| --- | --- |
| `npm run lint` | 통과 |
| `npm run build` | 통과 |
| `npx vitest run src/features/meeting-reservation/ui/ReservationRestrictedPopup.test.tsx` | 5/5 통과 |
| `npm run test` | 524/530 통과. 실패 6건은 `citizen-participation` MSW 관련 사전 존재 실패로 이번 변경과 무관 |

## 산출물

`.claude/logs/sessions/2026-09-08-ui-37fd2a2f/` — `plan.md`, `exploration.md`, `implementation-log.md`, `grill-me-review.md`, `review-log.md`, `evaluation-log.md`, `final-summary.md`, `portfolio-log.md`

## 알려진 제한

- 팝업이 아직 어떤 화면에서도 렌더되지 않아 실사용 검증은 STEP01 연결 이후에 가능하다.
- `168시간`이 정적 문구다. 실제 남은 시간 표기는 호출부가 계산해 `restrictionScope`로 넘겨야 한다.
- 전체 테스트에 사전 존재 실패 6건이 남아 있다.

## 다음 단계

1. 사용자 승인 후 `sy-main`으로 merge (`finish-proposal` → `finish` → `verify` → `close`)
2. Logic 역할: 제한 상태 조회 API·hook과 사전 검사 분기 구현
3. UI 역할: STEP01 로비 NPC 화면 구현 시 이 팝업 연결
