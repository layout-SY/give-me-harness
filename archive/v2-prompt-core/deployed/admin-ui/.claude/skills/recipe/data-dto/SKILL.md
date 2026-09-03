---
name: recipe-data-dto
description: synthoria-admin-ui에서 신규/수정 API DTO를 설계할 때 따르는 recipe. src/apis 공통 dto(TableApiResponseDto, PaginationDto), 도메인별 *.dto.ts 분리, 생성/수정/목록 쿼리 DTO 규칙, 모달 폼 상태↔payload 매핑을 한 번에 결정해야 할 때 사용. (reference: useApi, policy-validation)
---

# Data DTO (synthoria-admin-ui)

## 언제 이 스킬을 사용하나요?

- 새 API 엔드포인트의 요청/응답 타입을 정의할 때
- 기존 DTO를 화면 요구사항(목록, 상세, 생성, 수정)에 맞게 확장할 때
- 테이블 응답 구조(`content`, `count`, `pagination`)를 맞춰야 할 때
- 생성/수정 통합 모달의 폼 상태를 API payload DTO로 매핑할 때

---

## 선행 reference 확인 체크리스트

이 recipe를 따르기 전에 아래 reference 문서들을 먼저 읽고 계약을 숙지한다.

- [ ] [reference/custom-hooks/use-api/SKILL.md](../../reference/custom-hooks/use-api/SKILL.md) — `execute<T>` 제네릭과 `api.<domain>.<method>` 타이핑이 DTO와 어떻게 결합되는지
- [ ] [reference/custom-hooks/useFetchAdapter/SKILL.md](../../reference/custom-hooks/useFetchAdapter/SKILL.md) — `TableApiResponseDto<TItem, TCount>` 형식 요구사항
- [ ] [recipe/data-fetch/SKILL.md](../data-fetch/SKILL.md) — DTO 변경이 fetch 흐름과 어떻게 맞물리는지 (선·후 작업 영향)
- [ ] [policy/validation/SKILL.md](../../policy/validation/SKILL.md) — 폼 → payload 매핑 시 검증 책임 경계

> DTO만 단독으로 변경되는 일은 거의 없다. 위 reference·recipe와의 결합을 인지한 상태에서만 수정한다.

---

## 0) DTO 파일 위치 규칙

### 기본 원칙

- 도메인 DTO는 `src/apis/${domain}/${domain}.dto.ts`에 정의
- 공통 테이블/페이지네이션 DTO는 `src/apis/dto.ts` 사용
- 중첩 도메인도 동일 규칙:
  - `src/apis/event/attendance/attendance.dto.ts`
  - `src/apis/event/roulette/roulette.dto.ts`
  - `src/apis/dao/nft/nft.dto.ts`

### 작업 순서

1. 기존 도메인 DTO 파일 확인
2. 재사용 가능한 타입(`*ListItemDto`, enum/union, 공통 베이스 타입) 우선 탐색
3. 새 타입 추가 후 `*.api.ts` 시그니처 반영
4. 호출부(페이지/모달/훅)에서 타입 정합성 확인

---

## 1) 공통 DTO 구조 (`src/apis/dto.ts`)

프로젝트의 목록 API 기본 표준:

- `PaginationDto`
  - `page`, `pageCount`, `itemCount`
- `TableApiResponseDto<S, T = TableItemAmountCountDto>`
  - `content: S[]`
  - `count: T`
  - `pagination: PaginationDto`

추가 카운트 타입:

- `TableItemAmountCountDto`
- `TableCountDto<TKey>`
- DAO 전용 카운트:
  - `TableDaoProposalListCountDto`
  - `TableDaoProposalReviewListCountDto`

DTO 설계 시 목록 응답은 반드시 이 공통 구조를 재사용한다.

---

## 2) 도메인 DTO 네이밍 규칙

### 권장 네이밍

- 생성 요청: `CreateXxxDto`
- 수정 요청: `UpdateXxxDto` 또는 `PatchXxxDto`
- 목록 쿼리: `GetXxxListDto`
- 목록 아이템: `GetXxxListItemDto` 또는 `GetXxxListResponseDto`
- 상세 응답: `GetXxxResponseDto` / `GetXxxDetailResponseDto`
- 업로드 요청: `UploadXxxDto`

### 프로젝트 내 실제 패턴 반영

간단한 나열형은 `type`, 구조를 가진 타입이면 `interface`

- 예:
  - export type USER_TYPE = "ACTIVE" | "SUSPENDED"
  - export interface GetXxxListDto { id : number ; ... ;}

원칙:

- **DTO는 PascalCase 사용**
- 만약 기존 파일에서 PascalCase를 사용하지 않았더라도 무시하고 사용. 단, PascalCase를 사용하지 않은 기존 인터페이스는 건들지 말 것.

---

## 3) DTO 설계 기준 (요청/응답 분리)

### 3-1. 요청 DTO

- 생성 DTO: 필수 필드 중심
- 수정 DTO: `Partial<CreateXxxDto>` 또는 선택 필드 명시
- 쿼리 DTO: 필터 필드(keyword, tab)는 optional, `page/size`는 명시

예시 패턴:

- `items`: `CreateItemDto`, `UpdateItemDto = Partial<CreateItemDto>`, `GetItemListDto`
- `users`: `GetUserListDto`, `GetUserDeviceLogsDto`
- `dao`: `GetDaoProposalsQueryDto`, `UpdateDaoProposalQueryDto`

### 3-2. 응답 DTO

- 목록과 상세 응답을 분리한다
- 목록에서 필요 없는 대용량 필드는 제외(`Omit`) 가능
- 상태/카테고리/액션 값은 string literal union 또는 enum으로 명확히 제한

예시:

- `GetItemListResponseDto = Omit<ItemDto, "description">`
- `DaoProposalStatus`, `DaoProposalReviewStatus`, `DaoDiscussionStatus`

---

## 4) 테이블 응답 DTO 규칙

목록 API는 아래 중 하나를 사용:

1. 공통 표준
   - `Promise<TableApiResponseDto<RowDto, CountDto>>`
2. 레거시/도메인 특화 응답
   - `GetXxxResponseDto` 내부에 `content/pagination` 포함

권장:

- 신규 목록 API는 공통 `TableApiResponseDto` 우선
- `count`가 단일 숫자가 아니면 별도 `CountDto`로 확장

예:

- DAO 제안 목록: `TableApiResponseDto<GetDaoProposalsListItemDto, TableDaoProposalListCountDto>`
- NFT Pass 목록: `TableApiResponseDto<NftPassPolicyManagementItemListDto>`

---

## 5) 생성/수정 통합 모달과 DTO 매핑

### 모달 구조와 DTO 연결

생성/수정 통합 모달은 보통:

- `formState` (UI 상태)
- `initFormState` (dirty-check 기준)
- `CreateXxxDto` / `UpdateXxxDto` payload 변환

대표: `src/pages/manage/items/_id.modal.tsx`

매핑 원칙:

1. 폼 상태 타입은 API DTO와 1:1 고정하지 말고 `Partial` 조합 허용
2. 저장 직전에 payload DTO로 명시적 변환
3. 수정은 dirty 필드만 전송하는 전략을 우선 고려

예:

- `FormStateTypes = Partial<ItemDto> & Partial<CreateItemDto>`
- 저장 시 `CreateItemDto` 또는 `UpdateItemDto`로 변환

---

## 6) 파일 업로드 DTO 규칙

### 업로드 타입

- multipart 업로드는 API 시그니처에서 `FormData` 또는 `UploadXxxDto` 사용
- 현재 프로젝트는 빈 인터페이스 placeholder가 일부 존재:
  - `uploadItemImageDto`
  - `UploadEventAttendanceConfigImageDto`

권장:

- 신규 DTO는 placeholder 대신 실제 구조를 명시
- 다만 기존 API가 `FormData`를 직접 받는다면 호출부에서 `FormData` 생성 유지

### 업로드 응답 DTO

- 문자열 URL 반환인지, 객체 반환인지 명확히 분리
- 예:
  - DAO 이미지 업로드: `string`
  - 아이템 이미지 업로드: `{ uuid: string }` 형태 사용

---

## 7) 타입 설계 체크리스트

1. `any` 금지 (불가피하면 임시 주석으로 이유 명시)
2. union으로 상태값 제한 (`status`, `type`, `action`)
3. `page/size` 타입 누락 금지
4. 날짜 필드는 문자열 포맷 기준(ISO)으로 일관
5. 목록/상세/생성/수정 DTO 분리
6. 응답이 테이블이면 `TableApiResponseDto` 재사용 검토
7. API와 UI 명칭 불일치 시 변환 레이어를 두고 DTO 자체를 왜곡하지 않기
8. 현재 enum으로 정의되어 있는 타입/값이 일부 존재. 기존에 있는 건 건드리지 않지만, 이후 선택자들은 dto.ts에 type 정의 후 ${domain}.constants.ts 파일에 as const 값으로 별도 정의 요망

---

## 8) 실전 구현 절차 (프롬프트)

아래 순서로 DTO 작업:

1. 엔드포인트 목적 분류:
   - list / detail / create / update / delete / upload
2. 요청 DTO 정의:
   - `GetXxxListDto` 또는 `CreateXxxDto` 등
3. 응답 DTO 정의:
   - 목록이면 `RowDto + TableApiResponseDto` 우선
4. 상태값 타입화:
   - dto.ts에 type 정의 후 ${domain}.constants.ts 파일에 as const 값으로 별도 정의 요망
5. `*.api.ts` 함수 시그니처 반영
6. 화면 컴포넌트(목록/모달)에서 payload 매핑 적용
7. 타입 에러/린트 확인 후 누락 필드 점검

---

## 9) 빠른 템플릿

```ts
import { PaginationDto, TableApiResponseDto } from "~/apis/dto";

export type ResourceStatus = "ACTIVE" | "INACTIVE";

export interface GetResourceListDto {
  page: number;
  size: number;
  keyword?: string;
  status?: ResourceStatus;
}

export interface ResourceListItemDto {
  id: number;
  name: string;
  status: ResourceStatus;
  createdAt: string;
}

export type GetResourceListResponseDto = TableApiResponseDto<ResourceListItemDto>;

export interface CreateResourceDto {
  name: string;
  status: ResourceStatus;
}

export type UpdateResourceDto = Partial<CreateResourceDto>;

export interface GetResourceDetailResponseDto extends ResourceListItemDto {
  description?: string;
}
```

---

## 10) 주의사항

- 기존 DTO가 불완전하거나 네이밍이 혼재되어 있어도, 한 번에 전면 리네이밍하지 않는다
- 변경 범위 API와 직접 연결된 DTO만 최소 단위로 개선한다
- 모달 폼 상태 타입과 서버 DTO를 강제로 동일시하지 않는다 (UI 전용 필드 분리)
- `src/apis/dto.ts` 공통 타입을 중복 정의하지 않는다
