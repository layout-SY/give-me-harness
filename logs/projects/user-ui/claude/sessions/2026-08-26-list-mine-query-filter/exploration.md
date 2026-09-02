# 탐색

## 요청

사용자는 이전에 채택했던 「내 활동만 보기 = 별도 `/me/activity` API」 구성을 지우라고 했다. 제안 도메인에 반영된 것처럼 목록 필터는 별도 API가 아니라 query `true`/`false`로 요청해야 한다.

## 대상 관련 사실

- 제안 목록은 이미 `GET /citizen/proposals`에 `mine`을 붙였고, 기본 요청에서는 `mine`을 생략했다.
- 투표·토론·정책 목록은 `myActivityOnly`일 때 `useMyActivityQuery`가 `/me/activity?content=`를 쳤다.
- `useMyProposalActivityQuery`는 목록 필터용으로 생겼고, 내 활동 페이지 제안 탭이 재사용했다.
- 화면 URL은 `?myActivity=true`를 유지한다. 서버 query 이름은 `mine`이다.
- 설문 목록에는 「내 활동만 보기」 토글이 없다.
- 메인 「내 활동 보기」는 내 활동 페이지로 이동하는 별도 진입점이다.

## 불러온 스킬

- `.agents/skills/SKILL.md`
- `policy/harness`, `policy/coding-convention`, `policy/type-definition`, `policy/data-fetch-layer`, `policy/documentation`, `policy/portfolio`, `policy/hook-extraction`, `policy/abstraction-strategy`, `policy/codex-native-quality`, `policy/review-checklist`, `policy/publishing`
- `recipe/api-authoring`, `recipe/data-dto`, `recipe/data-fetch`
- `reference/SKILL.md`, `reference/custom-hooks`, `reference/components`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| Pagination | 재사용 | 기존 목록 페이지 계약 유지 |
| 새 필터 컴포넌트 | 제외 | `MyActivityToggle`이 이미 헤더에 있다 |
| useApi | 제외 | TanStack Query + `ApiClient` 경로가 있다 |

## 제약 조건 및 미확인 사항

- 투표·토론·정책 백엔드 `mine` 스펙 문서는 제안과 같다고 사용자가 지시했다. 허용 sort 같은 추가 필드는 이번 지시에 없다.
- `mine=false`의 의미는 전체 목록이다. `mine=true`의 반대 집합이 아니다.
- 내 활동 페이지의 전체/비제안 필터는 `/me/activity`를 유지한다.

## 결론

목록 필터의 단일 계약은 각 목록 endpoint의 `mine=true|false`다. `/me/activity`는 내 활동 페이지용으로만 남긴다.
