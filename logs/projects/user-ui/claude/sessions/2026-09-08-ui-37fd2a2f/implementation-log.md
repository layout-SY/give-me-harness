# 구현 로그

## 승인된 범위

- branch: `task/reservation-restricted-popup` (V3, parent `sy-main`, merge target `sy-main`, role `ui`, integrator `claude`)
- 격리 worktree: `/Users/okand/SynologyDrive/asan-worktrees/reservation-restricted-popup`
- scope: `src/features/meeting-reservation`, `.claude/logs/sessions/2026-09-08-ui-37fd2a2f`

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `src/features/meeting-reservation/ui/ReservationRestrictedPopup.tsx` | 신규. `Popup` + `NoticeBox` 2개 + `Button`으로 STEP04 팝업 구성. 문구 4종을 optional props로 노출하고 Figma 값을 기본값으로 둠 | 완료 |
| `src/features/meeting-reservation/ui/ReservationRestrictedPopup.test.tsx` | 신규. 5개 테스트(기본 문구, props 대체, `aria-labelledby`, `onConfirm`, `close` 폴백) | 5/5 통과 |
| `src/features/meeting-reservation/ui/parts/meeting-reservation-parts.css` | `.vo-restricted__icon`, `.vo-restricted .vo-notice--tint` 등 4줄 추가 | 완료 |
| `src/features/meeting-reservation/index.ts` | `ReservationRestrictedPopup` export 추가 | 완료 |

## 재사용한 자산과 새로 만든 자산

- 재사용: `~/shared/ui/popup`, `~/shared/ui/button/button`, `ui/parts/NoticeBox`, `.vo-complete*` CSS, `--danger` / `--danger-bg` 토큰
- 신규: 경고 SVG 인라인 상수 `alertIcon`(컴포넌트 파일 지역), `.vo-restricted*` CSS 4줄

## 핵심 로직·요청 처리

- 이 컴포넌트는 상태를 갖지 않는다. `open`/`close`는 호출부가 소유하고, 확인 버튼은 `onConfirm ?? close`를 호출한다. Figma 정의 04행의 "Popup 닫기 · 추가 화면 이동 없음"과 일치한다.
- 제한 사유·범위·주석·허용 설명은 전부 optional props다. Logic이 제재 종류·남은 시간을 계산해 넘기면 기본값을 덮어쓴다.
- 시각 강조만 danger 톤으로 바꾸기 위해 `.vo-complete`와 `.vo-restricted`를 함께 적용하고, `.vo-restricted` 하위에서 `.vo-notice--tint` 색만 오버라이드했다.

## 결정 사항

- 경고 아이콘을 `src/shared/assets/icons`로 올리지 않았다. 사용처가 하나이고 해당 경로가 승인 scope 밖이다.
- 라우트 연결을 하지 않았다. 진입 화면 STEP01이 미구현이라 연결 지점이 없고, 제한 상태 사전 검사는 Logic 역할이다.
- 새 디자인 토큰을 만들지 않고 기존 `--danger` 계열만 사용했다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `npm run lint` | 통과 (출력 없음) |
| `npm run build` | 통과 (`✓ built in 4.93s`) |
| `npx vitest run src/features/meeting-reservation/ui/ReservationRestrictedPopup.test.tsx` | Test Files 1 passed / Tests 5 passed |
| `npm run test` | 71 파일 중 68 통과, 530개 중 524 통과. 실패 6건은 모두 `src/features/citizen-participation/**`, `src/pages/citizen-participation/**`의 MSW `onUnhandledRequest` 관련 기존 실패로 이번 변경 경로와 무관 |

## 알려진 위험과 제한

- 전체 테스트에 사전 존재 실패 6건이 남아 있다. `citizen-participation` 소유 역할이 별도로 다뤄야 한다.
- 제한 남은 기간(`168시간`)이 정적 문구다. 실제 남은 시간 표기가 필요하면 호출부에서 계산해 `restrictionScope`로 넘겨야 한다.
- 팝업이 아직 어떤 화면에서도 렌더되지 않는다. 실사용 검증은 STEP01 연결 이후에 가능하다.

## 다음 담당자 인계

- Logic 역할: 제한 상태 조회 API·hook과 남은 기간 계산을 구현하고, 로비 NPC 진입 시 사전 검사 → 제한이면 `ReservationRestrictedPopup`, 아니면 `meetingReservationRoutes.reserve` 진입으로 분기한다.
- UI 역할: STEP01 로비 NPC 화면 구현 시 이 팝업을 연결한다.
