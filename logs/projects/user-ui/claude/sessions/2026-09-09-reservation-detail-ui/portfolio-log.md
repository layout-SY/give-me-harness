# 포트폴리오 로그 — 예약 상세 UI

## 사용자 요구

이전 세션에서 합의된 계획 그대로, STEP06 예약 상세 모바일 화면을 신규 구현한다. 취소 권한 판정·승인만료 전이·참여 코드 발급은 Logic 경계이므로 UI는 `canCancel: boolean`과 표시 문자열만 props로 받는다.

## 문제 근거

- 예약 목록 카드(`ReservationCard`)가 예약 상태 6종 유니온과 tone·label 맵을 파일 내부에 갖고 있어, 같은 상태를 표시해야 하는 상세 화면이 정의를 복제해야 하는 상태였다.
- 상세 화면이 없어 목록 카드의 `onSelect` 이동 대상이 비어 있었다.
- `docs/`에 STEP06 화면정의서가 없고 Figma 채널이 만료되어, 항목 구성 근거를 저장소 안에서 찾아야 했다.

## 검토한 대안과 선택

| 결정 | 대안 | 선택과 이유 |
| --- | --- | --- |
| 상태 계약 위치 | (a) 상세에서 복제 (b) `model/reservation.ts`로 이동 (c) UI 공용 모듈로 추출 | (c). (a)는 두 화면이 어긋난다. (b)는 model이 아직 4종만 정의해 Logic 경계 변경이 필요하고 UI 역할 범위를 넘는다. (c)는 UI 표시 계약만 한곳에 모으면서 기존 export 이름을 별칭으로 유지해 목록 import를 건드리지 않는다 |
| 취소 버튼 노출 판정 | (a) 상태값으로 UI가 판정 (b) `canCancel` boolean 수신 | (b). 취소 정책(상태 조건·시간 조건)은 서버·Logic 소유이며 UI가 규칙을 복제하면 정책 변경 시 두 곳을 고쳐야 한다 |
| 상세 정보 마크업 | (a) `<table>` (b) `<ul>` + span (c) `<dl>` | (c). 용어-설명 쌍이라는 의미가 시맨틱과 일치하고 화면 낭독 순서가 자연스럽다. 그리드 정렬을 위해 `dl > div > dt/dd` 구조를 썼다 |
| 값이 빈 항목 | (a) "-" 표시 (b) 줄 생략 | (b). 480px 고정 셸에서 의미 없는 줄이 화면을 밀어내지 않도록 했고, 항목이 전부 비면 섹션 제목도 그리지 않는다 |

## 실제 구현

`parts/reservationStatus.ts`(상태 6종 + tone·label + 라벨 해석 함수), `parts/ReservationDetailSection.tsx`(제목 + `<dl>`), `ui/MeetingReservationDetailPage.tsx`(controlled 화면), `.vo-detail*` CSS, `index.ts` export, 테스트 9케이스.

## 기술의 구체적 목적

- `useId`: 섹션 제목 id를 렌더 인스턴스마다 유일하게 만들어 `aria-labelledby` 중복을 막는다.
- `overflow-wrap: anywhere` + `white-space: pre-wrap`: 긴 안건·참여자 목록이 480px 셸에서 가로 스크롤을 만들지 않도록 한다.
- 옵셔널 prop 전개(`{...(x === undefined ? {} : { x })}`): `exactOptionalPropertyTypes` 환경에서 `undefined` 전달을 피하는 기존 코드베이스 관례를 따랐다.
- `StatusBadge` 톤 재사용: DESIGN.md에 없는 색을 새로 만들지 않기 위한 제약 준수.

## 검증 결과

- 신규 테스트 9개 통과, feature 디렉터리 24개 통과.
- `npm run lint`, `tsc -b`, `npm run build` 통과.
- 전체 테스트 533 passed / 6 failed — 실패는 `citizen-participation`의 MSW `onUnhandledRequest` 관련 기존 실패로, 실패 목록을 확인해 이번 변경과 무관함을 근거로 남겼다.

## 후속 피드백

- 사용자가 Figma 채널을 제공하지 않아 디자인 대조는 미실행 상태로 합의하고 진행했다.
- 세션 도중 자체 검토에서 참여 코드 섹션의 하드코딩 id를 발견해 `useId`로 교체했다.
