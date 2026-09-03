---
name: reference-index
description: synthoria-admin-ui의 reference(조각별 atomic 문서) 카테고리 인덱스. 공용 컴포넌트·커스텀 훅 중 무엇을 골라야 할지 진입점이 필요하거나, 새 reference 항목을 추가할지 판단해야 할 때 사용.
---

# Reference (synthoria-admin-ui)

> Reference = "이 조각이 무엇을 하는가, 어떤 계약을 가지는가"를 다루는 단일 책임 문서.
> Recipe가 "조립 순서"라면 Reference는 "각 조각의 단독 사용 설명서"다.

## 언제 이 스킬을 사용하나요?

- 특정 컴포넌트/훅의 props·반환값·계약을 확인하고 싶을 때
- 비슷한 기능의 기존 조각이 있는지 탐색할 때
- 새 reference 항목(공용 컴포넌트/훅)을 추가할지 판단할 때

---

## 1) 카탈로그

| 그룹 | 위치 | 내용 |
| --- | --- | --- |
| 공용 컴포넌트 | [components/SKILL.md](components/SKILL.md) | `src/components/*` 공용 컴포넌트, 도메인 종속 컴포넌트(`components/domain/*`) |
| 커스텀 훅 | [custom-hooks/SKILL.md](custom-hooks/SKILL.md) | `useApi`, `useAuth`, `usePubSub`, `useFetchAdapter` |

각 그룹의 SKILL.md가 자체 인덱스를 가진다. 거기서 개별 조각으로 들어가면 된다.

---

## 2) Reference 작성/추가 기준

### 2-1. 신규 reference를 만드는 시점

다음 중 하나라도 해당하면 reference 추가 후보다.

- 새 공용 컴포넌트(`src/components/*`)를 추가했다
- 새 커스텀 훅을 `src/hooks/*` 또는 도메인 hooks 폴더에 추가했다
- 기존 조각의 계약/사용법이 reference 문서로 남아있지 않다

### 2-2. 신규 reference를 만들지 않는 시점

- 페이지 단일 사용처에만 존재하는 helper/내부 컴포넌트
- 공용으로 승격되지 않은 inline 유틸 (코드 주석으로 충분)
- 한 도메인 안에서만 쓰이는 1회성 hook → 도메인 코드 README 또는 recipe 안에 흡수

### 2-3. 작성 표준

- 짧은 형식(< 100줄): 책임 / 사용 핵심 / 주의 / 예시 4개 섹션
- 긴 형식(≥ 100줄): 시그니처 / 입력·출력 / 패턴 / 함정 / 템플릿 섹션 (참고: `reference/custom-hooks/useFetchAdapter/SKILL.md`)
- frontmatter `description`은 **언제 부르는가** 중심으로 작성
- 다른 reference나 recipe로 흐름이 이어지면 **링크로만 위임** (내용 복제 금지)

---

## 3) 도메인 종속 reference

- 위치: `reference/components/domain/<comp-name>/SKILL.md` (이미 존재)
- 도메인 hook이 생기면: `reference/custom-hooks/domain/<hook-name>/SKILL.md`로 동일하게 분리
- 진정한 공용성이 확인되기 전까지는 **공용 폴더로 승격하지 않는다**

---

## 4) Reference vs Recipe vs Policy 구분 표

| 질문 | 위치 |
| --- | --- |
| "이 조각이 뭘 하나?" | reference |
| "이 플로우를 어떻게 조립하나?" | recipe |
| "무엇을 지켜야 하나?" | policy |

조립 흐름이 끼어들 여지가 없는 단일 조각이라면 reference. 여러 조각을 엮어야 한다면 recipe.
