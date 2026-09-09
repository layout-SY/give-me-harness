# 탐색

## 요청

사용자: "이걸로 figma mcp 연결해봐" → "다음 프레임 ui 작업 진행하면 돼" → "브랜치 전환해서 작업하고, 격리 워크트리 생성해서 작업해. 나머진 계획대로 진행"

TalkToFigma MCP 채널 `05j3cbcu`에 접속해 문서 `가상오피스`를 조회하고, 이미 구현된 STEP02·STEP03 다음 프레임인 STEP04의 UI를 구현한다.

## 조사 대상 경로

- Figma: 문서 `가상오피스`(page `0:1`), 프레임 `VO_V2_STEP04_P04_VO_RESERVATION_RESTRICTED_POPUP`(`10:3687`)
- `src/features/meeting-reservation/**`
- `src/pages/meeting-reservation/**`
- `src/shared/ui/popup/popup.tsx`, `src/shared/ui/button/button.tsx`
- `src/index.css`(디자인 토큰)

## 현재 코드와 인접 구현의 사실

- `sy-main`(HEAD `466567aee847`)에는 STEP02 `MeetingReservePage`, STEP03 `ReserveCompletePopup`, STEP05 `MeetingReservationListPage`와 `api/`·`hook/`·`model/` 계층이 이미 있다. STEP04 제한 안내 팝업만 없다.
- `ReserveCompletePopup`은 `Popup` + `custom-popup-content vo-complete` 컨테이너 + `NoticeBox` 2개 + `Button className="primary"` 구조다. 제목을 `aria-labelledby`로 연결하고 아이콘 `span`에 `aria-hidden="true"`를 준다.
- `NoticeBox`는 `title` / `emphasis?` / `description` / `tone: "tint" | "outline"` 계약이다. STEP04의 상태 박스(라벨·값·주석)와 허용 박스(제목·설명)에 그대로 대응한다.
- `Popup`은 `showModal`, Escape 처리, backdrop 클릭 닫기를 이미 담당한다.
- `Button`은 `className` 문자열을 HeroUI variant로 매핑한다. `primary`가 기본 확인 버튼이다.
- `src/index.css`에 `--danger: #b42318`, `--danger-bg: #fee4e2`, `--danger-border: #f4a7a1`가 이미 정의되어 있다.
- `src/shared/assets/icons`에 느낌표(경고) 아이콘은 없다. `block.icon`, `info.icon`은 의미가 다르다.

## Figma 프레임 계약 (scan_text_nodes 결과)

| 요소 | 문구 |
| --- | --- |
| 아이콘 | `!` |
| 제목 | 현재 새 회의 예약을 신청할 수 없습니다. |
| 사유 | No-show로 신규 예약 신청이 제한 중입니다. |
| 상태 라벨/값 | 제한 범위 / 신규 예약 신청 · 168시간 |
| 상태 주석 | 제한 중 다시 No-show가 발생하면 제한 종료시각이 갱신됩니다. |
| 허용 제목/설명 | 기존 이용은 가능합니다 / 기존 승인완료 예약 · 초대받은 회의 · 코드 참여 |
| 버튼 | 확인 (Popup 닫기 · 추가 화면 이동 없음) |

우측 정의 4행에서 확인한 동작: 로비 NPC의 회의 예약 선택 시 제한 상태를 사전 검사하고, 제한이면 M01 대신 이 팝업을 띄운다. 확인 버튼은 상태·기간을 바꾸지 않는다.

## 불러온 스킬

- `policy-task-role-routing`(`SKILL.md`, `references/ui.md`)
- `policy-git-branch-strategy`
- `policy-documentation`

## 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| `src/shared/ui/popup` | 재사용 | modal·Escape·backdrop 처리가 이미 있고 STEP03과 동일 패턴 |
| `src/shared/ui/button/button` | 재사용 | `primary` variant가 확인 버튼 요구와 일치 |
| `ui/parts/NoticeBox` | 재사용 | title/emphasis/description/tone 계약이 두 박스에 그대로 대응 |
| `.vo-complete*` CSS | 재사용 | 팝업 골격(아이콘 원형·텍스트·버튼 높이)이 STEP03과 동일 |
| `--danger` 계열 토큰 | 재사용 | 경고 톤에 필요한 색이 이미 정의됨 |

## 재사용하지 않은 후보와 이유

- `src/shared/ui/dialog`, `src/shared/ui/modal`: STEP03이 `popup`을 쓰고 있어 같은 계열을 유지하는 편이 일관적이다.
- `block.icon` / `info.icon`: 각각 금지·정보 의미로, Figma의 경고(`!`) 표현과 다르다.

## 새 자산 필요 여부와 근거

- 경고 SVG 1개가 필요하다. 현재 사용처가 이 팝업 하나뿐이고 승인 scope가 `src/features/meeting-reservation`이므로 공용 아이콘으로 승격하지 않고 컴포넌트 파일 안에 인라인 상수로 둔다.
- 새 색상·디자인 토큰은 추가하지 않는다.

## 성능·의존성 영향

- 새 런타임 의존성 없음. 추가 번들은 SVG path 1개와 CSS 4줄 수준이다.

## 제약 조건 및 미확인 사항

- 제한 상태 조회 API와 남은 기간 계산 계약이 아직 없다. UI는 optional props로만 노출한다.
- 진입 화면(STEP01 로비 NPC)이 미구현이라 실제 라우트 연결 지점이 없다.

## 결론

STEP04는 STEP03과 동일한 팝업 골격에 문구·강조색만 다른 화면이다. `Popup`·`Button`·`NoticeBox`·`.vo-complete` CSS를 그대로 재사용하고, 경고 아이콘과 danger 톤 오버라이드만 새로 만든다.
