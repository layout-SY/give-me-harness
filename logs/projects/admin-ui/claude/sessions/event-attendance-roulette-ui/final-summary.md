# 출석·룰렛 이벤트 관리 UI 결과

## 제공 사항

- `/events/*`용 `EventAdminShell`과 이벤트 메뉴(`_navigation7`), 기존 `_navigation2` 경로 `/events/*` 수정.
- `shared/ui/tabs` HeroUI Tabs 어댑터.
- `widgets/event-admin`: 기본 정보 필드, 환경 설정 목록(이미지 썸네일 클릭 교체·크게 보기 / 텍스트 일괄 저장), 아이템 이름 검색 팝업, objectId 입력 필드, 보상 가져오기 바, 저장 바, 상세 레이아웃(헤더·요약·3탭), 요약.
- 출석: 목록 View, 등록 View, 상세 View, 보상 편집기(월간 캘린더 ↔ 일차 목록 전환, 날짜 클릭 SideModal 편집, ACC 누적 보상 별도 영역).
- 룰렛: 목록·등록·상세 View, chance 비율 SVG 도넛 휠 + 보상 표(행·조각 강조 연동).
- 모든 View는 controller props 계약(types)으로만 동작. 새 의존성·색상 토큰 없음.

## 결정

- 캘린더는 외부 라이브러리 대신 dayjs 기반 grid 계약(일정 드래그·시간축 불필요). 셀에 칩 2개 + `+N`, 편집은 SideModal.
- 휠은 SVG 직접 구현, chance 합계 0이면 같은 크기로 표시.
- 설정 키 type 표는 사용자 승인 후 프런트 상수로 고정.

## 검증

- lint 통과, build 통과, 이벤트 관련 테스트 24 pass.
- 브라우저 시각 검증 미실행. controller·routes 미구현으로 화면 렌더 확인 불가.

## 미완료·다음

- Logic 인계: `handoff.md` (controller·payload·routes). 확인 필요 5건은 사용자 답변으로 확정해 "추가 확정 사항"에 반영(2026-09-17). 응답에 없는 설정 키는 화면 미표시·PATCH 제외로 확정(서버가 고정 키 상수를 그대로 응답).
- Git: `dad057f`(UI 40개 파일) → `9b50fda`(활성 여부 수정) → `aae0ba7`(화면 표시 개선·chance 경고) → `bbb16dc`(sy-main 동기화, JSX·CSS 6개 충돌 해결) 후 `2b9ca35`로 sy-main 통합. 병합 후 lint·build 통과. push·정리 미실행.

## 2026-09-21 후속 작업

- 화면 조정: 환경 설정 이미지(키 좌상단·중앙 정렬·원본 배경), 보상 행 2줄 분리와 버튼 겹침 해결, 아이템 이름 표시, 캘린더 칩(이름+n개, 축소), 룰렛 도넛 100 기준 채움.
- chance 합계 100 초과 경고를 controller까지 구현(사용자 승인으로 통합 구현 범위 확장). 저장은 막지 않는다.
- DateRangePicker: 추가한 클래스 이름이 HeroUI `.date-range-picker`와 충돌해 입력이 세로로 쌓였다. `date-range-picker-group`으로 바꿔 해결했다.
- sy-main의 아이템 검색 Table 전환·접근성 연결은 보존하고, 중복된 `itemName` props는 확정 계약 `objectName`으로 통일했다.
- 실제 브라우저 렌더링 확인은 사용자 쪽에서 수행한다.
