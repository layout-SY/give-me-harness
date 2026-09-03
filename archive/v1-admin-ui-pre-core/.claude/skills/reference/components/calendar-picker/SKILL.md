---
name: component-calendar-picker
description: synthoria-admin-ui의 CalendarPicker 사용 가이드. 날짜/기간 선택이 필요한 요구사항에서 pubsub 기반으로 사용.
---

# Calendar Picker Component

## 대상

- `src/components/calendar-picker/calendar-picker.tsx`
- pubsub 이벤트: `open-calendar-picker`, `close-calendar-picker`

## 언제 선택하나

- 시작일/종료일 선택 UI가 필요한 경우

## 사용 핵심

- `open-calendar-picker` 이벤트
  - 해당 이벤트의 payload는 `callback` 계약을 지킨다.
- callback에서 선택 결과를 페이지 form state로 반영한다.
- `isAutoSelectOneWeek`을 pubsub로 활성화 하면 startDate 선택 시 자동으로 7일 후가 endDate로 설정된다.

## 기능

- 첫 렌더링 시 시작 날짜는 오늘 날짜로 설정된다.
- 헤더엔 월/연도를 선택하거나 좌우 화살표를 클릭하여 이동할 수 있다.
- 메인 컨텐츠인 날짜 선택에선 시작/종료 날짜 선택 시 그 사이에 날짜들이 선택된 스타일로 적용된다.

## 주의

- 날짜 문자열 포맷은 기존 유틸(`formatDateToLocalTimezone`)과 일관되게 처리한다.

## 수정(리팩토링) 주의

- 현재 자동 날짜 선택은 7로 고정되어 있다.
