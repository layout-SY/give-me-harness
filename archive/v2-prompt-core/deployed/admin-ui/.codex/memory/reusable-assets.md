# Reusable Assets

> 선택 기준은 [reference/components/COMMON_COMPONENTS.md](../../.agents/skills/reference/components/COMMON_COMPONENTS.md) 참조.
> 개별 계약/props/주의사항은 아래 각 SKILL.md 링크에서 확인한다.
> 실제 구현 탐색 루트는 공용 프리미티브 `src/shared/ui/`, 레이아웃·합성 `src/widgets/`, 도메인 기능 `src/features/`와 대상 페이지다. `reference/components/`는 구현 경로가 아니라 계약 문서 경로다.

## 입력/폼

| 컴포넌트 | 설명 | SKILL |
| --- | --- | --- |
| `text-input` | 일반 텍스트 입력 | [SKILL.md](../../.agents/skills/reference/components/text-input/SKILL.md) |
| `text-area` | 멀티라인 입력 | [SKILL.md](../../.agents/skills/reference/components/text-area/SKILL.md) |
| `dropdown` | 드롭다운 선택 | [SKILL.md](../../.agents/skills/reference/components/dropdown/SKILL.md) |
| `toggle-switch` | 온/오프 토글 | [SKILL.md](../../.agents/skills/reference/components/toggle-switch/SKILL.md) |
| `text-editor` | 리치 텍스트 편집 | [SKILL.md](../../.agents/skills/reference/components/text-editor/SKILL.md) |
| `button` | 일반 액션 버튼 | [SKILL.md](../../.agents/skills/reference/components/button/SKILL.md) |
| `icon-button` | 아이콘 버튼 | [SKILL.md](../../.agents/skills/reference/components/icon-button/SKILL.md) |
| `calendar-picker` | 날짜 범위 선택 | [SKILL.md](../../.agents/skills/reference/components/calendar-picker/SKILL.md) |

## 목록/검색

| 컴포넌트 | 설명 | SKILL |
| --- | --- | --- |
| `table` | 표준 테이블(컬럼 정의 기반) | [SKILL.md](../../.agents/skills/reference/components/table/SKILL.md) |
| `search-state-bar` | 검색 + 탭 + 생성 버튼 상단바 | [SKILL.md](../../.agents/skills/reference/components/search-state-bar/SKILL.md) |
| `pagination` | 페이지네이션 | [SKILL.md](../../.agents/skills/reference/components/pagination/SKILL.md) |
| `no-results` | 빈 상태 표시 | [SKILL.md](../../.agents/skills/reference/components/no-results/SKILL.md) |
| `loading` | 로딩 오버레이 | [SKILL.md](../../.agents/skills/reference/components/loading/SKILL.md) |

## 모달/오버레이

| 컴포넌트 | 설명 | SKILL |
| --- | --- | --- |
| `modal` | 중앙형 모달 | [SKILL.md](../../.agents/skills/reference/components/modal/SKILL.md) |
| `side-modal` | 우측 상세 편집 모달 | [SKILL.md](../../.agents/skills/reference/components/side-modal/SKILL.md) |
| `popup` | 단순/선택 팝업 | [SKILL.md](../../.agents/skills/reference/components/popup/SKILL.md) |
| `image-modal` | 이미지 미리보기 모달 | [SKILL.md](../../.agents/skills/reference/components/image-modal/SKILL.md) |
| `image-upload` | 이미지 파일 선택 팝업(콜백형) | [SKILL.md](../../.agents/skills/reference/components/image-upload/SKILL.md) |
| `fade-in` | 부드러운 등장 효과 | [SKILL.md](../../.agents/skills/reference/components/fade-in/SKILL.md) |

## 전역/레이아웃

| 컴포넌트 | 설명 | SKILL |
| --- | --- | --- |
| `header` | 상단 바/언어 전환/로그아웃 | [SKILL.md](../../.agents/skills/reference/components/header/SKILL.md) |
| `navigation` | 좌측 내비게이션 | [SKILL.md](../../.agents/skills/reference/components/navigation/SKILL.md) |
| `private-route` | 인증 가드 | [SKILL.md](../../.agents/skills/reference/components/private-route/SKILL.md) |
| `role-based-route` | 권한 가드 | [SKILL.md](../../.agents/skills/reference/components/role-based-route/SKILL.md) |

## 도메인 공용 오버레이

| 컴포넌트 | 설명 | SKILL |
| --- | --- | --- |
| `select-users` | 유저 선택 팝업 | [SKILL.md](../../.agents/skills/reference/components/select-users/SKILL.md) |
| `send-parcel` | 우편/보상 발송 팝업 | [SKILL.md](../../.agents/skills/reference/components/send-parcel/SKILL.md) |

## 커스텀 훅

| 훅 | 설명 | SKILL |
| --- | --- | --- |
| `useApi` | API 호출 공통 훅 | [SKILL.md](../../.agents/skills/reference/custom-hooks/use-api/SKILL.md) |
| `useAsyncTask` | 비동기 작업 실행 + local loading 훅 | [SKILL.md](../../.agents/skills/reference/custom-hooks/use-async-task/SKILL.md) |
| `useAuth` | 인증 상태 접근 | [SKILL.md](../../.agents/skills/reference/custom-hooks/use-auth/SKILL.md) |
| `useLanguage` | 다국어 처리 | [SKILL.md](../../.agents/skills/reference/custom-hooks/use-language/SKILL.md) |
| `usePubSub` | 이벤트 버스 구독/발행 | [SKILL.md](../../.agents/skills/reference/custom-hooks/use-pub-sub/SKILL.md) |
| `useFetchAdapter` | 테이블 데이터 패칭 어댑터 | [SKILL.md](../../.agents/skills/reference/custom-hooks/useFetchAdapter/SKILL.md) |

## API/서버 상태

| 자산 | 설명 | 가이드 |
| --- | --- | --- |
| `QueryClient` | CP 도메인 서버 캐시·retry·staleTime 기본값 | [policy-tanstack-query](../../.agents/skills/policy/tanstack-query/SKILL.md) |
| `withAbortSignal` | TanStack Query의 `AbortSignal`을 Axios config에 결합 | [recipe-api-authoring](../../.agents/skills/recipe/api-authoring/SKILL.md) |
| `unwrapApiResult` | `ApiResult` 실패를 typed exception으로 전환해 query error 경계에 전달 | [recipe-api-authoring](../../.agents/skills/recipe/api-authoring/SKILL.md) |
