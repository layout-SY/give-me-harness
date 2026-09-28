# 계획

## 목표

Figma `가상오피스` 페이지의 관리자(ADM) 프레임을 FSD 구조에 맞춰 UI만 구현한다. 데이터는 Figma 표시값을 추론한 임시 요청/응답 DTO와 fixture로 채우고, controller·API는 연결하지 않는다.

## 작업 유형

- publish-only (UI 역할)

## 범위

| Figma | 화면 | 경로 |
| --- | --- | --- |
| A01 `10:5588` | 대시보드 | `/vo/dashboard` |
| A02 `10:4042` · A03 `10:4181` | 예약 관리 목록 · 상세 | `/vo/reservations`, `/vo/reservations/:reservationId` |
| P09 `10:4306` · P10 `10:4399` | 승인 확인 · 반려사유 팝업 | 예약 상세 안에 포함 |
| A04 `10:4492` | 회의실 일정 | `/vo/room-schedule` |
| A05 `10:5758` | 실시간 이용 현황 | `/vo/live-sessions` |
| A06 `10:5898` | 패널티 관리 | `/vo/penalties` |
| A07 `10:6036` · A08 `10:6167` | 이용 이력 목록 · 상세 | `/vo/meeting-histories`, `/vo/meeting-histories/:historyId` |

- entity: `src/entities/vo` (공통 어휘 `as const`, 영역별 도메인 타입, 임시 DTO, fixture, 표시 formatter)
- pages: `vo-dashboard`, `vo-reservation`, `vo-room-schedule`, `vo-live-session`, `vo-penalty`, `vo-meeting-history`
- app: `vo-admin-shell.tsx`, `routes.tsx`의 `/vo` 라우트
- widgets: `_navigation6.ts`, `buildVirtualOfficeNavigationItems`

## 제외 사항

- A09 이용 통계, A10 운영이력 (사용자 지시)
- 모바일·클라이언트·3D 프레임
- API client, parser, query hook, controller, zod 스키마

## 제약 조건 (사용자 확정)

- 메뉴: 대시보드, 예약 관리, 회의실 일정, 실시간 이용 현황, 패널티 관리, 이용 이력
- 상태 값은 `as const`. "캠핑/우주/호텔"은 테마가 아니라 회의실(`roomId`/`roomName`)
- 표는 `shared/ui/table/table.tsx` 사용
- 회의실 일정: 09:00~20:00 전체 시간 슬롯. 안내문 영역까지 그래프를 늘려 약 4행이 보이고 내부 스크롤
- 실시간 이용 현황: 회의실 3개 고정. 회의실 선택 → API 응답으로 참여자 현황 채움(Logic 연결 예정)
- 이용 이력: 로그형 테이블 나열 + 상세 페이지 필요
- 작업 branch: `feature/vo-admin-ui` (sy-main `6efd8ab`에서 생성)

## 스킬 및 역할

- 제안 역할: UI (inject `--role ui`)
- 역할 판단 근거: 화면 구조·표현 계약 구현, API·controller 미연결
- 사용자 역할 확인: inject role
- 승인할 Git 작업: branch 생성(완료). commit은 별도 승인 필요
- 산출물 책임: owner

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| entity 어휘·DTO·fixture | UI | task-role-routing | Logic이 이어받을 임시 계약 |
| page view·popup·CSS | UI | frontend-design | 기존 cp 토큰·공용 컴포넌트 재사용 화면 |
| 라우트·셸·메뉴 | UI | - | `/vo/*` 진입 |

## 검증

- `npm run lint`, `npm run build`

## 위험 요소 및 결정 사항

- 계획의 entity 6개는 FSD 동일 레이어 교차 import 금지로 회의실 등 공통 어휘를 공유할 수 없어 단일 `entities/vo`로 통합했다.
- 최종 이용결과 Enum은 Figma에서도 미확정이라 `string | null`로 유지한다.
- 패널티 "제한기간 변경"의 새 종료시각 입력 UI는 Figma에 없어 DTO 선택 필드로만 둔다.

## 승인

- 상태: approved (사용자 "이대로 작업 진행")
