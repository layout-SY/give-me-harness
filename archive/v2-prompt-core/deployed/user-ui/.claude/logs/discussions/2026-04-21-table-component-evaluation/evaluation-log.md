# evaluation-log.md

## Stage
- Agent: evaluator
- Date: 2026-04-21
- Target: `src/components/table/`
- Status: recommendation_ready

---

## Diagnosis

### 1. 시스템 플로우
`useFetchAdapter`가 fetch·상태관리·행 변환(mapRow)을 단일 훅에서 처리.
재조회 트리거가 `requestSearch` boolean 플래그 반전 방식으로, `searchState` 변경 시
`requestTableValues` 참조가 교체되어 `useEffect`가 연속 실행될 여지가 있다.

- 관련 위치: `hooks/useFetchAdapter.ts:26-49`
- **리스크: Medium**

### 2. 코드 구성
`interface/apiTableRowInterface.ts`가 도메인별 Row 인터페이스
(`DaoGetProposalsTableRow`, `ManageUsersTableRow` 등 12개 도메인)를
공용 테이블 폴더 내에 집중 보관. 도메인 DTO를 직접 import하는 역방향 의존성.
`TableHeader` 인터페이스는 프로젝트 전체에서 미사용(dead code).

- 관련 위치: `interface/apiTableRowInterface.ts:1-3`, `:102-105`
- **리스크: High**

### 3. 관심사 분리
`utils/commonCell.tsx`가 `pages/dao/` 레이어의 컴포넌트
(AuthorBadge, StatusBadge, CategoryBadge)를 직접 import.
`columnDef.ts`의 `CellValueMap`에 `DaoAuthorDto`, `DaoProposalCategory` 하드코딩.
`useFetchAdapter`가 내부 구현 상태(`setIsLoading`, `fetchedData`)를 외부에 노출.

- 관련 위치: `utils/commonCell.tsx:2-6`, `interface/columnDef.ts:26-33`, `hooks/useFetchAdapter.ts:60`
- **리스크: High**

### 4. 인터페이스 설계
- (긍정) discriminated union 기반 `TableColumnDef<TRow>`, mapped type `AccessorColumn<TRow, TType>` 설계 우수
- (문제) `ActionColumn`의 `type`이 `"open_detail"` 리터럴만 허용 → 추가 action 시 interface 수정 필요
- (문제) `CellValueMap`에 DAO 도메인 타입 고착
- (문제) `Pagination` 컴포넌트의 `handler: Function` 약타입 → type-safety 경계에서 단절

- 관련 위치: `interface/columnDef.ts:64-68`, `interface/columnDef.ts:26-33`
- **리스크: Medium**

### 5. 훅 설계
- `console.log(data)` 가 프로덕션 코드에 잔류 → 10개 이상 테이블 페이지에서 API 응답 전체 콘솔 출력
- 에러 상태(`isError`) 미노출 → 소비처가 fetch 실패 감지 불가
- `mapRow` inline 전달 시 매 렌더마다 `rows` useMemo 재실행
- `requestSearch` 플래그 방식으로 소비처에 암묵적 재조회 계약 강제

- 관련 위치: `hooks/useFetchAdapter.ts:31`, `:37-39`, `:51-53`
- **리스크: High**

### 6. 코드 퀄리티
- `table.tsx:86` row key로 배열 인덱스 사용 → 정렬/페이지네이션 시 잘못된 reconciliation 위험
- `table.tsx:146-158` NoResults 이중 렌더링 경로 존재
- `table.tsx:88-89` `resolveRowNumber` 동일 인자로 두 번 호출
- `proposal-manage/index.tsx`와 `history/_id.modal.tsx`에 vote-progress 셀 로직 copy-paste 중복
- `pass-management/index.tsx:348` `console.log` 잔류
- `history/_id.modal.tsx:60-66` 수동 number 컬럼 재구현 (Table 내장 index 컬럼과 중복)

- **리스크: Medium**

### 7. 성능 / 유지보수 / 확장성
- `columns` 배열이 소비처 함수 바디에서 매 렌더마다 새로 생성 (useMemo 없음)
- sticky 컬럼이 최대 2개 고정 (`--synthoria-table-secondary-sticky-right` 하드코딩 3.75rem)
- `apiTableRowInterface.ts` 변경 빈도 높음 (도메인 추가마다 수정 필요)

- **리스크: Medium**

---

## Architectural Risks

- 공용 `components/table/`이 `pages/dao/` 도메인 컴포넌트를 직접 역참조 (`commonCell.tsx`)
- 공용 `table/interface/`가 도메인 Row 타입을 집중 보관 (`apiTableRowInterface.ts`)
- `useFetchAdapter` 내부 구현 상태(`setIsLoading`, `fetchedData`)가 외부에 노출되어 캡슐화 훼손
- `requestSearch` boolean 플래그 방식의 재조회 트리거 → 소비처 12곳에 암묵적 계약
- `console.log`가 프로덕션 훅과 페이지에 잔류

---

## Improvement Options

1. **cellRendererRegistry 패턴**: `commonCell.tsx`의 도메인 렌더러를 외부 등록 방식으로 분리
2. **Row 타입 이전**: `apiTableRowInterface.ts`의 도메인 Row 타입을 각 feature 폴더로 이전 후 파일 삭제
3. **useFetchAdapter 반환 타입 정제**: 내부 setter 미노출, `isError` 추가
4. **mapRow 참조 안정화**: `searchState` 변경에 반응하는 파생 `useMemo` 분리, 소비처 가이드 수립
5. **row key 위임**: `getRowKey` prop으로 소비처가 안정적 key를 제공하도록 변경

---

## Recommended Backlog

### 즉시
1. `useFetchAdapter.ts:31` `console.log(data)` 제거
2. `pass-management/index.tsx:348` `console.log` 제거

### 단기
3. `apiTableRowInterface.ts` 도메인 Row 타입 → 각 feature 폴더로 이전
4. `commonCell.tsx` `pages/dao/` 직접 import 해소 (registry 패턴 or slot prop)
5. `useFetchAdapter` 반환 인터페이스 정제 (`setIsLoading`/`fetchedData` 제거, `isError` 추가)

### 중기
6. row key 안정화 (`getRowKey` prop)
7. NoResults 이중 렌더링 단일 경로로 통일
8. `resolveRowNumber` 중복 호출 변수 캐싱
9. `history/_id.modal.tsx` 수동 number 컬럼 제거
10. `TableHeader` dead code 제거

### 장기
11. `ActionColumn` 다중 타입 지원 확장 설계
12. sticky 컬럼 동적 오프셋 계산 로직 도입

---

## Optional Handoff
- to planner: true
- 사유: 항목 3·4·5는 소비처 12개 파일 import 경로 변경 및 columnDef.ts 타입 변경이 수반되어 단계적 계획 필요

---

## Suggested Next Step

console.log 제거 2건(즉시 항목)을 단독 작업으로 먼저 처리 후,
`apiTableRowInterface.ts` 이전 → `commonCell.tsx` 도메인 분리 → `useFetchAdapter` 정제 순서로
planner 에이전트에 계획을 이관한다.
