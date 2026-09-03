# Implementation Log — FSD 아키텍처 재설계

> 작성일: 2026-07-03
> 기법: `mv`(파일 이동) + `sed`(import 경로 remap) + 개별 `Edit`(주석/구조 변경), 매 단계 `tsc` 게이트.
> 표기: 이동은 `A → B`, 참조 재작성은 `~/old → ~/new`.

---

## S7 — 잔재 도메인 제거 (게이트: 18 → 17)

### 삭제
```
apis/services/ecommerce/        (삭제)
apis/services/videos/           (삭제)
apis/services/parcel/           (삭제)
apis/services/dao/nft/          (삭제)
enums/ecommerce.enum.ts         (삭제)
enums/nft.enum.ts               (삭제)
components/send-parcel/         (삭제 — parcel 유스케이스)
components/table/interface/domain/nftTableRows.ts (삭제)
```

### 유지 도메인의 nft 참조부 주석 처리 (`[nft-removed]`)
- `users/users.dto.ts`: `NFT_TYPES` import, `nftType`, `hasNft`, `NftSummary`, `GetNftUserDetailResponseDto.nftSummary`, `GetNftUserQueryDto`, `GetNftUserItemList` 주석. (유저 상세 타입 자체는 유지, nft 필드만 주석)
- `users/users.api.ts`: `getNftUsers` 엔드포인트 + 관련 import(`TableApiResponseDto`, `DaoProposalStatus`) 주석.
- `dao/table-rows`(구 daoTableRows): `DaoQuestRewardAction` import + `GetDaoQuestRewardTableRow` 인터페이스 주석.
- `table/interface/apiTableRowInterface.ts`: `nftTableRows` 재노출 주석.

### 참조 정리
- `apis/index.ts`: ecommerce·videos·parcel·nft 모듈 import/매핑 제거.
- `hooks/use-pub-sub/events.ts`: video/ecommerce/parcel 이벤트 + `open-send-parcel-popup`(ItemDto·GetUsersResponseDto 의존) 주석.
- `components/navigation/_navigation2.tsx`: video·ecommerce 메뉴 블록 + 미사용 `localShippingIcon` 주석.

**결과**: 잔재 참조(주석 제외) 0. send-parcel 관련 선재 에러 소멸로 18→17.

---

## S0 — 레이어 골격 (게이트: 17 유지)

```
src/{app/{providers,router,styles}, pages, widgets, features, entities,
     shared/{api,lib,ui,config,assets}} 생성
src/ARCHITECTURE.md 작성 (레이어 계약·책임·세그먼트 표준)
```

---

## S1 — shared 확립 (게이트: 17 유지, 중간 store 파손 즉시 교정)

### shared/assets · shared/config
```
assets/icons        → shared/assets/icons
assets/icons.tsx     → shared/assets/icons.tsx
assets/css           → shared/assets/css
assets/i18n          → shared/assets/i18n
assets/constants.ts  → shared/config/constants.ts
remap: ~/assets/icons → ~/shared/assets/icons
       ~/assets/i18n  → ~/shared/assets/i18n
       ~/assets/constants → ~/shared/config/constants
```

### shared/lib (utils·exceptions·hooks·pub-sub)
```
utils               → shared/lib/utils        (~/utils/ → ~/shared/lib/utils/)
exceptions          → shared/lib/exceptions   (~/exceptions/ → ~/shared/lib/exceptions/)
hooks/use-api.tsx   → shared/lib/hooks/use-api.tsx
hooks/use-language.ts → shared/lib/hooks/use-language.ts
hooks/use-pub-sub   → shared/lib/pub-sub
  remap: ~/hooks/use-api → ~/shared/lib/hooks/use-api
         ~/hooks/use-language → ~/shared/lib/hooks/use-language
         ~/hooks/use-pub-sub → ~/shared/lib/pub-sub
  (use-auth.ts는 features/auth용으로 잔류)
```

### shared/config/enums (공통 enum만)
```
common·response-codes·language·currency .enum → shared/config/enums/
  remap: ~/enums/(common|response-codes|language|currency).enum → ~/shared/config/enums/\1.enum
  (도메인 enum은 S3에서 entities로)
```

### shared/ui (전 컴포넌트 일괄 이동)
```
components/*  → shared/ui/*   (일괄 이동으로 상대 sibling import 파손 0)
  remap: ~/components/ → ~/shared/ui/
파손 교정: header/navigation의 `../../store/*` 상대참조 → `~/store/*` 절대화
```

### shared/api (api 인프라)
```
1) apis 내부 상대참조 정규화:
   "(../)+axios.interface" | "./axios.interface" → "~/apis/axios.interface"
   "(../)+common/..."      | "./common/..."      → "~/apis/common/..."
2) 이동:
   apis/api-client.ts     → shared/api/api-client.ts
   apis/axios-instance.ts → shared/api/axios-instance.ts
   apis/axios.interface.ts→ shared/api/axios.interface.ts
   apis/common/           → shared/api/common/
3) remap:
   ~/apis/api-client → ~/shared/api/api-client
   ~/apis/axios-instance → ~/shared/api/axios-instance
   ~/apis/axios.interface → ~/shared/api/axios.interface
   ~/apis/common/ → ~/shared/api/common/
   (apis/index.ts의 ./axios-instance → ~/shared/api/axios-instance)
```

---

## S3 — entities 이관 (게이트: 42 → 17)

### services → entities/<domain>/api (일괄)
```
apis/services/<d>  → entities/<d>/api   (d = 15개 도메인)
item-category 병합:
  apis/services/item-category/item-category.api.ts → entities/items/api/item-category.api.ts
  apis/services/item-category/item.category.dto.ts → entities/items/api/item.category.dto.ts
remap:
  ~/apis/services/item-category/ → ~/entities/items/api/
  ~/apis/services/<d>/           → ~/entities/<d>/api/
```
> 이동 직후 42건(전량 `apis/index.ts` 상대 import 파손) → registry의 import를 `~/entities/<d>/api/...`로 갱신하여 17 복귀. (item-category → `~/entities/items/api/item-category.api`)

### 도메인 enum → entities/<d>/model
```
admin→admin-settings, call→usage, dao→dao, faq→faq, inquiry→inquiries,
item→items, map→maps, news→news, transaction→sales,
user-history→users, user→users
remap: ~/enums/<e>.enum → ~/entities/<d>/model/<e>.enum
enums/ 폴더 제거
```

### store 재배치
```
store/user.store.ts     → entities/users/model/user.store.ts   (~/store/user.store → ~/entities/users/model/user.store)
store/language.store.ts → shared/lib/language.store.ts          (~/store/language.store → ~/shared/lib/language.store)
(auth.store·navigation.store는 S5용 잔류)
```

### dao 분해 판단 → 단일 entity 유지
- 근거: 모든 하위 슬라이스가 `dao/api/shared/shared.dto`(DaoAuthorDto·DaoProposalStatus 등)에 의존하고, `dao.api.ts`가 하위 API를 **조립(aggregate)**해 단일 `daoApi`로 노출. 개별 entity로 쪼개면 satellite→core + aggregator→satellite로 **cross-entity import가 증가**해 오히려 FSD 위반.
- 결정: `entities/dao/{api(내부 세그먼트: banner/discussion/proposal/...), model}` 단일 entity 유지.

---

## S5 — features / widgets 승격 (게이트: 17 → 19 → 17)

```
# features
hooks/use-auth.ts       → features/auth/use-auth.ts
store/auth.store.ts     → features/auth/model/auth.store.ts
shared/ui/select-users  → features/select-users/ui
shared/ui/image-manager → features/image-manager/ui
shared/ui/calendar-picker → features/calendar-picker/ui
# widgets
shared/ui/header        → widgets/app-header/ui
shared/ui/navigation    → widgets/side-navigation/ui
store/navigation.store.ts → widgets/side-navigation/model/navigation.store.ts
# app/router (라우팅 가드)
shared/ui/private-route.tsx    → app/router/private-route.tsx
shared/ui/role-based-route.tsx → app/router/role-based-route.tsx
```
remap: 위 각 경로 `~/shared/ui/... → ~/features|widgets|app/...`, `~/hooks/use-auth → ~/features/auth/use-auth`, `~/store/(auth|navigation).store → ...`

### 파손 교정
- select-users·calendar-picker가 shared/ui 컴포넌트를 `../button` 등 상대참조 → `~/shared/ui/<comp>` 절대화 (내부 `../../types`·`../../utils` 보존).
- `shared/ui/image-slot-item/`: image-manager 내부를 재노출하는 **미사용 배럴** → 삭제(shared→features 위반 겸 dead code).

---

## S4 — api 레지스트리 결합 해소 (게이트: 17 유지)

### entity별 api public singleton 생성
```
entities/<d>/api/index.ts:
  import axiosInstance from "~/shared/api/axios-instance";
  import module from "./<d>.api";
  export const <d>Api = module(axiosInstance);
(items: itemsApi + itemCategoryApi / event: eventAttendanceApi + eventRouletteApi)
```

### useApi 도메인-무지화
- `shared/lib/hooks/use-api.tsx`: `import api from "~/apis"` 제거, 반환에서 `api` 제거 → `{ execute, isLoading }`.

### 소비처 3곳 전환
- `features/select-users`: `api.users.getUsers` → `usersApi.getUsers` (`import { usersApi }`)
- `features/image-manager/.../useImageDelete`: `api.dao.deleteDaoProposalImage` → `daoApi.deleteDaoProposalImage`
- `features/auth/use-auth`: `api.auth.*` → `authApi.*`

### 전역 registry 제거
- `src/apis/` 폴더(및 `apis/index.ts`) 삭제. `~/apis` 참조 0.

---

## S2 — pub-sub 결합 해소 (게이트: 17 유지)

- `shared/lib/pub-sub/index.ts`: `class PubSub<TEvents extends Record<string,any>>` → `<TEvents extends object>` (interface 병합 허용).
- `shared/lib/pub-sub/events.ts`: `type PubSubEvents` → `interface PubSubEvents`. 도메인 타입(`DaoDiscussionStatus`·`CalendarBehaviors`) import 및 해당 이벤트 제거, `[parcel-removed]` 잔여 import 주석 정리.
- **선언 병합으로 도메인 이벤트 재배치**:
  - `features/calendar-picker/ui/pub-sub.events.ts`: `open/close-calendar-picker` (CalendarBehaviors)
  - `entities/dao/model/pub-sub.events.ts`: `open-discussion-comment-detail-modal` + `DiscussionCommentModalRow`(DaoDiscussionStatus)

---

## shared 순수성 마감 (게이트: 17 유지)

- `utils/date.util.ts`: `FreeRangeSelectType`(features) import 제거 → 로컬 `type DayOffsetSelectType = "start"|"end"`.
- `utils/admin-role.util.ts` → `entities/admin-settings/model/admin-role.util.ts` (소비처 app/router·widgets remap).
- table domain interfaces → entities:
  - `shared/ui/table/interface/domain/daoTableRows.ts` → `entities/dao/model/table-rows.ts`
  - `shared/ui/table/interface/domain/userTableRows.ts` → `entities/users/model/table-rows.ts`
  - `shared/ui/table/interface/apiTableRowInterface.ts`: 도메인 재노출 제거, `sharedTableTypes`만 노출.

**결과**: `grep ~/(entities|features|widgets|app)/ src/shared` → 주석 2줄 외 0.

---

## S6 — app 셸 (게이트: 17 → 16)

```
src/main.tsx  → src/app/index.tsx   (./index.css → ./styles/index.css)
src/App.tsx   → src/app/App.tsx      (./App.css → ./styles/App.css)
src/index.css → src/app/styles/index.css
src/App.css   → src/app/styles/App.css
index.html: /src/main.tsx → /src/app/index.tsx
```
> src 최상위 = 순수 레이어(app·pages·widgets·features·entities·shared) + ARCHITECTURE.md.
> 라우터 배선/RouterProvider는 `pages/` 부재로 후속(가드는 app/router에 준비 완료).

---

## S8 — 검증

- `tsc --noEmit`: cannot-find 0 · 총 16건(전량 선재 TS1294/6133/6196).
- `eslint .`: import-resolution 오류 0 (잔여 error는 선재 no-explicit-any/no-unused-vars).
- 레이어 경계 감사: 상위 역참조 0. cross-entity 2건(type-only) 문서화.
