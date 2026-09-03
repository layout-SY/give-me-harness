# Page Components Guide

## 1) 페이지 컴포넌트 배치 패턴 (`src/pages/**`)

### 대표 구조

- `index.tsx`: 페이지 엔트리
- `_id.modal.tsx`, `create.modal.tsx`: 상세/생성 모달
- `*.popup.tsx`: 팝업 보조 액션
- `widgets/`: 대시보드/프로필 카드 단위
- `modules/`: 이벤트/폼 단계별 블록
- `components/sections/`: 특정 도메인 상세 화면 조각

예시:

- `src/pages/dashboard/widgets/*.widget.tsx`
- `src/pages/manage/events/attendance/_id/modules/*.module.tsx`
- `src/pages/dao/proposal-manage/detail/components/sections/*.tsx`

---

## 2) 페이지 전용으로 유지해야 하는 경우

아래 중 하나라도 해당되면 페이지 폴더에 둔다.

1. `useApi` 호출과 DTO 매핑이 핵심
2. `usePubSub` 이벤트(`read-*`, `refresh-*`)에 강결합
3. 라우트/모달 상태(`MODAL_STATES`, id param)에 강결합
4. 해당 도메인 enum/상수를 광범위하게 참조

---

## 3) 페이지 컴포넌트 표준 패턴

### Fetch/State 패턴

- `const { api, execute } = useApi();`
- `isLoading`, `formState`, `initFormState`, `dirtyStateSet` 조합
- 저장 시 confirm -> API -> success alert -> refresh 이벤트 발행

### Modal 패턴

- 열기/닫기: `usePubSub` 이벤트 기반
- 수정 모드: `READ/UPDATE` 또는 `CREATE/READ/UPDATE`
- 취소 시 dirty-check 후 confirm

### Widget 패턴

- `useEffect` 마운트 시 fetch
- 로딩 중 `Loading`
- 에러 플래그 별도 관리(`isError`)

---

## 4) 공용 컴포넌트와의 경계

페이지 컴포넌트는 아래를 사용해 조합한다:

- 입력: `TextInput`, `Dropdown`, `IconButton`, `Button`
- 리스트: `Table`, `Pagination`, `NoResults`
- 모달: `CustomModal`, `SideModal`, `Popup`
- 보조: `Loading`, `ImageModal`, `CalendarPicker`

원칙:

- 공용 컴포넌트는 "UI 계약"
- 페이지 컴포넌트는 "비즈니스 조립"

---

## 5) 새 페이지 컴포넌트 작성 절차

1. 대상 페이지 폴더에서 기존 파일 구조(`modules/widgets/components`)를 먼저 따른다.
2. 내부 UI는 공용 컴포넌트를 우선 조합한다.
3. fetch/이벤트 로직은 페이지 전용 컴포넌트 또는 페이지 로컬 훅으로 캡슐화한다.
4. 사용자 노출 텍스트는 한글로 직접 작성한다.
5. 완료 후 목록 갱신 이벤트(`refresh-*`) 및 모달 close 흐름까지 확인한다.

---

## 6) 리팩터링 승격 기준 (Page -> Common)

아래 조건이 충족되면 공용으로 이동을 검토한다.

1. 동일 패턴이 최소 2개 도메인에서 반복됨
2. props화가 가능하고 도메인 종속성 제거 가능
3. 이동 후 호출부 복잡도가 감소함

승격하지 않는 편이 나은 경우:

- 재사용 빈도가 낮고 props가 과도하게 복잡해지는 경우
- 도메인 용어/로직이 강해 공용화가 오히려 가독성을 낮추는 경우
