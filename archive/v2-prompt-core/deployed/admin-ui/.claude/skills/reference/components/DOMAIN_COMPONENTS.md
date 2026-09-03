# Domain Shared Components Selection Guide

## 목적

이 문서는 특정 도메인(DAO/Activity/Dashboard) 내부에서 재사용되는 컴포넌트를
요구사항에 맞게 선택하기 위한 가이드다.

> 선택 후에는 반드시 `components/domain/<component>/SKILL.md`를 읽고 구현한다.

---

## 1) DAO 도메인

### 작성자/카테고리/상태 뱃지

- `AuthorBadge` -> `domain/dao-author-badge/SKILL.md`
- `CategoryBadge` -> `domain/dao-category-badge/SKILL.md`
- `StatusBadge` -> `domain/dao-status-badge/SKILL.md`

적합한 요구사항:
- DAO 제안/토론/심사 화면의 메타 정보 라벨 표시

### 제안 이미지 슬롯

- `ImageSlots` -> `domain/dao-image-slots/SKILL.md`

적합한 요구사항:
- 제안 이미지 다중 추가/삭제/미리보기(편집/조회 모드 분리)

### PASS 전용 드롭다운

- `PassDropdown` -> `domain/dao-pass-dropdown/SKILL.md`

적합한 요구사항:
- PASS 관리/리워드 화면의 타입 선택 드롭다운

---

## 2) Dashboard 도메인

### 파이 차트

- `PieChart` -> `domain/dashboard-pie-chart/SKILL.md`

적합한 요구사항:
- 디바이스 비율/분포 시각화

---

## 3) Activity 도메인

### 타일/라벨/마커

- `TileComponent` -> `domain/activity-tile-component/SKILL.md`
- `LabelComponent` -> `domain/activity-label-component/SKILL.md`
- `MarkerComponent` -> `domain/activity-marker-component/SKILL.md`

적합한 요구사항:
- 활동 맵에서 타일 렌더, 위치 라벨, 사용자 수 마커 표시

---

## 4) 공통 주의사항 (완성도 이슈)

도메인 전용 공용 컴포넌트도 완성도가 충분하지 않을 수 있다.

허용:
1. 페이지/도메인 CSS에서 세부 스타일 보강
2. 기존 컴포넌트를 감싸는 얇은 래퍼 추가
3. 필요한 최소 props 확장

금지:
1. 기존 도메인 화면을 깨는 대규모 시그니처 변경
2. 도메인 상수 체계를 무시한 처리
