# 2차 — searchState/payload 일반화에 대한 아키텍처 논의 (verbatim)

- 일자: 2026-05-07
- 참여: 사용자, 메인 에이전트
- 추가 정리 없이 원문 그대로 보존

---

## [사용자]

지금 각 도메인들(페이지 or 컴포넌트)을 보면 searchState으로 된 요청 쿼리 파라미터나 payload로 된 요청 body들이 각 도메인별로 hook 없이 구현 되어 있는 걸 확인할 수 있어.
그러니까 내가 구상한 건 지금 reason을 return하는 별도 hook이 있는 것처럼 searchState나 body를 구성하는 별도 hook이 존재하고(지금 도메인처럼 payload가 작은 경우엔 도메인 자체적으로 처리할 수도 있긴 하지만), 규모가 큰(5개 이상 항목) searchState나 body 구성에 대해선 해당 도메인이 직접 구현하는 게 아닌 각 도메인에서 어떤 searchState나 body 구성이 필요한 지(기능만) 제공하고, 해당 hook에선 searchState/body 구성에 필요한 로직과 reason과 같이 별도 사용자의 입력을 통해 받아와야 하는 내용에 경우 별도 hook을 호출해서 구현되면 해당 searchState/body를 return하고, 도메인은 이를 받아 요청하는 hook에게 제공하는 방식으로의 작업 방식을 구상해봤어.

간단하게 예를 들면 body에 경우 일부 도메인에선 같은 ui 컴포넌트 구성에 생성/수정이 동시에 혼재된 경우가 있어. 물론 해당 ui 컴포넌트가 동일한 경우이기 때문에 ui 재사용 목적으로는 괜찮지만, 로직 자체가 복잡하게 혼재되어 있는 게 문제인거야. 이런 경우에 생성 전용 요청 body 구성 hook/수정 전용 요청 body 구성 hook을 구현해놓고(해당 도메인 종속 hook이던, 글로벌 hook이던) 도메인에서 요구하는 기능 사항을 해당 hook에 제공하면 이에 적절한 payload가 return 되어 이를 요청 hook(지금은 해당 도메인 파일 자체에 명시되어 있는)에 제공하는 방식을 구상한거야. 이건 그냥 내 예시지 내 요구사항은 아니야. 궁금한 건 이러한 방식이 실무적으로 봤을 때, 책임(관심사) 분리, FSD 아키텍처 패턴과 같은 관점에서 봤을 때 적절한 방식인 지가 궁금한 가고, 내 이러한 문제를 해결할 수 있는 방식이 이러한 방식 외에 다른 방법이 있는 지가 궁금한거야.
[Request interrupted by user]
planner는 그대로 작업 진행시켜. 문서화 잊지 말고.

---

## [메인 에이전트 응답]

승인 받았습니다. generator로 S1을 시작시키고, 동시에 사용자의 아키텍처 질문에 답변드리겠습니다.

(generator/planner 실행 — 본 논의와 직접 관련 없는 도구 호출은 생략. 아래는 아키텍처 질문에 대한 텍스트 답변 그대로.)

## 아키텍처 질문에 대한 답변

말씀하신 "searchState/payload 구성을 별도 hook으로 추출" 발상에 대한 제 견해입니다.

### 1. 적절성 평가

**부분적으로 적절합니다.** 다만 **"무엇을 hook으로 뺄지"** 기준이 핵심입니다.

- `reason 모달` 케이스가 hook이 되는 이유는 **사용자 인터랙션 + 전역 모달 상태 + 비동기 결과 반환**이라는 React 런타임 동작이 있기 때문입니다. 이건 hook의 본질적 책임 영역입니다.
- 반면 "단순한 searchState/payload 구성"은 **순수 데이터 변환**입니다. 여기에 hook을 붙이면 React 의존성이 없는 로직에 React 결합을 만드는 셈이 되어 테스트·재사용성이 오히려 떨어집니다.

### 2. 분기 기준 (실무 권고)

| 구성 로직의 성격 | 권장 추상화 |
|---|---|
| 입력 → 출력 순수 변환 (validation, 필드 매핑, 기본값 주입) | **순수 함수** (`buildXxxPayload(input): Payload`) — `utils/` 또는 도메인 `model.ts` |
| form 상태 관리 + 파생값 + 제출 제어 | **도메인 hook** (`useXxxForm`) — 도메인 폴더 내 `hooks/` |
| 사용자 인터랙션이 끼어드는 비동기 합성 (reason 모달, 파일 업로드 후 URL 합성 등) | **글로벌 hook + 글로벌 컴포넌트** (지금 reason-prompt 케이스) |
| 생성/수정이 한 UI에 혼재 | **분기는 hook이 아니라 "타입+빌더 함수"로**: `buildCreatePayload`, `buildUpdatePayload` 두 개의 순수 함수 + 호출부에서 mode에 따라 선택 |

핵심: **"규모가 크다(5개 이상 항목)"가 hook 추출의 기준이 되어선 안 됩니다.** 항목 수가 아니라 **상태성(stateful) 여부**가 기준입니다. 큰 payload여도 stateless면 함수가 옳고, 작은 payload여도 인터랙션·비동기가 끼면 hook이 옳습니다.

### 3. FSD 관점

FSD(Feature-Sliced Design)에서는 이 문제를 자연스럽게 분리합니다.

- `entities/<entity>/model/` — 타입과 순수 빌더 (`buildPayload`)
- `features/<feature>/model/` — feature별 form hook, mutation orchestration
- `shared/ui/`, `shared/lib/` — `ReasonPrompt` 같은 도메인 무관 자산
- `shared/hooks/` — `useReasonPrompt` 같은 횡단 hook

말씀하신 "생성/수정 혼재"는 FSD 관점에서 **두 개의 feature slice** (`features/post-create`, `features/post-update`)로 분리하고 **UI는 `entities/post/ui` 또는 `shared/ui`에서 공유**하는 패턴이 정석입니다. UI 재사용과 로직 분리를 동시에 달성합니다.

### 4. "이 외 다른 방법"

1. **Form 라이브러리 도입** — `react-hook-form` + `zod` 조합. searchState/payload validation·변환이 선언적으로 풀리고, hook을 직접 만들지 않아도 됩니다. 5개 이상 필드에서 ROI가 큽니다.
2. **Discriminated union + 빌더 함수** — `type Payload = CreatePayload | UpdatePayload`로 타입 안전하게 분기, 빌더는 순수 함수.
3. **URL 동기화 hook (`useSearchParamsState`)** — searchState의 경우 URL과 동기화가 필요하면 이게 진짜 hook이 필요한 지점입니다. 단순 객체 구성이 아니라 "브라우저 URL ↔ React state" 동기화가 본질이기 때문입니다.
4. **Mutation orchestration hook** — `react-query`/`TanStack Query`의 `useMutation`을 도메인별로 한 번 더 감싼 hook. payload 구성 + API 호출 + 캐시 무효화 + 토스트를 한 단위로 묶을 수 있습니다.

### 5. 결론 권고

- **"항목 수"가 아닌 "상태성"으로 추출 기준**을 잡으세요.
- 우선 **순수 빌더 함수**로 빼고, form 상태가 복잡해지는 시점에서만 hook으로 승격하세요.
- 생성/수정 혼재는 hook이 아니라 **빌더 함수 분리 + 호출부 mode 분기**가 더 깔끔합니다.
- 장기적으로는 **react-hook-form + zod 도입**이 이 모든 케이스의 단일 해법이 될 수 있습니다 (현재 프로젝트 도입 여부는 미확인).
- reason-prompt처럼 **인터랙션이 끼는 케이스만** 글로벌 hook + 컴포넌트 패턴을 유지하세요.

추가로 짚고 싶은 부분 있으신가요? (예: 현재 프로젝트의 form 상태 관리 현황 점검, 특정 도메인 케이스를 evaluator에게 진단 의뢰 등)
