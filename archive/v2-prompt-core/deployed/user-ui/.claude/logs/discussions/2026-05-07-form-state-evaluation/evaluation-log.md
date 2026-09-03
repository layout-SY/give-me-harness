# Evaluation Log — 프로젝트 Form 상태 관리 현황 진단

- 일자: 2026-05-07
- 평가자: evaluator 에이전트
- 범위: `src/pages/**`의 searchState / form state / 요청 payload 구성 패턴 전반

```yaml
summary: synthoria-admin-ui의 form/searchState/payload 구성은 페이지 컴포넌트에 stateful 로직과 stateless 변환이 혼재되어 있고, react-hook-form/zod/react-query 미도입 상태로 useState + useApi(execute) + pubsub 패턴이 도메인마다 변형 복제되어 중복·검증 누락·테스트 어려움을 누적시키고 있다. ROI가 가장 높은 첫 단추는 "list searchState 동기화 hook"과 "도메인 빌더 함수 분리(toDraft/buildPayload)"이며, react-hook-form/react-query 도입은 P2로 점진 권장.
decision: recommendation_ready
status: recommendation_ready
handoff_to_planner_optional: true
```

## 1. 현황 파악 (대표 사례)

### 1.1 라이브러리 도입 현황 (package.json 기준)
- 상태/데이터: **jotai 2.x만 존재**
- 미도입: **react-query / TanStack Query**, **react-hook-form**, **zod**
- 라우팅: react-router-dom 6.22.3 (useSearchParams 사용 가능하나 거의 미활용)
- 결론: form/server-state 라이브러리가 전혀 없음 → 모든 패턴이 "useState + custom useApi.execute + pubsub" 조합으로 수작업 구현.

### 1.2 패턴 A — list 페이지의 searchState (대표: `src/pages/dao/proposal-manage/index.tsx`)
- searchState를 useState로 보유하고 `useFetchAdapter`(`src/components/table/hooks/useFetchAdapter.ts`)에 주입.
- 페이지 내부에 `enum FILTER_TYPES`를 두고 거대한 `handleFilter(type, index, value)` switch-by-enum으로 모든 필드 변경을 분기.
- **URL 동기화 없음**. 새로고침/링크 공유 시 필터 상태 유실.
- 동일 패턴이 dao/discuss-posts-management, dao/dao-logs, dao/quest-reward, dao/proposal-audit, dao/pass-management/*, manage/sales/*, manage/usage/*, manage/content/* 등 **20+ 페이지에서 반복**.

### 1.3 패턴 B — 단일 URL 동기화 (예외 사례)
- `src/pages/ecommerce/products/index.tsx`만 useSearchParams를 사용하지만, **단방향(읽기 전용)**으로 `searchParams.has("sellerId")` 분기 후 setSearchState. 양방향 sync 없음, 공통 hook 없음.
- `change-password/modules/detail.module.tsx`도 useSearchParams 사용. 두 페이지가 각자 다르게 구현.

### 1.4 패턴 C — modal에서 form state + 제출
- 대표: `dao/proposal-manage/create/_id.modal.tsx`, `admin-settings/admins/create.modal.tsx`, `dao/discuss-posts-management/detail/_id.modal.tsx`
- `_initFormState` 상수 + `useState<FormDto>` + 필드별 `setFormState((prev) => ({...prev, x: e.target.value}))` 패턴.
- 검증은 inline if 체이닝 + `Dialog.alert`로만 처리. 재사용/스키마 없음.
- 제출은 try/setIsLoading(true) → execute(...) → finally setIsLoading(false). **finally가 비동기 onSuccess 이전에 실행되어 isLoading 라이프사이클이 사실상 의미 없는 케이스 다수**.
- admin create.modal.tsx: roles 추가/제거는 인터랙션 + 파생 상태(availableRoleItems) 포함 → 이미 hook 추출 임계 도달했지만 컴포넌트 안에 그대로 있음.

### 1.5 패턴 D — 생성/수정 혼재 (대표: `src/pages/manage/items/_id.modal.tsx`, **1006 lines**)
- 한 컴포넌트가 `MODAL_STATES = {NULL, CREATE, READ, UPDATE}`를 모드로 들고, `FormStateTypes = Partial<ItemDto> & Partial<CreateItemDto>` 같이 두 DTO를 union해서 동일 state로 운용.
- 결과: 1000줄 단일 파일. payload 빌드/검증/모드 분기/카테고리 cascade/이미지 업로드 등 모든 책임 집중.
- `admin-settings/admins/_id.modal.tsx` (369), `manage/users/_id.modal.tsx` (450)도 동일 양상의 축소판.

### 1.6 패턴 E — 부분 hook 추출 (좋은 신호, 그러나 중간 단계)
- `src/pages/dao/proposal-manage/detail/_id.modal.tsx`는 mutation을 `useProposalDetailFetch`로 분리(좋음).
- 그러나 hook이 setIsLoading 콜백을 외부에서 주입받는 형태(역제어, props drilling 변종).
- form state(`formState`) / draft 변환(`toProposalDraft`) / `isFormDirty`(JSON.stringify 비교) / 카테고리 파생값 등은 여전히 모달 안에 평면 배치.
- 즉 **mutation hook만 떨어져 나가고 stateful form hook(`useProposalForm`)이 없는 절반의 분리** 상태.

## 2. 현재 패턴의 문제점

### 2.1 Stateful/stateless 혼재
- proposal-detail 모달: `toProposalDraft`(순수 변환)는 모듈 최상단 OK. 그러나 `isFormDirty = JSON.stringify(formState) !== JSON.stringify(toProposalDraft(fetchedData))` 같은 stateful 파생 비교가 컴포넌트 본문에 그대로 노출. 빌더 함수는 있는데 form hook이 없어 책임 분리가 절반.
- items 모달: payload 빌더 자체가 컴포넌트 내부에 인라인. `_buildItemIdPrefix`처럼 순수 함수는 모듈 상단으로 빠져 있지만, `buildCreateItemPayload(state)` / `buildUpdateItemPayload(state)`는 분리되어 있지 않음.

### 2.2 중복 빌더/검증 로직
- "필수 필드 if 체크 → `Dialog.alert(mui[키])`" 패턴이 거의 모든 create/update 모달에 손으로 복제됨(admin create, proposal create, items, users 등). **스키마/공용 검증기 없음**.
- "_initState 객체"가 도메인마다 컴포넌트 내부에 const로 박혀있고, draft 변환 함수가 있는 곳/없는 곳이 갈림 → DTO 모양이 바뀌면 다중 위치 수정 필요.
- `Partial<XxxDto>` 트릭이 admin-create와 items modal에 동일 등장 → "타입 안전성 절반만" 패턴이 관용적으로 굳어짐.

### 2.3 테스트 가능성
- 폼 컴포넌트가 useApi/usePubSub/useDialog/useLanguage를 모두 직접 의존 → 빌더/검증 단위 테스트가 불가능.
- `JSON.stringify` dirty check는 키 순서/Date/undefined 정규화 이슈에 취약.
- `useFetchAdapter`는 `requestSearch` 플래그를 setState로 토글하는 pull 모델 → 동시 제어 시 race(연속 setRequestSearch(true)) 발생 가능. 캐시/취소/재시도 없음.

### 2.4 라이프사이클 정확성
- `dao/discuss-posts-management/detail/_id.modal.tsx`: `try { setIsLoading(true); execute(...) } finally { setIsLoading(false) }` → execute의 onSuccess는 비동기인데 finally는 동기적으로 즉시 실행. **로딩 종료가 사실상 즉시** 발생 → UX 상 로딩 인디케이터가 의미를 잃음. 동일 안티패턴이 proposal-create, useProposalDetailFetch 등에 광범위 복제.
- create.modal.tsx(admin)는 await으로 올바르게 처리 → **한 코드베이스에 두 가지 라이프사이클 컨벤션 공존**.

### 2.5 pubsub-주도 모달 오케스트레이션
- 모든 모달이 "pubsub.subscribe(open-xxx)" → useState(isOpen) → 닫힘. 모달 자체가 라우트가 아니므로 딥링크 불가, 동시 다중 모달 상태 관리가 글로벌 이벤트 채널로만 가능.
- "강제 종료 모달"(forceEndVoteReasonModal)은 pubsub.publish 후 callback으로 reason 회수 → 비동기 합성을 일회용 콜백 prop으로 wiring. **Promise/awaitable 모달 API가 없어 합성 비용 큼**.

## 3. 개선 방향 평가 (ROI 우선순위)

### P0 (가장 높은 ROI, 도입 비용 낮음, 즉시 효과)
1. **shared hook: `useSearchParamsState<TQuery>(initial)`** (`src/hooks/use-search-state.ts`)
   - URL ↔ state 양방향 동기화 + 도메인 무관. 20+ 페이지가 동일 시그니처로 마이그 가능.
   - 동시에 enum FILTER_TYPES + handleFilter 거대 switch를 `setSearchState({ ...prev, [key]: value })`로 단순화.
2. **도메인별 빌더 함수 분리**: 각 도메인에 `model/payload.ts` 추가
   - `toXxxDraft(detail)`, `buildCreateXxxPayload(form)`, `buildUpdateXxxPayload(form, prev?)` (DTO 변환만, 순수).
   - 호출부에서 `mode === "create" / "edit"`에 따라 빌더 선택. `Partial<Dto>` 트릭 폐기.
   - 테스트: 빌더만 unit test로 즉시 커버 가능.
3. **검증 빌더 분리**: `validateXxxPayload(form): { ok: boolean; messageKey?: string }`
   - 모든 inline if + Dialog.alert를 한 함수로 압축. Dialog는 호출부 책임.
   - zod 미도입 단계에서도 일관 패턴 확보(나중에 zod로 교체 1:1 가능).

### P1 (구조 개선, 점진 가능)
4. **도메인 form hook**: `useXxxForm({ mode, initial })`
   - dirty 비교(`JSON.stringify` 제거 → 필드별 비교 또는 ref baseline), 카테고리 cascade(items의 main↔sub), roles add/remove(admin) 같은 stateful 로직을 hook 안으로.
   - proposal-detail의 `isFormDirty`, `handleSelectCategory`, `handleToggleMode`가 1차 후보.
5. **mutation hook 패턴 표준화**: useProposalDetailFetch처럼 흩어진 mutation들을 도메인별로 일관된 hook으로 정리하되, **외부에서 setIsLoading을 주입받는 역제어를 폐기**하고 hook 자체가 isLoading 반환.
6. **execute 라이프사이클 anti-pattern 일괄 정리**: try/finally setIsLoading 패턴을 await execute 또는 hook 내부 useState로 교체. lint rule(또는 SKILL.md 가이드)로 신규 진입 차단.

### P2 (라이브러리 도입, 큰 결정 필요)
7. **react-hook-form + zod 도입**:
   - 1000줄급 모달(items, proposal-detail, admin _id, users _id)에서만 우선 적용해 임팩트 측정.
   - 도입 ROI 높지만, 기존 컴포넌트(TextInput/Dropdown/DateRangeField/TextArea 등) controlled 인터페이스를 register/Controller로 어댑팅하는 작업이 비용. 공용 어댑터 1회 작성 필요.
8. **TanStack Query 도입**:
   - useApi.execute + useFetchAdapter + setRequestSearch 토글 + pubsub("refresh-xxx") 3종 세트를 `useQuery({ queryKey: [...searchState] })` + `queryClient.invalidateQueries`로 대체.
   - 가장 큰 코드량 절감 가능하지만, 글로벌 pubsub 기반 갱신 시그널을 query invalidation으로 옮기는 도메인 와이드 마이그레이션이라 리스크 가장 큼.

### 기타
- 모달 오케스트레이션을 pubsub에서 "Promise-returning modal API"로 점진 이전(forceEndVoteReasonModal 패턴이 그 신호) → 비동기 합성 비용 절감.
- FSD 관점: 현재 `src/pages` 안에 model/builder/hook/components가 모두 평면. 도메인별로 `pages/<domain>/model/`(타입+빌더), `pages/<domain>/hooks/`(form/mutation hook), `pages/<domain>/components/` 분리만 해도 가독성 큰 개선.

## 4. 리스크
- **일괄 마이그레이션 폭발 위험**: 20+ 페이지를 한 번에 useSearchParamsState로 갈아끼우면 query string 컨벤션(키명/직렬화) 합의 실패 시 광범위 회귀. → 키 직렬화 규약(plain string, undefined 제거, page=1 default 등)을 SKILL.md로 사전 고정 필수.
- **점진 도입 시 컨벤션 혼재**: 이미 useApi vs await execute, JSON.stringify dirty vs 명시 비교, useSearchParams 단방향 vs 양방향이 공존. 새 패턴 도입 시 "신규 코드부터 강제 + 기존은 다음 리팩터링 시점"이라는 명문 규칙 없으면 4번째 사투리가 추가될 뿐.
- **react-hook-form 부분 도입 위험**: 한 모달 안에서 controlled state와 register가 섞이면 dirty/reset 동작이 비대칭. 1 모달 단위로 완전 이전이 원칙.
- **useFetchAdapter 의존도 높음**(거의 모든 list 페이지) → 이를 react-query로 교체할 때 임시로 둘 다 사용 시 캐시 일관성 문제. 어댑터 내부에서 react-query 위임으로 우회하는 단계적 전략 권장.

## 5. Architectural Risks (요약)

- URL 동기화 부재로 list 필터 상태 유실 + 페이지 간 컨벤션 불일치
- Stateful form 로직이 페이지 컴포넌트에 평면 배치되어 1000줄급 파일 발생, mode union DTO 안티패턴 정착
- 검증 로직 중복: 모든 create/update 모달에 if + Dialog.alert가 손복제, zod/공용 validator 부재
- execute(...) 호출 직후 try/finally로 setIsLoading(false)하는 비동기 라이프사이클 안티패턴이 광범위 복제
- pubsub 기반 모달 오케스트레이션이 비동기 합성 비용을 callback prop drilling으로 전가
- useFetchAdapter의 requestSearch boolean 토글 모델은 캐시/취소/재시도 부재
- JSON.stringify 기반 dirty check가 다수 위치에 등장 (정확성/성능 모두 취약)
- Mutation hook은 일부 추출되었으나 setIsLoading 역제어 인터페이스라 재사용성/테스트성 낮음

## 6. Recommended Backlog

| ID | 우선순위 | 크기 | 항목 |
|---|---|---|---|
| BL-1 | P0 | S | 공용 `useSearchParamsState` hook 설계서 + 첫 적용 페이지 1개(가장 단순한 list, 예: dao/dao-logs)에 도입하여 키 직렬화 규약 확정 |
| BL-2 | P0 | S | dao/proposal-manage 도메인에 `model/payload.ts` 신설 — `toProposalDraft` 이전 + `buildCreatePayload`/`buildUpdatePayload` 분리 + 단위 테스트 |
| BL-3 | P0 | S | `validateXxxPayload` 표준 시그니처 결정 + dao/proposal-manage/create와 admin-settings/admins/create에 적용 (검증 로직 중복 제거 PoC) |
| BL-4 | P1 | M | `useProposalForm` hook 추출 — proposal-detail 모달의 formState/dirty/mode/category 핸들러 캡슐화. JSON.stringify dirty 폐기. |
| BL-5 | P1 | M | `useProposalDetailFetch` 리팩터링 — setIsLoading 역제어 폐기, hook이 isLoading/run 반환. 동일 패턴을 다른 mutation hook의 표준 템플릿으로 채택. |
| BL-6 | P1 | S | try/finally setIsLoading anti-pattern 코드베이스 grep + 일괄 수정 PR(또는 SKILL.md 추가 + 신규 코드 차단) |
| BL-7 | P2 | L | `manage/items/_id.modal.tsx` (1000줄)을 react-hook-form + zod로 파일럿 마이그레이션. 공용 RHF 어댑터(TextInput/Dropdown/DateRangeField) 작성 포함. |
| BL-8 | P2 | L | TanStack Query PoC — 1개 도메인(예: dao/dao-logs) 한정으로 useFetchAdapter 우회. pubsub refresh를 invalidateQueries로 교체. |
| BL-9 | P2 | M | pubsub 기반 모달 → Promise 모달 API 설계서 + forceEndVoteReasonModal 1건 이전 PoC |

## 7. 참고 파일

- `package.json`
- `src/pages/dao/proposal-manage/index.tsx`
- `src/pages/dao/proposal-manage/detail/_id.modal.tsx`
- `src/pages/dao/proposal-manage/create/_id.modal.tsx`
- `src/pages/dao/proposal-manage/detail/hooks/useProposalDetailFetch.tsx`
- `src/pages/dao/discuss-posts-management/detail/_id.modal.tsx`
- `src/pages/admin-settings/admins/create.modal.tsx`
- `src/pages/manage/items/_id.modal.tsx`
- `src/pages/ecommerce/products/index.tsx`
- `src/components/table/hooks/useFetchAdapter.ts`

## 8. Next Action

사용자 검토 후, P0 백로그(BL-1~BL-3) 1개를 골라 planner에게 이관해 plan.md 작성을 진행. 동시에 SKILL.md(searchState 직렬화 규약, 빌더/검증 시그니처) 초안 작업을 publisher 트랙으로 분기.
