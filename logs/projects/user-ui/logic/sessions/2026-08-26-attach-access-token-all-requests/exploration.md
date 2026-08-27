# 탐색

## 요청

사용자는 모든 API 요청에 액세스 토큰이 반영되어야 하므로 인증 헤더를 전부 추가하라고 했다.

## 대상 관련 사실

- 공유 `axios-instance` 인터셉터는 `authRequired === true`일 때만 `Authorization`을 붙였다.
- `customConfig`는 `{ authRequired: true }`이며, 시민참여에서는 쓰기 요청과 `mine=true` 목록에만 섞였다. 목록/상세/배너/공지 GET은 헤더가 없었다.
- 시민참여 런타임 클라이언트는 `createApiClient(axiosInstance)`를 쓴다.
- 로그인은 별도 `createAuthAxiosInstance`를 쓰며 인터셉터가 없었다.
- 회의 API는 `fetch`와 명시 `accessToken` 인자로 Bearer를 붙인다. 빈 문자열이면 헤더를 생략했다.
- 토큰 저장 키는 `ACCESS_TOKEN_STORAGE_KEY` (`access-token`)다.

## 불러온 스킬

- `.agents/skills/SKILL.md`
- `policy/harness`, `policy/coding-convention`, `policy/type-definition`, `policy/data-fetch-layer`, `policy/documentation`, `policy/portfolio`, `policy/abstraction-strategy`, `policy/codex-native-quality`, `policy/review-checklist`, `policy/hook-extraction`
- `recipe/api-authoring`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| 공용 UI | 제외 | HTTP 인증 헤더 작업이며 UI가 아니다 |

## 제약 조건 및 미확인 사항

- 토큰이 없을 때 401을 미리 막을지는 지시되지 않았다. 헤더만 붙이고 없으면 생략한다.
- 로그인 요청에 이전 토큰을 붙이는 서버 동작은 확정되지 않았다. 사용자는 모든 요청에 토큰 반영을 지시했다.

## 결론

요청마다 `customConfig`를 더 뿌리는 대신, 전송 계층에서 토큰이 있으면 항상 Bearer를 붙인다.
