---
name: policy-hook-extraction
description: synthoria-admin-ui에서 hook 분리 여부와 형태를 결정할 때 사용하는 횡단 정책. hook 분리 기준(상태성), 도메인 전용 hook vs 공용 마이크로 hook 구분, form/modal의 3-layer 분리 패턴을 판단해야 할 때 사용.
---

# Hook Extraction (Policy)

## 언제 이 스킬을 사용하나요?

- 페이지/컴포넌트에서 로직을 hook으로 분리할지 결정할 때
- 여러 도메인에 공통 hook을 만들지 도메인 전용 hook을 만들지 판단할 때
- form/modal 코드의 분리 구조를 설계할 때
- searchState, payload 등 요청 상태 관리 방식을 결정할 때

---

## 0. 분리 판단 3-질문 (진입 결정 절차)

> hook/util 분리 여부를 정하는 **첫 관문**. 분리 기준은 *재사용*이 아니라 **책임(변경 이유)·순수성·테스트 가능성**이다. 재사용은 분리 이유 중 하나일 뿐이다.

1. **React 없이 순수 함수로 쓸 수 있나?** → `lib`/util로 추출. (재사용 여부 무관 — 테스트·가독성 이득이 확정적. 예: 데이터 파생, role 필터, 순수 변환)
2. **다른 곳에서도 쓰이나?** → 공용 hook/util로 추출. (전형적 재사용)
3. **둘 다 아니지만, 빼면 컴포넌트가 "거의 순수 렌더"만 남나?** → 취향의 영역. 뺀다면 **co-located 단일목적** hook으로만. 아니면 **인라인 유지가 정답**.

### 원칙
- **순수 로직은 아래로/밖으로**(`lib`), **뷰-로컬 임시 상태는 뷰에** 남긴다.
- **진단 포인트**: "UI에 로직이 섞여 어색하다"의 진짜 원인은 대개 handler/뷰-로컬 상태가 아니라 **순수 파생 로직이 렌더 함수 안에 있는 것**이다. 그 순수 조각의 분리를 우선한다.

### 안티패턴
- Q1·Q2 어디에도 안 걸리는 로직(단일 사용·상태 소유가 뷰)을 "정리" 명목으로 **만능 `useXxx` 훅에 몰아넣기**. 서로 무관한 관심사를 묶어 재사용성은 0인데 locality만 잃는다. → 리팩터가 아니라 이동일 뿐.
- 단일 사용이라는 이유만으로 분리를 강요하는 것도, 반대로 순수분리(Q1)를 재사용 없다고 막는 것도 오적용이다.

> §1 이하는 이 3-질문을 통과한 뒤 **어떤 형태(순수 함수 vs hook, 도메인 전용 vs 공용)**로 만들지의 세부 기준이다.

---

## 1. Hook 분리 기준 — 상태성(Statefulness)

**필드 수가 기준이 아니다. 상태성 여부가 기준이다.**

| 상황 | 형태 |
|---|---|
| 본질이 **데이터 변환/검증** (상태 없음) | 순수 함수 (`buildPayload`, `validate`) |
| 본질이 **상태 관리 + 부수효과** | hook (`useXForm`, `useXSearchState`) |
| 상태가 있더라도 **단순 useState 1개** | 페이지/컴포넌트 인라인으로 충분 |

**잘못된 기준 예시**:
- "필드가 5개 이상이면 hook" → 8개 number 필드라도 본질이 캐스팅이면 빌더 함수가 정답
- "로직이 길면 hook" → 길더라도 상태가 없으면 순수 함수

---

## 2. 도메인 전용 Hook vs 공용 마이크로 Hook

### 도메인 전용 Hook이 정답인 경우

- 도메인별로 타입, 검증 규칙, 중첩 구조가 다름
- "공용처럼 보이지만 각 도메인에서 다르게 쓰인다" → 이미 도메인 hook

```
// 잘못된 방향
useFormState<T>(initial)  // 공용 — generic 폭발 또는 any 회귀

// 올바른 방향
useCreateProposalForm()   // 도메인 전용
useAdminForm()            // 도메인 전용
```

### 공용 마이크로 Hook이 정당화되는 경우

- **상태성 + 부수효과**가 본질이고 도메인 무관한 횡단 패턴
- 추상화 4조건 중 하나 이상 충족 (`policy-abstraction-strategy` 참고)

**synthoria-admin-ui 공인 공용 마이크로 hook 패턴**:
- `useModalOpenSubscribe(topic)` — pubsub open/close (모든 모달 공통)
- `useDirtyState(initial, current)` — dirty 비교
- `useDiscardConfirm(dirty)` — 닫기 confirm 다이얼로그
- URL ↔ state 양방향 동기화가 필요한 경우 (`useSearchStateUrlSync`)

단순 객체 구성/초기값 병합에는 hook 금지 — 순수 함수로 충분

---

## 3. Form/Modal 3-Layer 분리 패턴

모달/form 코드가 복잡할 때 적용하는 분리 구조.

| Layer | 역할 | 형태 | 위치 |
|---|---|---|---|
| **L1. 빌더·검증** | form state → API payload 변환, 필드 검증 | 순수 함수 | 도메인 `model.ts` |
| **L2. 도메인 form hook** | initialState, setState, submit 게이팅 | 도메인 전용 hook | 도메인 `hooks/` |
| **L3. 공용 마이크로 hook** | 진짜 횡단인 것만 (pubsub, dirty 등) | 공용 hook | `src/hooks/` |
| **컴포넌트** | JSX 결선만 | React component | 도메인 |

**L1이 존재해야 L2가 가벼워진다.** 빌더 함수는 순수 함수이므로 독립 테스트 가능.

---

## 4. SearchState Hook 패턴

페이지 테이블의 searchState(요청 쿼리)를 hook으로 분리할 때 적용한다.

```
// 올바른 방향
useDaoProposalSearchState()   // 도메인 전용

// 잘못된 방향
useSearchState<T>()           // 공용 — useFetchAdapter와 쿼리 객체 충돌
```

**반환 구조 권고**:
```ts
{
  searchState,        // fetch에 직접 전달
  patch,              // 부분 업데이트
  reset,
  bar,                // SearchStateBar props를 spread로 전달 가능한 묶음
  sort,               // TableSortFilter props 묶음
}
```

**의도적 비포함**: `setRequestSearch`(fetch 트리거)는 hook에 넣지 않는다. 페이지가 보유 → fetch 결합 방지.

---

## 5. Create/Update Hook 통합 판단

| 조건 | 결정 |
|---|---|
| create/update의 form shape가 동일 | mode 분기 hook 1개 |
| shape가 다름 (중첩 구조, 필드 차이 등) | hook 분리 |
| update가 아직 없음 | 분리하지 않음 (YAGNI) |

mode 분기 패턴:
```ts
type Mode = { kind: "create" } | { kind: "update"; id: number; initial: ReadDto };
function useXForm(mode: Mode) { ... }
```

---

## 금지

- 필드 수 기준으로 hook 분리 결정
- 단일 공용 form hook 생성 (`useFormState<T>`, `usePayload` 등)
- 도메인 특수 로직을 공용 hook에 흡수 (→ generic 폭발 또는 any 회귀)
- 순수 함수로 충분한 변환 로직에 hook 적용
- create/update가 shape 다른데 무리하게 generic으로 통합
