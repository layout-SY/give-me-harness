# Dependency & Architecture Decision — FSD Layer Contract

> 작성일: 2026-07-03
> 도메인: 전 프로젝트 구조 (횡단)
> 관련 세션: `logs/sessions/2026-07-03-fsd-architecture-restructure/`
> 살아있는 계약: `src/ARCHITECTURE.md`

---

## 1. 의존 방향 (레이어 순서)

```
app        (초기화·라우터·조립 지점)
  ↓
pages      (라우트 화면)
  ↓
widgets    (독립 UI 블록)
  ↓
features   (유스케이스)
  ↓
entities   (비즈니스 엔티티)
  ↓
shared     (도메인-무지 인프라)
```

- **하위 방향만 허용**. 상위 레이어 참조(역방향) 금지.
- 같은 레이어 슬라이스 간 직접 import 금지 → 슬라이스 public API로만.

### 데이터 흐름 (런타임 의존)
```
shared/api/axios-instance         (HTTP 인프라)
  ↓
shared/api/common/* (api-result)  (순수 타입/매퍼)
  ↓
shared/api/api-client             (클라이언트 추상화)
  ↓
entities/<d>/api/<d>.api          (도메인 API 모듈, factory)
  ↓
entities/<d>/api/index (<d>Api)   (axiosInstance 주입 완료 singleton) ← public API
  ↓
features / widgets / pages        (execute(() => <d>Api.x()) 호출)
        ↑
shared/lib/hooks/use-api (useApi) (도메인-무지 실행기: 취소·로딩·에러 Dialog)
```

---

## 2. 레이어 간 허용/금지 규칙

| 레이어 | 허용 import | 금지 |
|--------|-------------|------|
| `app` | 전 하위 레이어 | — |
| `pages` | widgets·features·entities·shared | 다른 page |
| `widgets` | features·entities·shared | app·pages·다른 widget |
| `features` | entities·shared | app·pages·widgets·다른 feature |
| `entities` | shared (+ 동일 slice 내부) | app·pages·widgets·features·**다른 entity(직접)** |
| `shared` | shared 내부만 | **모든 도메인/상위 레이어** |

### 슬라이스 세그먼트 표준
```
<slice>/
├── api/     *.api.ts, *.dto.ts, index.ts(=<d>Api singleton)  (entities)
├── model/   store, enum, 도메인 타입, pub-sub 선언병합       (※ hook 금지)
├── hook/    슬라이스 훅(use*.ts, behaviors/*) — 상태·부수효과
├── lib/     도메인-무지 순수 함수(변환·파생·검증)
├── ui/      표현 컴포넌트
└── (index.ts) public API
```
> **훅은 `model/`이 아니라 `hook/`에 둔다.** `model/`은 비-훅 도메인 자산(타입·store·enum·pub-sub 병합) 전용. 순수 함수는 `lib/`.
> 참조 구현: `features/calendar-picker/` (ui / hook(+behaviors) / model(types·pub-sub.events) / lib(date-range·calendar-cells)).

---

## 3. 공용화 수준 결정

| 자산 | 수준 | 근거 |
|------|------|------|
| `createApiClient`, `axiosInstance`, `ApiResult`/`ApiError` | shared/api | 도메인-무지 HTTP 계약 |
| `useApi` | shared/lib (공용 훅) | 도메인-무지 실행기. **더 이상 registry를 알지 않음** |
| `usePubSub` + base `PubSubEvents` | shared/lib | 도메인-무지 이벤트 버스 |
| utils, exceptions | shared/lib | 횡단 유틸 |
| 공통 enum(common/response-codes/language/currency) | shared/config | 전 도메인 어휘 |
| `<d>Api` singleton | entities/<d>/api (public) | 도메인별 API 접근점 |
| 도메인 enum·store·table-rows·pub-sub 이벤트 | entities/<d>/model | 도메인 소유 |
| 전역 `api` registry(구 `~/apis`) | **폐기** | shared→app 결합 유발 |

---

## 4. 핵심 아키텍처 결정 (ADR 요약)

### ADR-1. api 접근: 전역 registry → entity별 singleton
- **문제**: `useApi().api.<d>.x()`는 shared 훅이 전 도메인을 아는 역방향 결합.
- **결정**: 전역 registry 폐기. 각 entity가 `<d>Api` singleton을 public API로 노출. `useApi`는 `{ execute, isLoading }` 순수 실행기.
- **영향**: `reference/custom-hooks` SKILL의 "api는 useApi로만 접근" 규약 갱신 필요. 호출 패턴 = `import { <d>Api }` + `execute(() => <d>Api.x())`.

### ADR-2. pub-sub: 타입 맵 제네릭화 + 선언 병합
- **문제**: `PubSubEvents`가 도메인 DTO(dao·calendar) 직접 참조.
- **결정**: base `interface PubSubEvents`는 도메인-무지. 도메인 이벤트는 소유 레이어에서 `declare module "~/shared/lib/pub-sub/events"`로 병합.
  - `features/calendar-picker/model/pub-sub.events.ts`, `entities/dao/model/pub-sub.events.ts`
- **전제**: `PubSub<TEvents extends object>` (interface는 index signature 부재로 `Record<string,any>` 불충족).

### ADR-3. dao: 단일 entity (내부 세그먼트)
- **문제**: "주요 하위 개별 entity" 요구 vs 코드 실제.
- **결정**: dao는 단일 entity 유지. 하위가 공통 `shared.dto`에 의존하고 `dao.api`가 이들을 조립하므로, 분해 시 cross-entity import가 증가(satellite→core + aggregator→satellite).
- **트레이드오프**: 개별 배포/격리 불가 vs 결합 최소·조립 일관성. 후자 채택.

### ADR-4. cross-entity type-only 2건 (미해결)
- `profile→admin-settings`(ADMIN_ROLE_TYPE_CODES), `usage→sales`(TRANSACTION_*).
- **권장**: 교차 도메인 어휘이므로 해당 enum을 `shared/config/enums`로 승격해 entity→shared로 정규화.

---

## 5. 최종 레이어 형태 (파일 분포)

| 레이어 | 파일 수 | 구성 |
|--------|--------|------|
| app | 6 | index·App·router(가드 2)·styles(2) |
| pages | 0 | (신규 예정) |
| widgets | 11 | app-header · side-navigation(+model) |
| features | 28 | auth(+model) · select-users · image-manager · calendar-picker |
| entities | 87 | 15 도메인 × {api, (model), (ui)} |
| shared | 160 | api · lib · ui · config · assets |

(총 293 파일)
