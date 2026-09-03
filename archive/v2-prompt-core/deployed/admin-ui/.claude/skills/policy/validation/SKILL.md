---
name: policy-validation
description: synthoria-admin-ui에서 폼/요청 body/파라미터 유효성을 검증할 때 지켜야 하는 횡단 규칙. 표준 스택은 zod(스키마=검증 계약) + react-hook-form(폼 상태). 스키마 위치, RHF 폼 훅 분리, 어댑터, DTO 매핑, 한글 에러 메시지를 지켜야 할 때 사용.
---

# Validation (Policy)

> **표준 스택**: `zod`(검증 스키마) + `react-hook-form`(폼 상태) + `@hookform/resolvers`(zodResolver 브릿지).
> 유효성은 **zod 스키마 단일 출처**로 정의하고, 폼 상태는 RHF로 관리한다. 흩어진 수동 `if` 검증을 새로 만들지 않는다.
> FSD 배치·의존 방향은 `.claude/logs/dependency/2026-07-06-form-validation-zod-rhf-contract.md` 참고.

## 언제 이 스킬을 사용하나요?

- 신규/수정 모달·폼(formState 등 요청 body 객체)을 구현할 때
- page/컴포넌트 간 파라미터 이동 경계에서 값을 검증할 때
- submit 핸들러에서 서버 payload로 매핑하는 로직을 작성할 때

## 규칙

### 스키마 (검증 계약)
- 유효성 규칙은 **zod 스키마**로 선언한다. 컴포넌트/훅에 흩어진 수동 검증 로직 금지.
- 스키마는 **소유 슬라이스의 `model/`** 에 둔다 (`<slice>/model/<x>.schema.ts`). 순수(런타임+타입), React 무의존.
- 폼 shape 타입은 **`z.infer<typeof schema>`로 파생**한다 (동일 shape 타입 중복 선언 금지). 파생 타입은 데이터 형태이므로 `type` (`policy-type-definition`).
- 경계 검증(page↔page 파라미터, URL param 등)도 값을 소유한 슬라이스의 스키마로 `parse`/`safeParse`.

### 폼 상태 (react-hook-form)
- 폼 상태는 `useForm({ resolver: zodResolver(schema) })`로 관리한다. 폼용 로컬 `useState` 난립 금지.
- RHF를 감싼 **도메인 form 훅**을 슬라이스의 `hook/` 세그먼트에 둔다 (`<slice>/hook/use<X>Form.ts`). submit 게이팅·mode(create/update) 분기는 이 훅에서(`policy-hook-extraction §3` L2).
- 디자인시스템 인풋(TextInput/Dropdown/TextArea/DateRangeField)은 **공용 `FormField` 어댑터**(`shared/ui/form/*`, 도메인 무지)를 통해 RHF에 연결한다. 어댑터 props는 계약이므로 `interface`.
- 폼은 `FormProvider`로 감싸고, `FormField`는 **`useFormContext`로 자기 필드 에러만 구독**한다(필드별 구독 — 폼 전체 error 객체를 사용처가 받아 배분하지 않는다).
- 필드 하단에 에러를 **빨간색 + 한글**로 표시한다. 실패 사유(null/정규식/min·max 등)는 zod 규칙별 메시지로 구분.
- **커스텀 제네릭 검증 훅(`useFormValidation`/`useFormCheck` 류 DSL)을 새로 만들지 않는다** — RHF+zodResolver가 그 역할이며, zod 재구현은 leaky abstraction(`policy-abstraction-strategy`).

### 제출/매핑/에러
- `required` 등 검증 실패는 **제출 자체를 차단**하고 에러를 즉시 노출(silent 금지).
- 검증 통과값 → 서버 DTO 매핑은 **명시적 payload 빌더(순수함수, `model`)** 로 (`recipe/data-dto` 연계). 암묵 변환 금지.
- 에러 메시지는 **한글로 zod message에 직접 작성**한다 (예: `.min(1, "필수 입력입니다")`).
- 입력은 payload 반영 전 필요한 `trim`/sanitize를 스키마 `transform`으로 처리.

## 금지

- zod 스키마 대신 컴포넌트/훅에 수동 `if` 검증을 새로 추가
- 폼 shape 타입을 스키마와 별도로 중복 선언 (`z.infer` 미사용)
- RHF 없이 폼 상태를 로컬 useState로 산발 관리 (계약형 폼)
- 스키마를 `ui/`에 두기 (검증 계약은 `model/`)
- 에러 메시지 하드코딩 / 검증 실패 silent 처리 / sanitize 없이 payload 삽입
