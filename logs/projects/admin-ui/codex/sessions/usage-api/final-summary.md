# 이용 내역 API 구현 결과

두 이용 내역 API를 독립된 usage 도메인의 ApiClient·DTO/parser·TanStack Query 흐름으로 구현했다. 관련 테스트 24개와 lint·build가 통과했다.

## 실제 변경

- `src/entities/usage/api/admin-usage.api.ts`: `createAdminUsageApi`가 `getPointList`, `getItemList`를 제공한다. 각각 `GET /admin/usage/point`, `GET /admin/usage/item`을 호출하며 공용 인증·AbortSignal·ApiResult 처리를 재사용한다.
- `api/admin-usage.dto.ts`: 선택 검색 필드와 요청 기본값 `page: 1`, `size: 10`, 반복 sort 직렬화에 필요한 계약을 정의한다. 미설정·null·빈 문자열 검색값은 키까지 제외한다. 검색어를 ID로 변환하지 않고 by·type·action은 string을 사용한다.
- 같은 DTO의 포인트·아이템 항목 필드는 모두 필수 키이며 값은 nullable이다. 공용 페이지 필드 `items`, `total`, `page`, `size`는 다른 도메인과 동일한 필수·non-null 계약을 사용하고 서버 값을 재계산하거나 대체하지 않는다.
- `api/admin-usage.parser.ts`: unknown 성공 data를 각 응답 schema로 파싱한다. 필드 누락과 잘못된 타입을 정상 빈 목록으로 숨기지 않는다.
- `model/admin-usage-query-keys.ts`, `model/admin-usage-query-options.ts`: `admin-usage` 아래에서 포인트·아이템 캐시를 구분하고 모든 검색·정렬·페이지 조건을 포함한다. 생략된 값과 명시된 기본값은 같은 키를 사용한다.
- `hook/use-point-usage-list-query.ts`, `hook/use-item-usage-list-query.ts`: 두 조회 hook을 제공한다. 인자를 생략하면 기본 페이지를 조회한다.
- `api/index.ts`, `index.ts`: 기존 구형 usageApi를 보존하고 관리자 이용 내역 client·factory·DTO·hook을 노출한다. 다른 도메인의 API·enum은 수정하지 않았다.
- `tests/usage-contract.test.mjs`, `tests/usage-query.test.mjs`: 신규 계약 7개와 실제 Axios·Query 검증 7개를 추가했다.

## 검증 결과

모든 명령은 `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`에서 실행했다.

| 검증 | 결과 |
| --- | --- |
| 중앙 bundle `formatting.py apply` | 소스·테스트 11개 파일에 실제 Prettier 적용 완료. 테스트 보완 뒤 해당 파일에 재적용했다. |
| `node --test --test-reporter=spec tests/usage-contract.test.mjs tests/usage-query.test.mjs tests/common-response-contract.test.mjs tests/logic-api-contract.test.mjs tests/logic-api-types.test.mjs` | 24개 통과, 실패·취소·건너뜀 0개. 신규 14개와 기존 10개. |
| `npm run lint` | 최종 테스트 수정 후 재실행, 종료 코드 0. |
| `npm run build` | TypeScript와 Vite build 성공, 종료 코드 0. 이후 변경은 테스트 코드뿐이다. |
| `git diff --check` | 종료 코드 0. |

검증 내용은 정확한 endpoint·인증, query 평탄화·필드 생략·반복 sort, 검색 문자열 보존, 요청 기본값, 필수 키와 nullable 값, 응답 순서·숫자·페이지 메타 보존, 캐시 분리, HTTP 실패·불완전 응답 처리 및 진행 중 요청 취소다.

취소 테스트의 최초 실패는 설치된 Query의 `revert` 취소가 기존 데이터를 반환하는 동작을 반영해 수정했다. 또한 MSW의 Node Request는 실제 Axios signal과 별개이므로 Axios interceptor에서 전달된 signal과 `ERR_CANCELED`를 관찰하도록 보완했다. 실제 요청 중단·이전 데이터 반환·늦은 응답 이후 캐시 보존 검증은 유지했다. 애플리케이션 취소 코드는 변경하지 않았다.

build에는 `vite-tsconfig-paths`의 내장 기능 전환 안내와 500 kB 초과 번들 경고가 있었다. 해당 설정은 이번 변경 범위 밖이며 빌드는 성공했다.

## 사용과 남은 범위

`~/entities/usage`에서 `usePointUsageListQuery`, `useItemUsageListQuery`, `adminUsageClient`를 가져올 수 있다. 두 hook은 선택적인 `GetUsageListQueryDto`를 받는다. 직접 API 호출은 `{ params, signal? }` 형식을 사용하며 hook은 파싱한 페이지 데이터를 반환한다.

- 승인된 API·DTO/parser·조회 hook 구현에는 남은 작업이 없다.
- 실서버 호출은 수행하지 않았으며 테스트용 MSW와 실제 Axios 경로로 검증했다. 앱용 mock이나 화면을 추가하지 않았다.
- 전체 enum은 사용자 지시에 따라 미확정 string 상태다. 목록이 확정되면 해당 schema를 좁힐 수 있다.
- 작업 위치는 `sy-main`, 최종 HEAD는 `604e4dc46900edbedd0dc0369784b7a76f1ab83d`다. 사용자 승인 후 소스·테스트 11개 파일을 `feat(usage): 이용 내역 API와 조회 훅 연결`로 커밋했다. 커밋 후 Git 작업 트리는 깨끗하다. branch 변경·merge·push는 실행하지 않았다.
- 자기 세션 기록은 `.codex/logs/sessions/usage-api/`에 두었다. 다른 세션 산출물과 중앙 정책은 수정하지 않았다.

## 후속 커밋

- 사용자 `커밋` 요청과 `명령 실행 승인`에 따라 보호 실행기 작업 `1ddcf52c37de07e22a58b695f900d2df`로 명시한 11개 파일의 stage·commit을 수행했다.
- 최초 실행은 중앙 잠금 파일 쓰기의 샌드박스 권한 오류로 Git 실행 전에 실패했다. 사용자 승인 후 동일 작업을 권한 요청과 함께 재실행하여 `stage: done`, 종료 코드 0을 확인했다.
- `git log -1`과 `git show --stat --oneline HEAD`에서 커밋 ID·메시지·11개 파일·626줄 추가를 확인했다. `git status --short --branch`에 변경 경로가 없다.
- 검증 완료 이후 소스 변경이 없어 테스트·lint·build는 재실행하지 않았다. 기존 24개 테스트와 lint·build 통과 결과가 해당 변경에 적용된다.
