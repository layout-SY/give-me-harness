# 아키텍처 Q&A — 계약·추상화·결합·FSD 논의 정리

- 일자: 2026-05-07
- 참여: 사용자, 메인 에이전트
- 정리 기준: **사용자가 제기한 의문점·시나리오를 축으로**, 각 주제별로 사용자 질문과 핵심 답변 함께 보존

> 이 문서는 reason-prompt 작업 트랙 종료 후 진행된 일련의 아키텍처 토론을 주제별로 묶은 것이다.
> 1차 reason 모달 설계 토론과 2차 payload/searchState 일반화 토론은 별도 verbatim 문서로 보존되어 있다.
> - `.codex/logs/discussions/2026-05-07-1-reason-modal-design.md`
> - `.codex/logs/discussions/2026-05-07-2-payload-searchstate-generalization.md`

---

## 주제 1 — Page = Service 비유 (FSD vs Spring IoC/DI)

### 사용자 질문 (원문 요지)

> FSD 아키텍처나 스프링 백엔드의 전략 패턴(IoC 컨테이너/DI)을 기준으로 봤을 때, 어떤 페이지를 service(혹은 비즈니스 로직)으로 보고, 페이지에서는 UI를 제외한 TypeScript로만 볼 때 해당 페이지에서 사용되는 기능들을 페이지 자체에서 작성하는 것이 아닌 hook이나 utils에서 가져오는 방식이, 스프링 백엔드에서 보면 @Bean으로 등록되는 service 내에서 필요로 하는 기능들을 가져와 사용하는 방식과 같은 추상화/책임 분리 관점에서 적절한가?

### 핵심 답변

**비유 자체는 추상 수준에서 정합, 메커니즘 수준에서는 다름.**

#### 정합 지점
- FSD page-layer = "features/entities를 조립해 use-case를 완성하는 합성자(orchestrator)"
- Spring `@Service` = "여러 협력자(repository, util bean)를 주입받아 use-case를 구현하는 합성자"
- 두 정의 모두 "직접 일하지 않고 협력자를 모아 흐름을 만든다"는 본질을 공유

#### 비유가 깨지는 지점

| 축 | Spring `@Service` | React page |
|---|---|---|
| 라이프사이클 | 컨테이너 관리 싱글톤 | 매 렌더 함수 재실행 |
| 의존성 바인딩 | **런타임 주입(IoC)** | **정적 import(컴파일 타임)** |
| 호출 컨텍스트 | 어디서든 호출 가능 | hook은 렌더 함수 내부에서만 (Rules of Hooks) |
| 교체성 | `@Qualifier`/`@Profile` | Context Provider / props / factory hook |
| AOP | 프록시 기반 | HOC/wrapper hook (완전 대응 X) |

핵심: "hook/utils에서 import해서 합성"은 **IoC/DI가 아니라 modular composition**. 결과적 책임 분리 효과는 유사하지만 메커니즘은 다름. 진짜 IoC에 해당하는 React 도구는 Context Provider, Props, Hook Factory.

#### 적절성 결론

**적절** — page가 200줄+이고 query/mutation/UI state/handler 혼재 / 동일 use-case 다른 곳 재사용 / 검증·변환 jsx 인라인.

**부적절·과잉** — 단일 호출 핸들러를 굳이 hook 분리 / form local state까지 외부 hook 강제 추출 / 교체 가능성 없는데 Provider 도입.

#### 현실적 균형점 (synthoria-admin-ui)
1. 순수 로직 → utils (1순위)
2. 서버 상태·mutation → hook (2순위)
3. 진짜 교체 필요한 지점만 Provider/props 주입 (소수)
4. DI 컨테이너 라이브러리는 도입하지 않음 — 현 규모 과잉

#### Spring → React 매핑 충실도

| Spring | React/FSD | 충실도 |
|---|---|---|
| `@Service` | features hook + page orchestrator | 70% |
| `@Repository` | `apis/*.api.ts` + features gateway | 85% |
| `@Configuration`/`@Bean` | App-level Provider 트리 | 50% |
| 생성자 DI | Context value / props / hook 인자 | 50% |
| `@Qualifier` | Provider key / factory 인자 | 40% |
| `@Transactional` (AOP) | wrapper hook / HOC | 30% |
| 전략 패턴 | props injection / Provider / hook factory | 70% |

본질적으로 깨지는 지점: AOP, 런타임 빈 교체, 싱글톤 보장.

---

## 주제 2 — 프론트엔드 DI 라이브러리 존재 여부

### 사용자 질문

> 프론트에도 DI 라이브러리가 있어?

### 핵심 답변

**있음. 다만 백엔드만큼 보편적이지 않고 특정 시나리오에서만 채택됨.**

#### 주요 라이브러리

| 라이브러리 | 출처 | 특징 |
|---|---|---|
| **tsyringe** | Microsoft | 가벼움, 데코레이터 기반, TS 친화적 |
| **InversifyJS** | OSS | 가장 본격적. Spring과 가장 비슷한 경험 |
| **Awilix** | Jeff Hansen | 데코레이터 없이 함수/객체 등록 |
| **Brandi** | OSS | 경량 (~3KB), React Context와 결합 잘 됨 |
| **typed-inject** | OSS | 컴파일 타임 의존성 검증 |

프레임워크 내장: **Angular** (`@Injectable()`, Spring과 가장 유사), **NestJS** (Spring 사용자가 가장 익숙).

#### React에서 잘 안 쓰이는 이유
1. Context + custom hook으로 80% 커버
2. 함수형 컴포넌트 + hook 모델이 이미 합성 친화적
3. 번들 크기 부담 (InversifyJS + reflect-metadata)
4. JS 생태계의 모듈 mocking이 강력해 테스트 격리 동기 약함
5. 데코레이터 stage-3 이슈

#### 채택되는 케이스
- 대형 SPA + 환경별 구현 교체 잦음 (결제 게이트웨이, 로깅 transport)
- 백엔드 마인드셋 풀스택 팀 (NestJS + InversifyJS 통일)
- Clean Architecture / Hexagonal 엄격 적용
- Storybook/테스트 mock 비용이 큰 경우

#### synthoria-admin-ui에는 도입 불필요
- 관리자 SPA 규모에선 Context Provider + custom hook factory로 충분
- `apis/*.api.ts`는 환경별 교체 수요 없음
- 도입 비용 > 이득
- 다만 **gateway 패턴**(apis 위 도메인 메서드 모음)은 DI 없이도 도입 가능, 미래에 필요해지면 그 시점에 Provider/factory만 추가

---

## 주제 3 — Hook 분리 시 추상화가 필요한 시점

### 사용자 질문

> hook으로 분리될 때 페이지는 기능에 대해서, hook은 기능에 대한 구현을 정의하는 방식으로 이루어지는데, 이 때 추상화가 필요한 시점은 뭐야? 추상화가 이 둘의 추상적 기능 정보를 명시해놓는 게 추상화야? 만약 그렇다면 특정 도메인에서 사용되는 hook의 경우엔 어차피 둘 간에만 이루어지는 계약이기 때문에 별도로 추상화가 필요할 거 같진 않고, 공용 컴포넌트나 hook의 경우엔 호출자가 역으로 공용 컴포넌트나 hook에 대한 추상화 정보를 보고 계약을 하는 개념으로 보이는데, 맞아?

### 핵심 답변

**계약(contract) ≠ 추상화(abstraction).**

| 구분 | 정의 | 예 |
|---|---|---|
| **계약(interface)** | 시그니처 + 입출력 타입 + 호출 규약 | `useReasonPrompt({ title, callback }): { open }` |
| **추상화(abstraction)** | 계약 + **정보 은닉** + **불변식** + **대체 가능성** | "reason 입력 모달은 도메인을 모른 채 reason만 비동기로 산출한다" |

함수 분리 → **계약은 자동 생성**, 추상화는 **의식적 작업**.

#### 추상화가 비용을 정당화하는 4가지 조건
1. **소비자가 둘 이상**
2. **구현이 둘 이상**(현재 또는 가까운 미래) — 환경별, 정책별, 전략 패턴
3. **불안정한 영역에 안정 경계가 필요할 때** (내부는 자주 바뀌지만 외부 계약 유지)
4. **인지 부하 감소가 ROI 있는 규모** (구현이 100줄+이면 호출자 1개여도 가치)

→ 어느 것도 충족 안 되면 **추상화는 오버헤드**, 계약(시그니처)만으로 충분.

#### 사용자 가설 검증

**"도메인 hook은 추상화 불필요"** — 대체로 맞음. 단서:
- 같은 도메인 내 호출처 둘 이상 → 사실상 mini-public, 추상화 필요
- 구현이 비자명 → 호출자가 안 봐도 쓸 수 있어야 ROI
- 미래 다른 도메인 가능성 → 시그니처 위생만이라도 챙기기

**"공용 hook은 호출자가 추상화 정보 보고 계약"** — 정확. 단 **인과 방향 주의**:
- 공용 hook: publisher가 **추상화를 먼저 설계**, 호출자들이 순응 (publisher mindset)
- 도메인 hook: 사용 패턴이 먼저 존재, 거기서 hook 추출 (refactor mindset)
- 둘 다 결국 추상화를 만들지만 동기와 엄격도가 다름

---

## 주제 4 — 사용자가 정리한 추상화 모델 (DIP 발견)

### 사용자가 정리한 시나리오

> 도메인에 종속된 hook이라도 호출자가 둘 이상이면, 두 호출자 중 특정 호출자에게 종속되지 않고 독립성을 갖게 구현해야 하고, 이를 위해 두 호출자와 hook 간 추상적 계약으로 "이렇게 사용하고, 이런 기능이야"를 약속하는 것. 이 때 마치 의존성 역전처럼 hook이 기능 추상화로 설계되고 호출자가 받아 사용하는 관계.
> 
> 특정 도메인에서만 사용되는 hook(usePostDetail 등)은 호출자가 직접적으로 hook의 구현 목적이 되므로 굳이 추상화 불필요.
> 
> 이 관계는 페이지/컴포넌트뿐 아니라 hook이 호출자인 상황에서도 동일.

### 핵심 답변

**대체로 정확. 세 군데 보정하면 완성.**

#### 1. "의존성 역전 개념이랑은 다르지만" — **사실 맞음**

사용자 그림은 정확히 **DIP(Dependency Inversion Principle)**, SOLID의 D.

DIP의 두 명제:
1. 상위 모듈은 하위 모듈에 의존하지 않는다. 둘 다 추상에 의존한다.
2. 추상은 세부 구현에 의존하지 않는다. 세부 구현이 추상에 의존한다.

사용자 표현:
- "각 호출자와 직접 종속되면 안 됨" → 명제 1
- "hook이 추상화로 설계되고 호출자가 받아 사용" → 명제 2

완전 일치. 다만 백엔드 IoC 컨테이너의 **런타임 주입 메커니즘**이 React에 없을 뿐, **원칙은 그대로 적용**.

#### 2. 계약 표현 수단 (interface 외)

| 수단 | 강제력 | 용도 |
|---|---|---|
| `interface` / `type` | 컴파일 타임 | 가장 흔함, 구조적 타이핑 |
| **함수 시그니처 자체** | 컴파일 타임 | 별도 선언 없이 함수 타입이 곧 계약 |
| Branded/Nominal types | 컴파일 타임 | `UserId` vs `PostId` |
| Discriminated union | 컴파일 타임 | 조건부 계약 |
| Generic 제약 (`<T extends X>`) | 컴파일 타임 | 다형성 계약 |
| JSDoc | 문서/IDE | 타입 외 불변식·부수효과 |
| Zod / Yup 스키마 | 런타임 | 외부 입력 경계 |
| 테스트 코드 | 런타임 (CI) | 행위적 계약 |
| 추상 클래스 + DI | 런타임 | DI 라이브러리 |
| Module 경계 (export shape) | 컴파일 타임 | barrel export로 노출 표면 좁힘 |
| Provider + Hook | 런타임 | React식 DI |

실무에서 React hook은 **함수 시그니처 + (필요 시) interface/type + JSDoc** 조합이 표준.

추가 강조:
- 반환 타입을 명시적으로 선언 → 작은 추상화 시작점
- 공용 hook은 입력 타입을 별도 export 거의 필수 (`OpenReasonPromptOptions`)

#### 3. 단일 호출 hook도 "계약은 존재"

- **계약은 항상 있음** (시그니처 = 계약, 분리 즉시 자동 발생)
- **추상화 *작업*은 없어도 됨** (invariant 정의, 별도 interface 선언, 문서화)
- 그래도 **시그니처 위생은 챙겨야 함** — 두 번째 호출처 생길 때 공용 hook 승격 비용 절감

휴리스틱: **"두 번째 호출처가 생기는 순간"이 도메인 hook → 공용 hook으로 추상화 엄격도를 올리는 자연스러운 트리거.**

---

## 주제 5 — 계약과 추상화의 명확한 분리

### 사용자가 정리한 시나리오

> 계약은 어떤 기능을 위해 import 되는 것 자체가 계약이라고도 볼 수 있는 거야. Modal.tsx 컴포넌트에서 useModal.ts hook을 import 하는 것 자체로도 계약.
> 
> 단, useModal.ts가 Modal.tsx + DomainModal.tsx 양쪽에서 사용된다면 동일한 기능 제공 명세가 필요하며, 각자 useModal.ts에 제공하는 정보와 useModal.ts가 반환하는 정보를 일치시키고, useModal.ts의 구현이 변경되어도 계약이 변경되지 않는 구성과 사용처들이 기능 맥락만 파악해 동작하는 흐름이 추상화가 완료된 시점.

### 핵심 답변

**거의 정확. 두 군데 다듬어야 정확한 정의.**

#### 1. "import 자체가 계약" — 비유로는 OK, 엄밀히는 아님

| 개념 | 정의 |
|---|---|
| **Import** | "이 모듈을 사용하겠다"는 **의존성 선언** |
| **Contract** | "이 입력에 이 출력, 이 부수효과"라는 **형태/행위 명세** |
| **Implementation** | 그 명세를 어떻게 달성하는가 |

import는 "useModal의 contract에 합의한다"는 **약속의 이행**, contract 자체는 아님. Contract는 함수 시그니처(타입) + 문서화된 행위에 박혀 있음.

다만 TypeScript 환경에서는 **import하는 순간 시그니처(=contract)도 함께 따라옴**. 실무적으로는 "import = contract 합의"로 봐도 무방.

표현 정리:
- import = contract에 대한 **합의(commitment)**
- contract = 시그니처와 문서에 박힌 **명세**
- abstraction = 그 명세가 **여러 호출자와 미래 구현 변화에도 안정**된 상태

#### 2. "input/return을 일치시킨다" — **abstract level에서 일치**해야 함

**잘못된 해석 (X)**: 두 호출자가 완전히 동일한 값을 넘기고 동일한 값을 받는다.

**올바른 해석 (O)**: 두 호출자가 **동일한 contract 구조**(시그니처, 타입 형태, 행위 규약)에 맞춰 호출. **구체적 값은 다를 수 있음.**

```ts
useModal({ initialData: User })   // Modal.tsx
useModal({ initialData: Post })   // DomainModal.tsx

function useModal<T>({ initialData }: { initialData: T }): {
  data: T;
  open: () => void;
  close: () => void;
};
```

추상화의 핵심은 **"호출자별 차이를 contract 안에 흡수할 수 있는 형태"** 로 contract를 설계하는 것. 도구:
- Generic (`<T>`)
- Discriminated union
- Optional 필드 + default
- Strategy parameter

#### 3. 추상화 완성도 정의 (보정 후)

> 추상화가 "완료에 가까워진" 시점:
> 1. hook에 호출자가 둘 이상이고,
> 2. 모든 호출자가 **동일한 contract**에 합의 (각자 구체 값은 달라도 contract 형태는 일치),
> 3. contract는 호출자별 차이를 **변수/제네릭/유니언으로 흡수**할 표현력을 갖고,
> 4. 내부 구현이 바뀌어도 contract가 유지되어 호출자 코드를 손대지 않으며,
> 5. 호출자는 contract만 보고도 충분히 이해 가능 — 구현을 읽을 필요 없음.

보정:
- "완료" → "완료에 가까워진" 또는 "현재 호출자 집합에 대해 안정적인" — 추상화는 binary가 아닌 gradient
- 5번이 핵심: **"구현을 읽지 않아도 쓸 수 있는가"** = 추상화 완성도의 실용적 척도. 자꾸 내부를 들여다봐야 한다면 leaky abstraction.

---

## 주제 6 — 함수 시그니처가 import에서 어떻게 작동하는가

### 사용자 질문

> 함수 시그니처를 가져온다는 표현이 너무 모호해. import 할 때 함수 시그니처를 가져온다는 건 해당 함수에서 사용될 파라미터 정보가 type으로 같이 넘어오기 때문에 그에 맞게 사용처에서는 type에 맞게 데이터를 제공해야 한다. 이런 흐름이 함수 시그니처 자체를 같이 가져온다는 개념이야?

### 핵심 답변

**정확히 그 개념. 다만 양방향(인자 + 반환).**

#### 함수 시그니처의 정확한 정의

함수의 **타입 정보**:
- 파라미터 이름과 타입
- 반환 타입
- 제네릭 제약 (`<T extends X>`)
- (드물게) `this` 타입, 오버로드

**구현 본문은 시그니처에 포함되지 않음.** 시그니처는 "어떻게 호출하고 무엇을 받는가"만 기술.

#### import 시 시그니처 전파 — 두 층위

**런타임 (실제 실행)**
```ts
import useModal from "./useModal";
```
함수 값(=구현)만 옴. JavaScript는 타입 정보 없음. 런타임에 시그니처는 존재하지 않음.

**컴파일 타임 (TypeScript 검사)**

```ts
// useModal.ts
export default function useModal<T>(options: {
  initialData: T;
  onClose?: () => void;
}): {
  data: T;
  isOpen: boolean;
  open: () => void;
  close: () => void;
} {
  // ... 구현
}
```

```ts
// Modal.tsx
import useModal from "./useModal";

const { data, open } = useModal({ initialData: { id: 1 } });
//                              ^^^^^^^^^^^^^^^^^^^^^^^^^
// 타입 검사기가 useModal 시그니처 적용:
//   - options 객체에 initialData 있는지
//   - data 반환 타입이 { id: number }인지
```

타입 검사기가 보는 것은 **시그니처뿐**. 함수 본문은 호출자 입장에서 검사 시 무관. 호출자는 **시그니처만 알면** 안전하게 사용 가능 — 추상화 작동 원리.

#### 보강

사용자 정의는 정확. 한 가지 보강:
- **파라미터뿐 아니라 반환 타입도 함께 따라옴**
- 인자 타입 → 호출자가 제공할 값의 형태
- 반환 타입 → 호출자가 받게 될 값의 형태
- 양방향이 모두 시그니처

#### `.d.ts` 분리 예

```ts
// useModal.d.ts (타입만, 시그니처만)
export default function useModal<T>(options: {...}): {...};
```
```js
// useModal.js (구현만, 시그니처 없음)
export default function useModal(options) { /* ... */ }
```

→ 시그니처 = **함수 본문 없이 호출 규약만 기술한 부분**

#### 한 줄 요약

> "함수 시그니처를 가져온다" = **import한 함수의 호출 규약(파라미터 타입 + 반환 타입 + 제네릭 제약)이 컴파일 타임에 호출자에게 전파되어, 호출자가 그 규약에 맞게 코드를 작성하도록 타입 검사기가 강제한다.**

---

## 주제 7 — Table 컴포넌트의 추상화 분석 (실제 사례)

### 사용자가 제시한 시나리오

> `src/components/table/table.tsx`와 사용처 관계를 봤을 때, 사용처들이 필요로 하기 때문에 Table 컴포넌트가 존재하지만 특정 사용처에 종속되는 순간 문제가 생기기 때문에 Table 자체적으로 계약 관계를 정의하고, 사용처들이 그 계약 관계에 따라 props를 정의하는 것이 추상화. 사용처에서는 기능에 필요한 데이터를 props로 넘기고, Table에서는 받은 데이터를 기능에 적절하게 사용하되 데이터의 구체적 정보를 모르는 형태로 구현된다면 이게 컴포넌트 추상화 관계?

### 핵심 답변

**정확. 그리고 이 Table은 잘 추상화된 컴포넌트의 교과서적 예시.**

#### 추상화 증거

**1. 제네릭 `<TRow>` — 데이터 타입을 모름**
```ts
type TableProps<TRow> = {
  columns: TableColumnDef<TRow>[];
  rows: TRow[];
};
```
Table은 `TRow`가 무엇인지 모름. User든 Post든 DaoDiscussionPost든. 호출자가 타입 박아주고, Table은 **그 타입을 일급으로 취급하지만 내부 구조는 들여다보지 않음**.

**2. `column.accessor` — 데이터 추출을 호출자에게 위임**
```ts
case "accessor": {
  renderedCell = commonCell({
    row,
    type: column.type,
    value: column.accessor({ row, rowIndex }),  // 호출자 정의 함수
  });
}
```
Table은 `row.id`, `row.name` 같은 구체 필드를 직접 읽지 않음. 호출자가 column 정의에 `accessor: ({ row }) => row.userName`처럼 박아주고, Table은 호출만 함. **전형적 전략 패턴.**

**3. `column.cell` — 렌더링 자체도 위임**
```ts
case "custom":
default: {
  const context: TableCellContext<TRow> = { row, rowIndex, column, ... };
  renderedCell = column.cell(context);  // 호출자가 JSX 결정
}
```
custom 컬럼은 **JSX 생성 자체를 호출자가 결정**. Table은 컨텍스트만 모아 넘기고 렌더 결정은 모름.

**4. `column.kind` 분기 — 추상화 안의 다형성**
Discriminated union으로 컬럼 종류 분기. Table은 종류별 협력자(accessor/cell/onOpenDetail) 호출 방법만 알고, 협력자 자체는 모름.

**5. 그 외 전략 주입 슬롯들**
- `getRowClassName?` — 행별 클래스명 결정 전략
- `handler?` — 페이지 변경 전략
- `emptyContent?` — 빈 상태 UI 전략

#### 추상화 완성도 척도

| 척도 | 충족 여부 |
|---|---|
| 호출자 둘 이상 | ✅ |
| 새 호출자가 Table 수정 없이 도입 가능 | ✅ |
| 내부 구현 변경이 호출자에 영향 X | ✅ |
| 호출자가 본문 안 읽고 사용 가능 | 거의 ✅ |
| 호출자별 차이를 contract가 흡수 | ✅ (제네릭 + DU + 슬롯) |

다섯 척도를 거의 만점으로 통과 — **사용자 정의 "추상화"의 살아있는 예시**.

#### 미세 누수 지점

```ts
<th className="..."><span>index</span></th>
```
`"index"` 문자열 하드코딩 — 다국어 환경에서 호출자가 못 바꿈. 레이아웃 책임 안에 도메인성(언어)이 살짝 새어나온 지점.

또 `commonCell({ row, type, value })`에 `row` 자체가 넘어가는데, commonCell 내부에서 `row` 특정 필드를 읽으면 그 시점에서 추상화가 깨지기 시작. 보통 commonCell도 `value`만 쓰도록 만드는 게 정석.

---

## 주제 8 — commonCell의 도메인 결합 / 추상화 누수 판별

### 사용자 의문 (1차)

> commonCell은 테이블에서 각 사용처마다 공통 사용되는 컴포넌트들을 모아놓은 함수인데, 여기에서 row를 사용하게 되면 사용처에 대한 정보가 노출되기 때문에 Table 자체적으로 존재하는 value에 값을 담아 제공하는 것이 옳은 거지? 그러면 commonCell 함수는 각 사용처에서 공용으로 사용되는 셀 정보를 담아 놓은 건데 이렇게 되면 사용처와 Table 간 추상화 전략이 commonCell에 특정 사용처 몇 개에서 사용되는 도메인 정보가 노출되는 거 아니야?

### 핵심 답변

**날카로운 지적. 두 층의 추상화가 있고, layer마다 누수 판단이 다름.**

```
호출자 ──contract A──▶ Table ──contract B──▶ commonCell
```

- **Layer A (Table ↔ 호출자)**: 잘 분리됨. 제네릭 + accessor/cell 슬롯으로 도메인 차단.
- **Layer B (Table ↔ commonCell)**: 따로 봐야 함.

#### commonCell의 추상화 누수 판별 기준

commonCell = "공용 셀 종류의 어휘집(vocabulary)". 누수 여부는 **어휘의 성격**으로 결정.

**누수 아님 (안전한 어휘)**

`column.type`이 **UI primitive**만 담음:
- `"text"`, `"date"`, `"number"`, `"link"`, `"badge"`, `"avatar"`, `"open_detail"`

→ **렌더링 형태**의 분류, 도메인 의미 X. 어떤 도메인이든 필요. 디자인 시스템 typography catalog과 같음.

**누수임 (도메인 어휘)**

`column.type`에 **도메인 의미** 박힘:
- `"user_name_with_avatar"`, `"proposal_status_pill"`, `"discussion_post_id"`, `"dao_role_badge"`

→ commonCell이 **특정 도메인의 어휘를 학습**. 새 도메인마다 case 추가, commonCell이 점점 "프로젝트의 모든 도메인을 아는 신"이 됨. **추상화 깨지는 임계점.**

#### `row`를 commonCell에 넘기는 것 — 두 번째 누수

```ts
commonCell({ row, type, value });  // row는 누수 위험
```

이상적으로:
```ts
commonCell({ type, value });  // accessor: value만 충분
```

`row`가 commonCell까지 흘러가면 내부에서 `row.someField` 읽고 싶은 유혹 발생. 그 순간 추상화 무너짐. **`row`는 column.accessor에서 끝나고 추출된 `value`만 흘러야** 깔끔.

#### 추상화 깨지 않으면서 도메인 셀 다루는 정공법

**정답 1: 도메인 셀은 호출자가 `custom` kind로 직접**
```ts
{ kind: "accessor", type: "text", accessor: ({ row }) => row.title }   // 공용 어휘
{ kind: "custom", cell: ({ row }) => <AuthorBadge user={row.author} /> }  // 도메인 셀
```
`custom` kind는 **"여기서부터는 너의 도메인이니 네가 결정해라"** 는 추상화 탈출구.

**정답 2: 자주 쓰이는 도메인 셀은 별도 레이어에 도메인 컴포넌트로**
```
shared/ui/Table         ← 순수 레이아웃, commonCell도 UI primitive만
entities/user/ui/UserCell, AuthorBadge   ← 도메인 셀 (FSD entities)
features/.../column-defs.ts              ← UserCell을 column.cell에서 사용
```

#### 판별 한 줄

> **commonCell의 `type` union에 새 항목 추가할 때, 그 이름이 "UI 형태의 이름"이면 안전, "도메인 개체의 이름"이면 누수.**

예:
- `"badge"` 추가 → 안전
- `"user_role_badge"` 추가 → 누수 → `custom` kind로

---

## 주제 9 — 단방향 체이닝과 약한 추상화 / commonCell이 사용처와 결합되는가

### 사용자 의문 (2차, 3차)

> 어차피 흐름은 단방향 체이닝이기 때문에 사용처 → table → commonCell이어서 table → commonCell 둘 간에 관계에서 table의 정보가 commonCell 내부에서 직접적으로 사용되는지 여부만 판단하면 된다는 거잖아. 거기다가 현재 이 케이스가 table이라는 특정 도메인에만 종속하는 함수인 commonCell, 이에 대해선 사용처 → table 간 관계에서 정의했던 columnDef와 같은 구체적 계약 관계 정의를 통한 추상화 같은 작업은 과하게 되는 거고, table의 정보가 commonCell에 직접적으로 포함되지만 않는다면 사용처 → table 간 강한 추상화 관계만큼은 아니지만 table → commonCell에서도 유지보수성을 갖는 약한 수준의 추상화를 가지게 되는 거네?
> 
> 근데 commonCell은 사용처와의 관계에서 어떤 도메인에 종속되지 않은 공용 사용처에 대한 셀 정보가 추가/수정/삭제 된다고 했을 때 사용처에 대한 정보 수정이 연쇄적으로 발생하는 구조를 가지고 있어. 이는 commonCell와 사용처 간 결합도를 의미하고, 이는 commonCell이 사용되는 table 컴포넌트와 사용처 간 결합도로도 연결지을 수 있어?

### 핵심 답변

**세 인식 모두 정확. 마지막이 가장 날카로운 통찰.**

#### Q (단방향 체이닝, 약한 추상화) — 정확

```
사용처 ──[강한 계약: TableColumnDef<TRow>]──▶ Table ──[약한 계약: CommonCellProps]──▶ commonCell
```

- **사용처 ↔ Table**: 둘이 서로를 모르는 상태에서 만나야 함 → **강한 추상화** 필요 (제네릭, 전략 슬롯, 도메인 무관 contract)
- **Table ↔ commonCell**: commonCell은 `src/components/table/utils/`의 **Table의 사적 구현 보조 도구**. **같은 모듈**의 일부, Table만 호출자. 사용처 ↔ Table 수준의 contract 엄격도 적용 시 **과잉 엔지니어링**
- 약한 추상화 조건: **Table 내부 상태(sticky, pagination, layout)가 commonCell에 누설 X**, **commonCell이 Table 다른 부분에 도달 X**

현재 commonCell 시그니처:
```ts
{ row, type, value, placeholder } | { row, type: "open_detail", onOpenDetail }
```

Table의 sticky/pagination/layout 상태가 commonCell에 한 톨도 안 들어감 → **약한 추상화 조건 만족.**

다만 `row`가 들어있는 점은 누수 위험 신호이고, `case "open_detail"`에서 `<OpenDetailActionCell row={props.row} />`로 row를 자식 컴포넌트에 흘려보내고 있음. OpenDetailActionCell이 row 특정 필드 읽는다면 추상화 깨지기 시작.

#### Q (commonCell-사용처 결합 → Table-사용처 결합) — 가장 날카로운 통찰

**네, 결합되며, 이건 *의도된* 결합.**

##### 결합의 정확한 경로

commonCell은 Table 내부에 숨겨진 듯 보이지만, **타입 어휘가 외부로 새어나가 있음**:

```
commonCell.tsx
  ↓ defines case "status", "date", ... via CellValueMap
columnDef.ts  
  ↓ TableColumnDef<TRow>의 column.type이 CellValueMap의 키 사용
table.tsx
  ↓ TableProps<TRow>에 columns: TableColumnDef<TRow>[] 노출
사용처
  ↓ column 정의 시 type: "status" 등 직접 작성
```

→ commonCell의 **type 어휘가 TableColumnDef를 통해 사용처까지 그대로 노출**. 물리적으론 숨어있지만 **타입 시스템 상 public API의 일부**.

##### 변경 영향

- 새 case `"currency"` 추가 → CellValueMap 키 추가 → 사용처가 새 타입 사용 가능 (additive, 호환)
- `"numbering_text"` 제거/이름 변경 → CellValueMap 변경 → **그 타입 쓰던 사용처 모두 컴파일 에러** (breaking)
- case 동작 변경 (예: date 포맷) → 시그니처는 같지만 **모든 호출처 화면이 한 번에 변함** (silent change)

##### Table-사용처 결합으로 이어지는가 — 네

`TableColumnDef<TRow>`의 `column.type` 필드 타입이 commonCell 어휘에 **참조 의존**. 사용처가 보는 contract(`TableProps<TRow>` → `TableColumnDef<TRow>`)는 Table 자체의 contract지만, **그 안에 commonCell의 어휘가 박혀있어** commonCell 변경이 Table contract 변경으로 **전파**.

이는 OOP **인터페이스 안정성(interface stability)** 문제와 동일. Spring의 `@Service` 인터페이스에 새 메서드 추가하면 모든 구현체가 영향받는 것과 같은 메커니즘.

##### 나쁜 결합인가? 아니다

**closed vocabulary 디자인이 가지는 본질적 비용**:

| 디자인 | 사용처 ergonomics | 결합도 / 안정성 |
|---|---|---|
| **Closed union** (현재 commonCell) | 좋음 — `type: "status"`만 쓰면 됨 | 높음 — vocabulary 변경이 모든 사용처에 전파 |
| **Open extension** (custom kind) | 나쁨 — 매번 cell JSX 작성 | 낮음 — 사용처별로 격리 |

현재 Table은 **둘 다 제공**:
- 자주 쓰이는 셀 → `kind: "accessor"` + `type: "status"` (closed vocabulary, 결합 감수)
- 도메인 특수 셀 → `kind: "custom"` + 호출자가 직접 cell 작성 (open extension, 결합 없음)

**이원화가 디자인의 핵심**, 추상화 누수가 아니라 **의도된 결합 트레이드오프**.

##### 관리 방법

받아들이되 관리:
1. **CellValueMap을 versioned API surface로 취급**: case 이름 변경/제거는 메이저 변경. 추가는 안전.
2. **case 추가 기준 엄격히**: "둘 이상의 도메인이 정확히 같은 모양으로 쓰는가" 통과 조건. 한 도메인만이면 `custom`.
3. **case 시각적 출력 고정**: 외형 변경은 모든 사용처를 의식.
4. **도메인 종속 의심되는 case 분리**: `"author"`, `"category"`처럼 dao 가까운 어휘는 commonCell에서 빠져 도메인 컴포넌트로 가야 깔끔 (현재 일부 도메인 냄새 섞임).

---

## 주제 10 — 계약 변경 = 큰 변경

### 사용자가 정리한 인식

> 그러니까 내가 제시한 시나리오의 경우엔 계약 자체의 변화라고 간주하는 거고, 이러한 변경에 대한 계약 관계에 포함된 각 도메인들은 어쩔 수 없는 결합에 의한 수정을 겪을 수 밖에 없단 거지? 한마디로 이러한 시나리오는 큰 변경이라고 볼 수 있는 거네? 계약 자체에 변화인거니까.

### 핵심 답변

**정확. 그리고 이 인식이 추상화 설계에서 가장 중요한 운영 감각.**

#### 계약 변경의 종류 (모두 같은 "큰 변경"은 아님)

| 변경 유형 | 계약 영향 | 사용처 영향 | 비유 |
|---|---|---|---|
| **추가(additive)** | contract 확장 | 영향 없음 (옵트인) | SemVer minor |
| **파괴(breaking)** | 기존 contract 깨짐 | 모든 사용처 강제 수정 | SemVer major |
| **행위(behavioral)** | 시그니처 동일, 동작만 변경 | 컴파일 통과하지만 화면/로직 조용히 바뀜 | "사일런트 회귀" |

commonCell 시나리오 분류:
- 새 case `"currency"` 추가 → **additive** (안전)
- `"numbering_text"` 제거/이름 변경 → **breaking** (큰 변경)
- `"date"` 포맷 변경 → **behavioral** (조용한 큰 변경, 더 위험)

#### 사용자 표현 다듬기

> "계약 자체의 변화이기 때문에 각 도메인은 어쩔 수 없는 결합에 의한 수정"

→ **breaking change**에 한정해서 정확. additive는 결합이 있어도 수정 강제 X. behavioral은 코드 수정은 없지만 영향이 가장 광범위 → **테스트/검토 비용** 발생.

#### 추상화의 가치 한 줄

> **"안정된 contract는 자산이고, contract 변경은 부채를 즉시 가시화한다."**

추상화의 진짜 가치는 "구현을 숨긴다"가 아니라 **"contract를 바꾸지 않는 한 사용처가 안전하다는 보장"**. 그래서:
- contract 처음 설계할 때 **변경이 잦을 축**(셀 종류 등)을 generic/DU/슬롯으로 흡수해두면 → 미래 변경이 additive 영역에 머무름
- contract 표면에 **고정 어려운 것**(도메인 특수 셀)을 박아넣으면 → 변경 잦고 매번 breaking

현재 Table-commonCell 구조가 잘 만들어진 이유:
- closed vocabulary(`column.type`)는 안정 어휘만 담음 → 추가가 주된 변경 패턴
- 도메인 특수 셀은 `custom` kind로 외부화 → contract에 영향 X
- 두 트랙으로 변경 빈도 분리 → contract 안정성 확보

#### 운영 휴리스틱

1. **분리하는 순간 contract가 생긴다** (자동)
2. **두 번째 사용처가 생기면 contract가 자산이 된다** (안 깨면 가치 ↑)
3. **contract 변경은 모든 사용처의 비용으로 환산된다.** 변경 비용 = (사용처 수) × (변경 종류 비용)
4. **contract를 처음 설계할 때 "어디가 자주 바뀔지" 예측해 흡수 가능한 형태로** — generic, union, slot, callback의 존재 이유
5. **그럼에도 breaking 변경이 불가피하면 그건 "큰 변경"이고, SemVer major처럼 의식적으로 다뤄야 함**

---

## 정리: 사용자가 도달한 핵심 인식 5가지

본 토론 시리즈를 통해 사용자가 정립한 멘탈 모델:

1. **계약(contract) ≠ 추상화(abstraction)**
   - 분리 = 계약 자동 발생
   - 추상화 = 의식적 작업, 4가지 조건 충족 시에만 비용 정당화

2. **추상화는 DIP(의존성 역전 원칙)와 동일**
   - 호출자가 hook에 의존하지 않고, 둘 다 추상에 의존
   - React에서는 정적 import + TypeScript 시그니처 + (필요 시) Provider/factory로 구현
   - DI 라이브러리는 보통 불필요

3. **계약은 abstract level에서 일치, concrete level이 아님**
   - 사용처별 차이는 generic/DU/슬롯/optional로 흡수
   - 호출자가 구현을 안 읽어도 사용 가능 = 추상화 완성도

4. **단방향 체이닝에서 약한 추상화도 충분**
   - 같은 모듈 내부 helper는 강한 contract 엄격도 불필요
   - 누수 조건(상위 정보가 하위로 흘러들어가지 않음)만 지키면 됨

5. **closed vocabulary의 결합은 의도된 비용**
   - 어휘 변경 = 계약 변경 = 큰 변경 (breaking change)
   - additive / breaking / behavioral 세 종류로 분류
   - 추상화 설계의 목표 = "잦은 변경을 additive 영역에 몰아넣고, breaking은 드물고 의식적으로만"
