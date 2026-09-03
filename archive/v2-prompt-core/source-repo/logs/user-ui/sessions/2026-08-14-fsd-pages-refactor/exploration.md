# 탐색

## 요청

현재 feature 중심 구조를 저수준 자원을 pages와 app이 조합하는 FSD 방향으로 리팩터링한다.

## 대상 관련 사실

- `src/pages`는 현재 존재하지 않는다.
- `src/app/routing.ts`는 시민참여 route component 13개를 feature barrel에서 직접 import한다.
- route wrapper 5개와 URL/search-param state는 `features/citizen-participation/integration`에 있다.
- `features/citizen-participation/model/presentation.ts`는 15개 UI 표시 타입을 import한다.
- 시민참여 외부 production caller는 `src/app/routing.ts` 하나다.
- 초기 route 조사에서는 feature 간 직접 import가 발견되지 않았다.
- 후속 전체 레이어 검사에서 `src/shared/mocks/browser.ts`가 feature mock handler를 import하는 상향 의존을 발견했다.
- focused baseline은 7 test files, 19 tests 모두 통과했다.

## 불러온 스킬

- `refactor`
- `programming`
- `frontend`
- `project-ui`
- `policy-refactoring`
- `policy-coding-convention`
- `policy-documentation`
- `policy-harness`
- `policy-abstraction-strategy`
- `reference-index`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| `src/shared/ui/tabs` | 유지·재사용 | `ServiceTabs`의 domain wrapper가 이미 소비하며 이동 필요 없음 |
| `src/shared/ui/loading` | 유지·재사용 | list page pending 표시 계약 유지 |
| `src/shared/ui/button` 및 badge류 | 유지·재사용 | page UI 마크업을 이동하지 않으므로 import 변화 없음 |

## 제약 조건 및 미확인 사항

- TypeScript LSP는 사용자가 설치를 거부한 상태라 `npm run build`로 진단을 대체한다.
- auth와 meeting도 page-like component를 feature에서 노출하지만 독립적인 상태·테스트 경계이므로 후속 단계로 분리한다.
- `entities` 추출을 정당화할 cross-feature 재사용 근거는 현재 없다.
- MSW worker 시작은 앱 초기화 책임이므로 `app/mocks`가 소유하고, feature mock handler는 production barrel과 분리된 `testing.ts`로 노출하는 것이 가장 작은 경계 수정이다.

## 결론

가장 작은 안전한 1차 단위는 route composition, route state, page 표시 mapper를 `pages/citizen-participation`으로 이동하고 app이 pages 공개 API만 소비하게 만드는 것이다. MSW bootstrap은 `app/mocks`로 이동하되 feature-local handler/fixture와 Page UI primitive는 유지해 동작과 시각 계약을 보존한다.
