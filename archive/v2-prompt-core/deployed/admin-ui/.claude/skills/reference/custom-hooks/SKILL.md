---
name: reference-custom-hooks
description: synthoria-admin-ui 커스텀 훅(useApi, useAuth, usePubSub, useFetchAdapter)을 선택·사용·수정할 때 진입하는 reference 인덱스. 어떤 훅이 어떤 상황의 책임자인지 판단이 필요할 때 사용.
---

# Custom Hooks (synthoria-admin-ui)

## 이 스킬의 목적

- 기능 구현 전에 **이미 존재하는 커스텀 훅으로 해결 가능한지**를 먼저 판단한다.
- 각 훅의 책임 범위/의존성/호출 관례를 일관되게 유지한다.
- 신규 훅 작성보다 기존 훅 조합을 우선한다. 신규 훅이 필요하다면 `src/hooks/` 혹은 페이지 전용 `hooks/` 하위에 두고, 재사용 여부를 근거로 위치를 결정한다.

---

## 프로젝트 내 커스텀 훅 목록

| 훅 | 위치 | 책임 |
| --- | --- | --- |
| `useApi` | `src/hooks/use-api.tsx` | API 호출 실행/취소/로딩/에러 Dialog 표시 |
| `useAuth` | `src/hooks/use-auth.ts` | 로그인/토큰 리프레시/로그아웃 + jotai 상태 동기화 |
| `usePubSub` | `src/hooks/use-pub-sub/index.ts` | 전역 이벤트 pub/sub (모달 열기/리프레시/알림) |
| `useFetchAdapter` | `src/components/table/hooks/useFetchAdapter.ts` | 공용 Table 전용 검색·페이지네이션 데이터 어댑터 |

---

## 빠른 선택 규칙

- **API 호출이 필요한가?** → `useApi`
- **토큰 세션/로그인 흐름이 필요한가?** → `useAuth`
- **사용자 노출 문자열이 필요한가?** → 한글로 직접 작성 (프로젝트는 i18n 미사용)
- **타 화면/컴포넌트와 이벤트 기반 연동이 필요한가?** → `usePubSub`
- **공용 `Table` 데이터 바인딩이 필요한가?** → `useFetchAdapter`

> 목록/검색 화면의 행 데이터를 직접 표시하는 경우 `useFetchAdapter`가 아닌 `useApi` + 로컬 state로 처리하는 패턴도 공존한다. 해당 페이지의 기존 스타일을 우선 따른다.

---

## 이 스킬의 문서 구조

- `useApi` 개별 가이드: [use-api/SKILL.md](use-api/SKILL.md)
- `useAuth` 개별 가이드: [use-auth/SKILL.md](use-auth/SKILL.md)
- `usePubSub` 개별 가이드: [use-pub-sub/SKILL.md](use-pub-sub/SKILL.md)
- `useFetchAdapter` 개별 가이드: [useFetchAdapter/SKILL.md](useFetchAdapter/SKILL.md)

---

## 작업 전 체크리스트

- 호출부에서 `api`를 직접 import 하지 않고 `useApi()`를 통해 접근했는가?
- 사용자 노출 문자열을 한글로 직접 작성했는가 (프로젝트는 i18n 미사용)?
- pubsub 이벤트를 추가했다면 `src/hooks/use-pub-sub/events.ts`의 `PubSubEvents` 타입도 갱신했는가?
- 공용 테이블 기반 화면이면 `useFetchAdapter` + `setRequestSearch(true)` 트리거 규칙을 지켰는가?
- 토큰/세션 조작은 `useAuth`의 진입점만 사용했는가 (직접 localStorage 조작 금지)?

---

## 금지/주의

- `useApi()` 없이 `api.*`를 직접 import 하여 호출하지 않는다 (에러 Dialog/취소 가드가 누락됨).
- `useAuth` 밖에서 access/refresh 토큰을 직접 저장·삭제하지 않는다.
- `usePubSub` 이벤트 이름을 `PubSubEvents`에 등록하지 않고 publish/subscribe 하지 않는다.
- `useFetchAdapter`는 공용 `Table` 패턴 전용이다. 수동 `<table>` 화면에 끼워 넣지 않는다.

---

## 수행 프롬프트

1. 요구사항이 어느 훅의 책임인지 위 표/선택 규칙으로 매핑한다.
2. 선택한 훅의 개별 `SKILL.md`를 읽고 계약/반환값/주의사항을 확인한다.
3. 기존 페이지에서 같은 훅이 어떻게 쓰였는지 한 곳 이상 참고 후 동일 스타일로 적용한다.
4. 타입/린트/빌드 통과를 확인한다.
