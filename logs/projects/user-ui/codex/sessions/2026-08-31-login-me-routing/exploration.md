# 탐색

## 요청

- 비로그인 시민참여 상세 진입 시 안내 모달을 먼저 표시하고 확인 후 로그인 화면으로 이동한다.
- current-user 조회 API를 `/me`로 변경한다.

## 대상 관련 사실

- 시민참여 경로는 `AuthRouteBoundary` 아래에서 보호된다.
- 기존 `AuthRouteBoundary`는 인증되지 않은 사용자를 모달 없이 즉시 `/login`으로 이동시킨다.
- `ApiErrorDialogBridge`는 `serverErrorQueue`의 `reauthenticate` 이벤트를 기존 `Dialog`로 표시하고 확인 후 인증 세션을 지운 다음 `/login`으로 이동한다.
- `meApi.getMe()`는 `RESOURCE = "/citizen"`과 `${RESOURCE}/me` 조합으로 `/citizen/me`를 요청한다.
- `useMeQuery()`는 투표·토론·정책 상세에서 호출된다.
- proposal·survey 상세에서는 current-user 조회가 관찰되지 않았다.
- 무인증 실제 API 요청은 `/citizen/me`와 `/me` 모두 401이었다.

## 불러온 스킬

- `policy-git-branch-strategy`
- `git-master`
- `skill-index`
- `policy-index`
- `reference-index`
- `reference-components`
- `reference-custom-hooks`
- `programming`
- `policy-coding-convention`
- `policy-type-definition`
- `policy-hook-extraction`
- `policy-validation`
- `policy-review-checklist`
- `policy-documentation`
- `policy-portfolio`
- `policy-harness`
- `policy-codex-native-quality`
- `policy-abstraction-strategy`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| `Dialog` | 재사용 | 기존 전역 오류 안내가 사용하는 접근 가능한 공용 대화상자 |
| 신규 모달 컴포넌트 | 제외 | 기존 `ApiErrorDialogBridge`와 `Dialog`로 요구 동작을 충족할 수 있음 |

## 제약 조건 및 미확인 사항

- production UI 파일은 Claude Code 소유 범위이므로 수정하지 않는다.
- 인증된 실제 `/me` 성공 응답은 사용할 수 있는 자격 증명이 없어 독립 확인하지 못했다.
- 사용자 보고에 따라 인증된 `/citizen/me`의 404를 수정 근거로 사용한다.

## 결론

- 보호 경계는 직접 이동하는 대신 기존 재인증 이벤트를 한 번 발행하고 콘텐츠를 차단한다.
- 모달 표시·세션 삭제·`returnTo` 이동은 기존 `ApiErrorDialogBridge`에 위임한다.
- current-user 조회와 대응 MSW handler만 `/me`로 변경하며 활동 API는 유지한다.
