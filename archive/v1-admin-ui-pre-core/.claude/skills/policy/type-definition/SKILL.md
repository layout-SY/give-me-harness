---
name: policy-type-definition
description: synthoria-admin-ui에서 타입을 선언할 때 interface와 type 중 무엇을 쓸지 결정하는 횡단 규약. props·콜백·hook 반환·레이어 경계 등 "두 관계 간 계약"을 표현하면 interface, 그 외 데이터 형태/유니온/파생은 type. 계약 타입·파라미터/props 타입 지정 시 항상 적용.
---

# Type Definition (Policy)

## 언제 이 스킬을 사용하나요?

- props / 콜백 / 이벤트 인터페이스 등 컴포넌트 계약을 선언할 때
- hook 반환 타입, api client 계약, DTO·레이어 경계 타입을 선언할 때
- 파라미터·반환값 타입을 새로 정의하거나 리팩터 중 계약을 뽑아낼 때

---

## 핵심 규칙 — 계약이면 `interface`, 아니면 `type`

> **판단 기준(단 하나)**: 이 타입이 **두 관계(당사자) 간의 계약 상태**를 나타내는가?
> - **그렇다 → `interface`** (계약은 확장·구현·선언병합의 대상이 되는 안정 경계)
> - **아니다 → `type`** (데이터의 형태/조합/파생을 표현하는 값 수준 별칭)

### `interface` — "계약"인 경우
당사자 A ↔ B 사이의 약속을 정의하는 객체 형태 타입.

| 계약 사례 | A ↔ B |
| --- | --- |
| 컴포넌트 **Props** / 콜백 props | 부모 ↔ 자식 |
| **이벤트/콜백 인터페이스** | 발행자 ↔ 구독자 |
| **hook 반환 계약** | hook ↔ 호출부 |
| **api client / service 계약** | 호출부 ↔ 클라이언트 추상화 |
| **DTO(요청/응답 경계)** | 서버 ↔ 클라이언트 (또는 레이어 ↔ 레이어) |
| **확장/선언병합이 예정된 공개 경계** | 예: `PubSubEvents` (도메인 레이어가 `declare module`로 확장) |
| 모듈 간 **핸드오프 계약** | UI 컴포넌트 props 인터페이스, event interface points |

### `type` — "계약이 아닌" 경우
관계가 아니라 데이터 자체의 형태/조합/파생을 표현.

- **유니온 / 인터섹션** (`"start" | "end"`, `A | B`) — 애초에 interface로 표현 불가
- **매핑 / 조건부 / 유틸리티 타입** (`Partial<T>`, `Omit<...>`, `[K in Keys]`)
- **값에서 파생** (`typeof x`, `keyof T`, `ReturnType<...>`)
- 로컬 임시 shape, primitive 별칭, 단순 데이터 컨테이너

---

## 우선순위 & 경계

- **강제 조건 우선**: 유니온/매핑/조건부/파생은 계약처럼 보여도 **무조건 `type`** (interface로 불가능).
- **계약이면 객체 형태로 뽑아 `interface`**: props·hook 반환·경계 DTO는 union이 아닌 한 interface.
- 애매하면 "이 타입에 나중에 필드가 **추가/확장/구현**될 관계인가?"를 물어라 — 그렇다면 계약(interface).

---

## 금지

- props·콜백·hook 반환·경계 DTO 같은 **계약을 `type`으로** 선언 (계약 확장성 상실)
- 유니온/매핑/파생을 억지로 interface로 우회
- 같은 개념을 파일마다 interface/type 혼용 (일관성 위반)
