---
name: reference-components
description: synthoria-admin-ui 컴포넌트(src/components 공용 + src/pages/**/components|modules|widgets 전용)를 신규 작성·수정·재사용 판단할 때 진입하는 reference 인덱스. 어떤 공용 컴포넌트를 골라야 할지, 공용/도메인/페이지 중 어디에 둘지 기준이 필요할 때 사용.
---

# Components (synthoria-admin-ui)

## 이 스킬의 목적

- 새 컴포넌트를 만들기 전에 **기존 공용 컴포넌트 재사용 가능성**을 먼저 판단한다.
- 공용으로 올릴지, 페이지 전용으로 둘지 기준은 두 개 이상 서로다른 도메인에서의 사용, props 데이터 및 타입의 제네릭화 가능성,
- 공용 컴포넌트의 유지보수는 리팩토링 에이전트만 전담한다.

---

## 빠른 시작

1. 먼저 `src/components/`에서 유사 컴포넌트를 찾는다.
2. 아래 결정 규칙으로 위치를 정한다.
3. 구현 전에 관련 가이드 파일을 읽는다.

### 결정 규칙 (필수)

- **공용 컴포넌트로 승격**: 2개 이상 도메인에서 재사용 + DTO/라우트 의존이 약함
- **페이지 전용 유지**: 특정 페이지의 API/도메인 이벤트/상태에 강하게 결합

---

## 이 스킬의 문서 구조

- 공용 컴포넌트 **선택 가이드**: [COMMON_COMPONENTS.md](COMMON_COMPONENTS.md)
- 도메인 전용 공용 컴포넌트 선택 가이드: [DOMAIN_COMPONENTS.md](DOMAIN_COMPONENTS.md)
- 페이지 일반 컴포넌트 가이드: [PAGE_COMPONENTS.md](PAGE_COMPONENTS.md)
- 공용 컴포넌트별 **개별 사용 가이드**: `components/<component>/SKILL.md`
- 도메인 전용 공용 컴포넌트별 가이드: `components/domain/<component>/SKILL.md`

작업 순서:

1. `COMMON_COMPONENTS.md`에서 요구사항에 맞는 컴포넌트를 고른다.
2. 선택한 컴포넌트의 개별 `SKILL.md`를 읽고 사용 규칙을 따른다.
3. 공용 컴포넌트 완성도가 부족한 부분은 페이지 레벨 스타일/래퍼로 보강한다.

---

## 작업 전 체크리스트

- `src/components/`에 기존 대체품이 없는가?
- 목록 UI라면 `Table`/`useFetchAdapter` 조합을 따르는가?
- 모달이라면 `modal` vs `side-modal` 선택이 맞는가?
- PubSub 이벤트가 필요하면 `src/hooks/use-pub-sub/events.ts` 타입도 함께 갱신했는가?
- 선택한 공용 컴포넌트의 개별 `SKILL.md`를 읽었는가?

---

## 금지/주의

- 사용자 노출 문자열은 한글로 직접 작성 (프로젝트는 i18n 미사용)
- 페이지 전용 비즈니스 로직을 무분별하게 `src/components/`로 이동 금지
- 기존 패턴(인덱스 기반 `Dropdown`, `MODAL_STATES`, `refresh-*` pubsub 흐름)을 무시한 독자 구조 도입 금지
- 공용 컴포넌트가 부족하다는 이유로 기존 계약을 깨는 대규모 수정 금지

---

## 수행 프롬프트

아래 순서대로 컴포넌트 작업을 진행한다.

1. 요구사항과 유사한 기존 컴포넌트를 `src/components`와 대상 페이지 폴더에서 탐색한다.
2. 재사용/확장/신규 중 하나를 선택하고, 선택 근거를 짧게 명시한다.
3. 공용/페이지 전용 위치를 결정한다.
4. 스타일, 상태(`useApi`/`usePubSub`)를 기존 패턴에 맞춰 구현한다.
5. 기존 호출부까지 연결하고 동작 검증(열기/닫기, 로딩, empty, 에러)을 수행한다.
