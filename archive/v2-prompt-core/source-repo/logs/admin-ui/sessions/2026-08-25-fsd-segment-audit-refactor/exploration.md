# 탐색 기록

## 대상 경로
- src/ARCHITECTURE.md
- src/app, src/pages, src/widgets, src/features, src/entities, src/shared
- src/pages/cp-survey, src/entities/cp-survey

## 발견한 기존 재사용 자산
- 발견 항목: 레이어 단방향(app→pages→widgets→features→entities→shared)은 대체로 지켜진다. CP pages는 entity public API를 사용한다. `widgets/admin-page-layout`과 `features/cp-status-transition`은 슬라이스 배럴이 있다.
- 재사용 제안: 세그먼트 표준을 `cp-survey`에 먼저 적용한 뒤 동일 패턴 CP 슬라이스에 복제한다.
- 근거: ARCHITECTURE.md 슬라이스 세그먼트 규칙과 refactoring 정책의 “한 범위씩” 원칙.

## 재사용이 어려운 자산
- 자산: 전 도메인 일괄 폴더 이동
- 부적합 사유: 범위 불명확 대규모 수정 금지, 레거시 엔티티는 소비 페이지 생성 시 배럴 정비가 후속으로 명시되어 있다.

## 신규 자산 필요성
- 필요 항목: 없음. 파일 이동과 배럴 경로 수정만 한다.
- 필요 이유: 관심사 분리이지 새 추상화가 아니다.
