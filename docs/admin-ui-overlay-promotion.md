# admin-ui 자산 카탈로그 중앙 승격 내역

## 문서 상태

- 기준일: 2026-09-04
- 대상: `admin-ui`의 컴포넌트·커스텀 훅 참고 자료 카탈로그
- 원본: V1 세대(`archive/v1-admin-ui-pre-core/.agents/skills/reference/`) 44개
- 결과: 중앙 `projects/overlay/admin-ui/skills/reference/` 23개
- 목적: 소비자에만 있던 프로젝트 전용 카탈로그를 중앙 정본으로 올리고, 실제 코드와 어긋난 서술을 제거한다.

## 1. 왜 그대로 옮기지 않았는가

V1 카탈로그는 중앙 정책 통합 이전의 수작업 세대이며 다음 문제가 있었다.

| 항목 | V1 상태 |
| --- | --- |
| 프로젝트명 | `synthoria-admin-ui` (현재 저장소명과 불일치) |
| 사본 | `.agents`와 `.claude` 두 벌이 존재하고 43쌍 중 36쌍이 상이 |
| 참조 경로 | 57개 중 **22개가 존재하지 않음** (38% 소실) |
| 기술 서술 | Jotai `src/atoms/**` 전제. 실제 의존성은 zustand 5 |
| UI 기반 | HeroUI 래퍼 구조를 전혀 반영하지 않음 |

두 사본 중 `.agents` 계열이 현재 구조에 가까웠으므로 이를 기준으로 삼았다. 예를 들어 `use-api`의 위치를 `.agents`는 `src/shared/lib/hooks/use-api.tsx`로, `.claude`는 존재하지 않는 `src/hooks/use-api.tsx`로 서술한다.

기존 공통 인덱스(`policy/common/skills/reference/SKILL.md`)가 이미 다음을 규정하고 있었고, V1 카탈로그는 정확히 이 원칙을 위반한 상태였다.

> 참고 자료 스킬은 실제로 존재하는 자산만 설명합니다. 원본 프로젝트의 컴포넌트가 이 대상 프로젝트에도 존재한다고 단정하지 않습니다.

## 2. 분류 기준

- **추가**: 자산이 실재하고 서술 구조가 현재 코드와 일치한다. 실제 소스를 읽어 계약을 보충해 재작성했다.
- **수정**: 자산은 실재하나 경로·API가 어긋난다. 실제 코드 기준으로 교정한 뒤 승격했다.
- **제외**: 자산 자체가 없거나, 설명된 구조가 현재와 근본적으로 달라 보충이 아닌 재설계가 필요하다.

모든 승격 문서는 `synthoria-admin-ui` 표기를 `{{PROJECT_NAME}}`으로 치환했다.

## 3. 승격한 23개

### 3.1 수정 후 승격 — 경로·API 교정 (20개)

`src/shared/ui` 아래 컴포넌트 18개와 훅 2개다. 공통 교정 사항은 다음과 같다.

- V1은 모든 컴포넌트를 자체 구현으로 서술했으나, 실제로는 대부분 **`@heroui/react` 래퍼**다. 이 사실과 prop 매핑을 명시했다.
- 존재하지 않는 CSS 파일 참조를 제거했다. 예: `button.css`는 없다.
- 실제 prop 시그니처와 기본값을 표로 기록했다.

| 문서 | 주요 교정 내용 |
| --- | --- |
| `components/button` | `button.css` 참조 제거. HeroUI `Button` 래퍼임과 `className` → variant 매핑(`cancel` → `secondary`), `fullWidth` 기본 `true` 명시 |
| `components/icon-button` | `button`과 별개의 variant 표(`primary-light` → `secondary`), 기본 variant가 `secondary`임을 명시 |
| `components/text-input` | `InputGroup` 기반, `enableClear` 기본 `true`, `enableShow` 동작, `data-invalid` 계약 추가 |
| `components/text-area` | `forwardRef` 계약과 `text-area-component` 고정 클래스 추가. `error` prop이 없음을 명시 |
| `components/dropdown` | **index 기반 통신**과 **동일 항목 재선택 시 해제(-1)** 동작을 명시 |
| `components/toggle-switch` | 완전 제어 컴포넌트임과 HeroUI `Switch` 하위 구조 고정 명시 |
| `components/loading` | `isOverlay` 사용 시 부모 `position` 필요 조건, CSS 2개 파일 동시 적용 명시 |
| `components/modal` | HeroUI `Modal` 래퍼, ESC·백드롭 닫힘이 기본 동작임을 명시 |
| `components/popup` | 네이티브 `<dialog>` 직접 제어임을 명시. `active`/`closing` 클래스와 `animationend` 기반 지연 닫힘, `onCancel` preventDefault 이유 추가 |
| `components/side-modal` | HeroUI `Drawer` 기반, `placement="right"` 고정 명시 |
| `components/image-modal` | **props 없음**. pub-sub `open-image` 이벤트로 열리는 전역 싱글턴임을 명시 |
| `components/image-upload` | **props 없음**. `open-image-upload-popup`/`close-image-upload-popup` 계약, JPG·PNG 제한, 단일 파일 처리 명시 |
| `components/pagination` | **1-based 페이지**와 10개 단위 묶음 계산 규칙, 경계 비활성 조건 명시 |
| `components/fade-in` | `delay` 이전 `null` 반환, 이중 `requestAnimationFrame` 이유 명시 |
| `components/no-results` | **`children`을 받지만 렌더링하지 않음**, CSS 파일명이 `no-result.css` 단수임을 명시 |
| `components/reason-prompt` | 명명 내보내기, `trim()` 기반 최소 길이 검증, 문구가 전부 prop임을 명시 |
| `components/search-state-bar` | 명명 내보내기, `<form>` submit 기반 검색, `title` prop 미사용, `proposal-` 접두 클래스 명시 |
| `components/table` | **페이지네이션과 빈 상태 내장**, `accessor`/`action`/`custom` 컬럼 분기, sticky·순번 계산 규칙 명시 |
| `custom-hooks/use-api` | 반환값이 `{ execute, isLoading }`뿐임(**`api` 집계 객체 없음**), `silent` 기본값이 `true`라 기본적으로 오류 UI가 뜨지 않음, seq 기반 race 가드와 `{ canceled: true }` 계약 명시 |
| `custom-hooks/useFetchAdapter` | `shared/lib/hooks`가 아닌 `shared/ui/table/hooks` 위치로 교정. `searchState` 변경 시 자동 재조회, `mapRow`/`fetchApi` 참조 안정성 요구, debounce 우선 규칙 명시 |

### 3.2 위치 이동 반영 후 승격 (2개)

| 문서 | 이동 |
| --- | --- |
| `custom-hooks/use-auth` | `src/features/auth/use-auth.ts`. 인증 기능 슬라이스로 이동. zustand store 연동, `CustomException` 재throw, refresh 응답 stale 검사를 명시 |
| `custom-hooks/use-pub-sub` | `src/shared/lib/pub-sub/index.ts`. 파일명 기반 탐색으로는 찾을 수 없어 V1 목록에서는 소실로 보였으나 실재한다. 싱글턴·타입 맵·구독 이전 이벤트 수신 불가를 명시 |

### 3.3 구조 변경 반영 후 승격 (1개)

| 문서 | 변경 |
| --- | --- |
| `components/calendar-picker` | `src/features/calendar-picker`로 이동하고 `shared/ui/date-range-picker` 어댑터를 쓰는 얇은 필드로 재설계됐다. 문자열 `DateRange` 계약과 부분값 입력·확정값 출력 비대칭을 명시했다. 현재 import하는 화면이 없다는 점도 기록했다 |

## 4. 제외한 21개

### 4.1 자산 소실 — 도메인 전면 교체 (9개)

`activity-label-component`, `activity-marker-component`, `activity-tile-component`, `dao-author-badge`, `dao-category-badge`, `dao-image-slots`, `dao-pass-dropdown`, `dao-status-badge`, `dashboard-pie-chart`

DAO·activity 도메인 자체가 존재하지 않는다. 현재 admin-ui의 도메인은 `cp-`(시민참여) 계열이다. 보충이 아니라 새 도메인 카탈로그 작성에 해당한다.

### 4.2 자산 소실 — 컴포넌트 없음 (7개)

`header`, `navigation`, `image-slot-item`, `private-route`, `role-based-route`, `send-parcel`, `text-editor`

`src` 전체에서 해당 디렉터리·파일을 찾을 수 없다.

### 4.3 자산 소실 — 훅 없음 (4개)

`use-async-task`, `use-language`, `use-reason-prompt`, `domain/use-dao-keyword-sort-query-state`

정의 심볼(`useAsyncTask` 등) 기준으로 재검색해도 존재하지 않는다. `use-reason-prompt`는 `src/shared/ui/reason-prompt` 컴포넌트만 남아 있고 훅은 없다.

### 4.4 동작 불가 (1개)

`select-users`

`src/features/select-users/ui/select-users.tsx`로 파일은 존재하나 **pub-sub 배선이 주석 처리되어 현재 열 수 없다.** `src` 어디에서도 import하지 않는다. 열림 경로를 되살리는 것은 보충이 아닌 기능 복구 결정이므로 사용자 판단이 필요하다.

## 5. 신규 작성한 12개

V1 카탈로그에 없던 `src/shared/ui` 자산이다. 실제 코드를 읽어 새로 작성했다.

| 문서 | 기록한 핵심 계약 |
| --- | --- |
| `components/dialog` | `useDialog().alert/confirm`. `confirm`은 store에 resolver를 저장해 `Promise<boolean>`을 반환한다. `Dialog` 컴포넌트가 앱에 마운트되어 있어야 하며, 제거하면 `useApi`의 오류 표시까지 죽는다. 애니메이션 이름이 CSS 계약이다 |
| `components/date-range-picker` | HeroUI·react-aria·`@internationalized/date` import를 이 파일에만 두는 anti-corruption layer. `Group` 래퍼를 `div`로 바꾸면 팝오버 앵커가 사라지고, `RangeCalendar.Cell`에 children을 주면 날짜 숫자가 사라진다 |
| `components/status` | 의미 색 → HeroUI 팔레트 2단계 매핑. 상태 코드 30여 개의 기본 색과 미등록 코드가 `neutral`로 떨어지는 동작 |
| `components/category` | 같은 2단계 매핑이지만 빈 값에서 `null`을 반환한다(`StatusBadge`는 `-`). `purple`과 `blue`가 같은 Chip color를 쓴다 |
| `components/author` | 결측 상태 네 갈래 분기. `getAuthorAvatarColorByAuthorId`로 사용자별 색이 고정된다 |
| `components/kpi-card` | `value`가 `ReactNode`이며 포맷은 소비처 책임. tone 이름이 `StatusBadge`와 겹치지만 다른 타입이다 |
| `components/definition-list` | `inline/rows/stack/grid` layout. `columns`·`labelWidth`는 `grid`·`rows`에서만 유효하다 |
| `components/section-card` | 헤더가 `title` 또는 `actions`가 있을 때만 렌더링된다. `description`만 넘기면 보이지 않는다 |
| `components/ratio-bar` | `percent` 합 정규화는 소비처 책임. 세그먼트는 `aria-hidden`이고 범례가 의미를 전달한다. 키가 `label`이라 중복 시 충돌한다 |
| `components/choice-chip-group` | 단일 선택이며 **해제가 없다**(`dropdown`과 다름). `data-selected`와 `aria-pressed` 이중 표기 |
| `components/timeline-list` | 빈 상태에서 `NoResults`가 아니라 `cp-caption` 문구를 렌더링한다. 날짜 포맷·정렬은 소비처 책임 |
| `components/status-transition-field` | `dropdown`을 감싸 value ↔ index 변환을 흡수한다. `dropdown`의 해제(-1)가 여기서는 선택 취소(`null`)로 이어진다 |

`src/shared/ui/form`은 제외했다. `index.ts`가 `export {}`뿐인 **미구현 placeholder**다. react-hook-form 설치 후 구현 예정이라는 주석만 있어 설명할 자산이 없다.

이로써 overlay 문서는 35개, `admin-ui` managed 파일은 253개가 됐다. 검증 대상 참조 경로는 96개이며 전부 실재한다.

## 6. 렌더링과 재발 방지

중앙 원본은 `projects/overlay/{project}/skills/**`이며 해당 프로젝트에만 렌더링된다.

- 투영 경로: `.agents/skills/**`와 `.agent-policy/common/skills/**`
- `admin-ui` managed 파일 183개 → **229개**. `user-ui`는 183개로 변동 없다.
- 공통 카탈로그 인덱스와 경로가 겹치면 렌더가 실패한다. 겹침 금지는 테스트로 고정했다.

`bin/agent-policy audit`에 overlay 불변식을 추가했다.

- overlay 문서에 `synthoria` 같은 낡은 프로젝트명이 남으면 실패한다.
- **overlay 문서가 백틱으로 인용한 `src/...` 경로가 소비자 저장소에 실재하지 않으면 실패한다.**

두 번째 검사가 V1 카탈로그를 낡게 만든 원인을 직접 막는다. 현재 66개 참조 경로 전부가 실재한다. V1은 57개 중 22개가 소실 상태였다.

회귀 테스트는 `tests/test_rendering.py`에 세 건을 추가했다. overlay가 자기 프로젝트에만 렌더링되는지, 치환이 끝나고 낡은 이름이 남지 않는지, 공통 인덱스를 가리지 않는지 확인한다.
