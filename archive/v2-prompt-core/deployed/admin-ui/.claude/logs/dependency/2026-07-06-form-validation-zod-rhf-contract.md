# Dependency & Architecture Decision — Form Validation (zod + react-hook-form)

> 작성일: 2026-07-06
> 도메인: 폼/요청 body/파라미터 유효성 (횡단)
> 정책: `policy-validation` · 살아있는 계약: `src/ARCHITECTURE.md`
> 상태: **큰 틀(의존 계약)만 확정. 실제 스키마/폼/어댑터 구현은 미착수. 패키지 미설치.**

---

## 0. 결정 요약

- 표준 스택 = **zod**(검증 스키마=계약) + **react-hook-form**(폼 상태) + **@hookform/resolvers**(zodResolver).
- 검증은 **스키마 단일 출처**. 폼 상태는 RHF. 수동 `if` 검증·폼 로컬 useState 난립을 대체.
- FSD 세그먼트에 역할별로 배치하고, 의존은 하위 방향만.

### 확정 결정 (2026-07-06)
- **파이프라인**: RHF + zodResolver + 공용 **`FormField`** 표준. 커스텀 제네릭 검증 훅(`useFormValidation`/`useFormCheck` DSL)은 **만들지 않는다**(RHF가 이미 그 역할, zod 재구현·leaky abstraction 회피).
- **결과 노출**: **필드별 구독**. `FormField`가 `useFormContext`로 **자기 필드 에러만** 읽어 렌더한다. 폼 전체 error 객체를 사용처가 받아 배분하지 않는다(필드 간 결합 0).
- **사용처 무지**: 사용처(ui/page)는 zod를 작성하지 않는다. 도메인 스키마(`model`)를 바인딩한 form 훅만 사용 → "검증 내부"를 모른다.

## 0-1. 공용 `FormField` 어댑터 계약 (shared/ui/form)

- **책임**: 디자인시스템 인풋(`as` prop) + 라벨 + **필드 하단 에러 표시**를 한 단위로 묶는다. 도메인/스키마 무지.
- **props(계약 → `interface`)**: `{ name: string; label?: string; as: 인풋컴포넌트; ...passthrough }`.
- **에러 소스**: `useFormContext().formState.errors[name]` — 자기 필드만 구독(다른 필드 변화에 리렌더 안 됨).
- **표시**: 에러 시 입력 아래 `<span className="field-error">{error.message}</span>` — **빨간색(css)**, **한글은 zod message에 직접 작성**. null/정규식/min·max 등 실패 사유는 zod 규칙별 한글 메시지로 구분.
- **전제**: 폼은 `FormProvider`로 감싼다(=`useForm` 반환을 context로 제공). `FormField`는 `useFormContext`로 접근.

---

## 1. 조각별 FSD 배치

| 조각 | 역할 | 위치(세그먼트) | 계약 성격 |
| --- | --- | --- | --- |
| **zod 스키마** | 검증 계약 + form shape 원천 | `<slice>/model/<x>.schema.ts` | 순수. `type X = z.infer<typeof schema>` |
| **payload 빌더** | 검증 통과값 → 서버 DTO 매핑 | `<slice>/model/<x>.payload.ts` | 순수함수 (`recipe/data-dto`) |
| **도메인 form 훅** | `useForm+zodResolver`, submit 게이팅, create/update mode | `<slice>/hook/use<X>Form.ts` | 상태·부수효과 (L2) |
| **공용 RHF 어댑터** | 디자인시스템 인풋 ↔ RHF 결선 | `shared/ui/form/*` | 도메인 무지. props=계약→`interface` |
| **공용 zod 프리미티브** | 재사용 refinement(email/phone/required 키 등) | `shared/lib/validation/*` | 도메인 무지 |
| **폼 컴포넌트** | 훅 + 어댑터 결선(JSX) | `<slice>/ui/*` 또는 `pages/*` | 표현 |

> `<slice>` = `features/<f>` 또는 `entities/<d>` (혹은 소비 `pages/<p>`).

---

## 2. 의존 방향 (하위 방향 단방향)

```
외부: react-hook-form / zod / @hookform/resolvers
  ↑
shared/lib/validation (공용 zod 프리미티브)     shared/ui/form (RHF 어댑터: shared/ui 인풋 결선)
  ↑                                                ↑
<slice>/model/<x>.schema.ts (zod 스키마, 순수) ── z.infer ──▶ form type
  ↑                         └▶ <slice>/model/<x>.payload.ts (통과값→DTO)
<slice>/hook/use<X>Form.ts (useForm+zodResolver(schema) + 어댑터 사용)
  ↑
<slice>/ui / pages (폼 컴포넌트)
```

### 허용/금지 (FSD 계약 정합)
- `model/schema` → `shared/lib/validation`, `zod`(외부)만. 상위 레이어·타 슬라이스 참조 금지.
- `hook/useXForm` → 동일 슬라이스 `model`(schema/payload) + `shared/ui/form` + `shared` + RHF(외부). OK.
- `shared/ui/form` → `shared/ui` 인풋 + RHF(외부)만. **도메인 무지**(어떤 스키마/도메인도 모른다).
- schema는 `ui/`에 두지 않는다(검증 계약=model).
- 폼 shape 타입은 `z.infer` 파생만(중복 선언 금지).

---

## 3. 큰 틀 스켈레톤 (이번에 생성)

```
src/shared/ui/form/     # 공용 RHF 어댑터 자리 (placeholder)
src/shared/lib/validation/  # 공용 zod 프리미티브 자리 (placeholder)
```
- 슬라이스별 `model/*.schema.ts`, `hook/use<X>Form.ts`는 **해당 폼 구현 시** 생성(선제 생성 안 함, YAGNI).

---

## 4. 패키지 (설치 필요 — 미설치)

```
zod  react-hook-form  @hookform/resolvers
```
- 신규 런타임 의존성이므로 **설치는 사용자 승인 후**. 설치 전까지 스켈레톤은 외부 import 없는 placeholder 유지(빌드 무영향).

---

## 5. 기존 자산과의 관계

- `recipe/data-dto`(폼↔payload 매핑): payload 빌더가 이를 따른다.
- `policy-hook-extraction §3`(Form/Modal 3-Layer): L1=schema/payload(model), L2=useXForm(hook), L3=공용 마이크로(shared). 본 계약이 L1/L2 구현 스택을 zod/RHF로 고정.
- `policy-type-definition`: 어댑터 props=계약→interface, z.infer form type=데이터→type.
- backlog `BL-7`(react-hook-form+zod PoC)·`BL-3`(검증 빌더 표준 시그니처)의 상위 계약.

---

## 6. 후속 (구현 착수 시)
1. 패키지 설치 승인 → `zod`/`react-hook-form`/`@hookform/resolvers`.
2. `shared/ui/form` 어댑터 1차(TextInput/Dropdown/TextArea/DateRangeField) 구현.
3. 파일럿 도메인 1곳(예: `admin-settings` 관리자 폼 또는 `dao` proposal)에서 schema+useXForm PoC.
4. 성공 후 `recipe/form-validation` 조립 레시피 신설 검토.
