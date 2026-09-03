# 역할 범위 세션 (`--role`) 연구

> 상태: 연구 단계. 도입하지 않았다. 세 호스트의 역할 배분이 확정된 뒤 재검토한다.

## 1. 무엇을 하려는 것인가

현재 런처는 대상 프로젝트와 호스트만 지정한다.

```sh
python3 bin/sync.py start --target user-ui --host claude
```

여기에 역할을 더해, 세션이 시작될 때부터 자기 담당 범위를 알고 그 범위 밖은 건드리지 않게 하려는 구상이다.

```sh
python3 bin/sync.py start --target user-ui --host claude --role ui
python3 bin/sync.py start --target user-ui --host codex  --role generator
```

기대 효과는 세 가지다. 역할별로 필요한 스킬과 지침만 주입해 컨텍스트를 줄이고, 병렬 세션 간 파일 충돌을 미리 막고, 어떤 세션이 무엇을 바꿨는지 책임을 명확히 한다.

## 2. 경계가 무너지는 지점

같은 저장소의 두 파일이 문제를 정확히 보여준다. 둘 다 `src/**/ui/**` 아래에 있어 경로만 보면 동일하게 `ui` 역할 소유다.

### 경계가 성립하는 경우

`src/features/auth/ui/LoginPage.tsx` 는 상태와 동작을 전부 props 로 받는다.

```tsx
const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
  event.preventDefault();
  onSubmit();
};
```

`handleSubmit` 은 브라우저 기본 동작을 막고 주입받은 콜백을 호출할 뿐이다. 도메인 지식이 없다. 이 파일에서는 `ui` 역할이 모든 줄을 소유한다고 말해도 무리가 없다.

### 경계가 무너지는 경우

`src/features/meeting/ui/MeetingPage.tsx` 는 같은 `ui` 경로에 있으나 성격이 다르다.

```tsx
const [accessToken, setAccessToken] = useState("");
const { execute } = useApi();
const agoraMeeting = useAgoraMeeting();

const joinMeetingChannel = async (
  access: MeetingWithRtcCredential,
  refreshRtcCredential: RefreshRtcCredential,
) => { ... };
```

인증 토큰 상태, API 실행기, RTC 자격 증명 갱신이 한 컴포넌트 안에 있다. 경로는 `ui` 지만 내용의 상당 부분은 `logic` 역할의 관심사다. 이 파일을 `ui` 세션이 편집하면 로직을 건드리게 되고, `logic` 세션이 편집하면 UI 파일을 건드리게 된다. **어느 쪽으로 판정해도 틀린다.**

### 반대 방향의 사례

사용자가 지적한 두 사례가 이 구조에서 나온다.

- `ui` 역할이 CSS 를 제어하는 JavaScript 를 수정한다. 파일은 `.ts` 지만 관심사는 시각 표현이다.
- `logic` 역할이 React 컴포넌트 안의 `onClick` 핸들러가 호출하는 액션 함수를 수정한다. 파일은 `.tsx` 지만 관심사는 도메인 동작이다.

## 3. 왜 어려운가

**소유권의 단위가 파일이 아니기 때문이다.** 역할은 관심사 단위로 나뉘는데 훅이 관측할 수 있는 것은 파일 경로다. 관심사가 파일 안에서 섞이면 경로만으로는 판정할 수 없다.

여기서 중요한 사실이 따라온다. **경계가 모호한 파일은 대체로 관심사가 섞인 파일이다.** `LoginPage.tsx` 에서 경계가 명확한 이유는 UI 와 로직이 이미 분리되어 있기 때문이고, `MeetingPage.tsx` 에서 모호한 이유는 섞여 있기 때문이다.

즉 역할 경계 문제는 새로운 문제가 아니라 **기존 코드 구조 문제가 다른 형태로 드러난 것**이다. 이 프로젝트에는 이미 `policy/hook-extraction`, `policy/abstraction-strategy` 스킬이 있고 `CLAUDE.md` 는 UI 를 제어형 props 로 작성하도록 요구한다. 그 규칙이 지켜진 파일에서는 역할 경계도 저절로 명확해진다.

## 4. 접근법 비교

| 접근 | 방식 | 강점 | 약점 |
| --- | --- | --- | --- |
| 경로 기반 강제 | 역할별 허용 경로를 정의하고 벗어나면 차단 | 구현이 단순하고 현재 훅 구조를 그대로 쓴다 | 혼재 파일에서 반드시 오판한다. 정상 작업이 막히면 신뢰를 잃는다 |
| diff 위치 기반 | 변경된 hunk 가 JSX 블록 안인지 밖인지로 판정 | 파일보다 정밀하다 | 파서가 필요하고, JSX 안의 인라인 핸들러처럼 여전히 판정 불가한 형태가 남는다 |
| 선언 기반 | 세션 시작 시 작업 범위를 선언하고 그 범위만 허용 | 모호한 경우를 사람이 결정한다 | 매 세션 선언 비용이 든다. 선언이 부정확하면 무의미하다 |
| 관측 후 귀납 | 차단하지 않고 역할과 실제 변경을 기록한 뒤 데이터로 경계를 도출 | 정상 작업을 막지 않는다. 실제 경계를 근거로 정할 수 있다 | 즉각적인 강제력이 없다 |

## 5. 제안 — 관측부터 시작하고 단계적으로 승격한다

경계를 먼저 정의하고 강제하는 순서는 실패한다. 정의할 근거가 아직 없기 때문이다. 순서를 뒤집는다.

### Phase 0. 역할 주입만 (강제 없음)

`--role` 을 받아 해당 역할의 계약을 시스템 프롬프트에 주입한다. 훅은 아무것도 차단하지 않는다. 역할 정의는 이미 `common/roles/orchestration.md` 와 `hosts/<id>/agents/` 에 있으므로 새로 만들 것이 없다.

이 단계만으로도 컨텍스트 축소와 책임 명확화라는 효과의 절반을 얻는다.

### Phase 1. 관측

`Stop` 훅에서 그 세션이 실제로 바꾼 파일 목록과 선언된 역할을 대조하여 기록한다. 차단하지 않는다.

```json
{
  "session": "2026-08-26-meeting-join",
  "host": "claude",
  "role": "ui",
  "changed": ["src/features/meeting/ui/MeetingPage.tsx"],
  "outside_role": ["src/features/meeting/ui/MeetingPage.tsx"],
  "reason": ["logic-markers: useState, useApi, async"]
}
```

몇 주치가 쌓이면 다음을 알 수 있다. 어떤 파일에서 역할 충돌이 반복되는가. 어떤 위반이 실제로는 정상 작업인가. 어떤 경로 규칙이 오판을 만드는가.

### Phase 2. 경고

관측 데이터로 규칙을 조정한 뒤, 위반 시 메시지를 띄우되 통과시킨다. 사람이 판단해 진행하거나 중단한다. 오판률이 충분히 낮아졌는지 이 단계에서 확인한다.

### Phase 3. 선택적 차단

오판이 사실상 없는 항목만 차단으로 승격한다. 전부 차단할 필요는 없다. 예를 들어 `ui` 역할이 `src/**/api/**` 를 수정하는 것은 어떤 해석으로도 정상이 아니므로 차단 대상이지만, `ui` 역할이 `.tsx` 안의 이벤트 핸들러를 수정하는 것은 끝까지 경고로 남길 수 있다.

## 6. 경계 판정 규칙 초안

Phase 1 에서 사용할 1차 규칙이다. 확정이 아니라 관측 시작점이다.

| 역할 | 명백히 소유 | 명백히 비소유 | 판정 보류 |
| --- | --- | --- | --- |
| `ui` | `src/**/ui/**` 의 JSX 마크업과 CSS, `src/shared/ui/**` | `src/**/api/**`, DTO, parser, store | `.tsx` 안의 이벤트 핸들러 본문, 시각 제어용 `.ts` |
| `logic` | `src/**/hook*/**`, `lib`, `utils`, `api`, parser, validator | JSX 마크업, CSS 파일 | `.tsx` 안의 상태 선언과 비동기 함수 |
| `review` | 없음 (읽기 전용) | 모든 소스 | 세션 산출물 문서 |
| `plan` | 세션 산출물 문서 | 모든 소스 | 없음 |

`판정 보류` 열이 이 연구의 핵심이다. 이 칸을 없애려 하지 말고, 여기 쌓이는 사례를 관찰해야 한다.

### 로직 마커

혼재 판정에 쓸 수 있는 신호다. `ui` 경로의 파일에서 아래가 다수 발견되면 혼재 후보로 기록한다.

```
useState  useEffect  useReducer  use<도메인>()
async  await  fetch  execute(
```

`MeetingPage.tsx` 는 이 기준으로 25건, `LoginPage.tsx` 는 0건에 가깝다. 실제 코드에서 구분력이 확인된 지표다.

## 7. 구현 스케치

### CLI

```sh
python3 bin/sync.py start --target user-ui --host claude --role ui
```

`--role` 은 선택이며 생략하면 현재와 동일하게 동작한다.

### 번들

`bundles.build()` 가 역할을 받아 `system-prompt.md` 에 역할 계약 절을 덧붙이고, 역할별 훅 설정을 생성한다. 스킬은 역할에 필요한 것만 선별해 넣을 수 있으나, 초기에는 전량 유지해 변수를 줄인다.

### 훅

`harness_core.py` 에 역할 인식을 더한다. 환경변수로 역할을 전달받아 판정 함수만 추가하며, 기존 차단 로직은 건드리지 않는다.

```python
ASAN_SESSION_ROLE = os.environ.get("ASAN_SESSION_ROLE")

def role_observation(role: str, relative: str) -> dict[str, object] | None:
    """역할 범위 밖 변경을 기록용으로 판정한다. 차단하지 않는다."""
```

### 기록 위치

`logs/<target-id>/roles/<날짜>.jsonl` 에 append 한다. 이미 있는 로그 미러링 구조를 그대로 쓴다.

## 8. 부수 효과 — 리팩터링 신호

역할 충돌이 반복되는 파일은 관심사가 섞인 파일이다. 관측 데이터는 그대로 리팩터링 후보 목록이 된다.

```
충돌 상위 파일
  1. src/features/meeting/ui/MeetingPage.tsx     ui/logic 충돌 12회
  2. src/pages/citizen-participation/ui/...       ui/logic 충돌 7회
```

이 목록은 `policy/hook-extraction` 스킬이 다루는 바로 그 대상이다. 역할 시스템이 강제력을 갖기 전에도 이 부수 효과만으로 도입 가치가 있다.

## 8.1 테스트 가능성과 감시 가능성은 같은 속성이다

3절에서 역할 경계 문제가 코드 구조 문제와 동형이라고 했다. 이 관계는 더 구체적으로 확인된다. **테스트가 모킹해야 하는 경계가 곧 역할이 나뉘어야 하는 경계다.**

### 확인 과정

처음에는 "혼재된 파일은 테스트하기 어려우므로 테스트가 없을 것"이라고 예측했다. 데이터는 반대였다.

| 파일 | 로직 마커 | 테스트 |
| --- | --- | --- |
| `MeetingPage.tsx` | 22건 | 있음 |
| `LoginPage.tsx` | 0건에 가까움 | 없음 |

테스트 유무는 용이성이 아니라 필요성을 반영한다. 복잡하니까 테스트를 작성했고, 단순하니까 작성하지 않았다. 지표를 바꿔 테스트 코드의 내용을 보자 관계가 드러났다.

`src/features/meeting/ui/MeetingPage.test.tsx` 는 125줄 중 모킹과 셋업이 18줄이고 실제 단언은 2건이다. 2건을 검증하기 위해 6개 모듈을 모킹한다.

```js
vi.mock("~/shared/lib/hooks/use-api", ...)
vi.mock("../api/access/meetingAccess", ...)
vi.mock("../model/forms/meetingForms", ...)
vi.mock("../hook/agora/useAgoraMeeting", ...)
vi.mock("./preparation/MeetingPreparationPanel", ...)
vi.mock("./stage/MeetingStage", ...)
```

이 여섯 모듈은 `api`, `model`, `hook` 이다. 6절 표에서 `logic` 역할이 소유한다고 정의한 바로 그 경로다. 개발자가 테스트를 작성하며 그은 경계와 역할 시스템이 그으려는 경계가 일치한다.

### 왜 일치하는가

두 속성이 같은 질문으로 환원되기 때문이다.

| 테스트 가능성 | 감시 가능성 |
| --- | --- |
| 의존성 주입 → 모킹 불필요 | 제어형 props → 소유권 명확 |
| 모킹 대상 목록 | 역할 경계선 |
| 부수 효과 격리 → 테스트 격리 | 관심사 격리 → 세션 격리 |
| 테스트하기 어려운 코드는 설계 냄새 | 감시하기 어려운 코드도 같은 냄새 |

테스트 가능성은 입력을 통제하고 출력을 관측할 수 있는지를 묻고, 감시 가능성은 행위 범위를 통제하고 결과를 관측할 수 있는지를 묻는다. 둘 다 **경계가 명시적인가** 하나로 환원된다.

### 실용적 함의

**`vi.mock` 목록을 역할 경계의 후보로 쓴다.** 6절의 로직 마커는 휴리스틱이지만 모킹 목록은 개발자가 실제로 그은 경계다. Phase 1 관측 데이터를 몇 주 모으지 않아도 현재 테스트 코드에서 즉시 추출할 수 있다.

```sh
grep -rhoE 'vi\.mock\("([^"]+)"' src --include='*.test.tsx' | sort | uniq -c | sort -rn
```

**설계 기준이 하나로 합쳐진다.** "AI 가 감시하기 쉽게 작성하라"는 "테스트하기 쉽게 작성하라"와 같은 방향이므로 추가 비용이 없다. 새 제약을 도입하는 것이 아니라 기존 원칙의 보상이 하나 늘어난다.

### 한계

모킹 경계는 역할 경계의 **하한**이지 상한이 아니다.

- 테스트는 동작을 검증하고 감시는 권한을 본다. 잘 분리된 유틸 두 개가 테스트 용이성은 같아도 서로 다른 역할 소유일 수 있다.
- 파일이 잘 분리되어도 한 파일 안에 두 역할이 공존할 수 있다. `.tsx` 의 JSX 와 핸들러 본문이 그 예이며 모킹으로는 갈라지지 않는다.

모킹이 필요한 곳은 확실히 경계지만, 모킹이 필요 없다고 경계가 없는 것은 아니다.

## 9. 도입 판단 기준

다음이 충족되기 전에는 Phase 2 이상으로 올리지 않는다.

- 세 호스트의 역할 배분이 확정되었다. 특히 Claude 가 계획과 평가를 맡을 경우 `plan` 역할의 소유자가 정해져야 한다.
- Phase 1 관측이 최소 20 세션 이상 축적되었다.
- 관측된 위반 중 실제 오판 비율이 파악되었다.
- 역할별 허용 경로가 두 프로젝트 모두에서 검증되었다. admin-ui 는 스택이 달라 경로 관행이 다를 수 있다.

## 10. 미해결 질문

- 한 세션이 여러 역할을 수행해야 할 때 어떻게 처리하는가. 역할 전환을 허용할 것인가, 세션을 나눌 것인가.
- 역할이 다른 두 세션이 같은 파일을 동시에 편집하려 할 때 조정 주체는 누구인가. 현재는 사용자가 중계한다.
- 역할별 산출물 요구를 어떻게 정하는가. `plan` 역할이 `implementation-log.md` 를 쓰지 않는 것은 자연스럽지만, 훅은 현재 세션 디렉터리 단위로만 검사한다.
- 역할 계약을 `common/` 에 둘 것인가 `hosts/<id>/` 에 둘 것인가. 공통으로 두면 호스트 간 드리프트를 막지만, 호스트별 능력 차이를 반영하기 어렵다.
