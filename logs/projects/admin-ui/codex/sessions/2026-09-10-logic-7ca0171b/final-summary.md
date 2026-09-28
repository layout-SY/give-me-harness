# Logic 타입·lint 정리 결과

확인된 기존 계약 범위에서 소스 11개와 테스트 2개를 변경하고 `a4c4ec9`로 커밋했다. Logic 타입 오류 7건, lint 오류 15건과 cleanup 경고 1건을 제거했다. 전체 오류 정리는 미완료이며, 계약이 확인되지 않는 Logic lint 39건과 UI 오류는 남겼다. 병합은 아직 실행하지 않았다.

## 역할·승인·작업 위치

- 역할과 책임: `logic`, `owner`.
- 사용자 구현 승인: `그럼 너가 먼저 시작해`. 작업 브랜치 생성은 별도 `명령 실행 승인`으로 완료했다.
- worktree: `/private/tmp/asan-metaverse-admin-ui-logic-type-lint-7ca0171b`
- branch / HEAD: `task/logic-type-lint` / `a4c4ec94e752bea91fac7ef0bb675af7bcfb88b6`. 커밋 후 worktree와 index는 clean이다.
- 직접 부모 및 최종 병합 대상: `task/news-management-ui`. 상위는 `sy-main`. 사용자의 최신 교정에 따라 sy-main 직접 병합은 대상에서 제외한다.
- 기본 checkout의 `task/news-management-ui`는 `25c3ade2bcb26b72189945fd25921fcbb4b0e4b8`이며 커밋 후 조회에서도 clean이었다. `sy-main`은 `5834f920fcceadbe79491791d5cf8a35ca7e2a98`이다. 중앙 관계 그래프에는 news UI와 이번 Logic 관계가 아직 등록되지 않았다. 완료 통합 시 사용자와 확인한 계보를 등록해야 한다.

## 실제 변경

| 경로 | 변경과 근거 |
| --- | --- |
| `src/shared/lib/utils/performance.util.ts` | debounce·throttle의 any 인자를 tuple 제네릭으로 표현. 기존 호출부는 제네릭 인자를 명시하지 않으며 호출 방식·타이머 동작을 유지 |
| `src/shared/lib/utils/token.util.ts` | 설치된 jwt-decode 선언의 JwtPayload를 사용. 토큰 판정 로직은 유지 |
| `src/shared/lib/hooks/use-api.tsx` | effect가 참조한 AbortController Set을 cleanup에서 사용. execute·취소·최신 요청 계약 유지 |
| `src/entities/event/api/attendance/attendance.dto.ts`, `roulette/roulette.dto.ts` | 일반 enum 5개를 news.enum.ts의 const 객체·동명 타입 패턴으로 변경. 문자열 값과 멤버 접근 유지 |
| `src/entities/dao/model/table-rows.ts` | 미사용 타입 import 2개 제거 |
| `src/entities/profile/api/profile.api.ts` | getProfile·getRbac의 기존 반환 DTO를 Axios의 두 번째 제네릭에 연결 |
| `src/entities/admin-settings/api/admin-settings.api.ts` | getPolicies·getAdminRoles의 기존 반환 타입 연결 |
| `src/entities/items/api/item-category.api.ts` | main/sub 조회의 기존 DTO 연결. parentItemCategoryId를 parentId로 변환할 때 any·delete를 제거하고 원본 입력 보존 |
| `src/entities/maintenance/api/maintenance.api.ts` | 기존 GetSynthoriaConfigListResponseDto 연결 |
| `src/entities/maps/api/map.api.ts` | 기존 GetMapActivityResponseDto 배열 연결 |
| `tests/performance-util.test.mjs` | debounce의 마지막 인자·지연 갱신, throttle의 즉시 호출·제한 구간 검증 |
| `tests/item-category-contract.test.mjs` | 원본 입력 보존, parentId 생략·0 처리, interceptor 이후 data와 조회 params 전달 검증 |

Axios interceptor가 이미 응답 본문을 반환하므로 응답 타입은 `{ data: 기존 DTO }`로 표현했다. 서버 필드를 새로 추정하거나 공용 전송 계층을 바꾸지 않았다. UI 소스·패키지·정책은 변경하지 않았다.

## 검증

| 명령 | 결과 |
| --- | --- |
| `npm ci --offline` | 성공 |
| `node --test tests/performance-util.test.mjs tests/item-category-contract.test.mjs` | 신규 5개 통과 |
| `node --test --test-concurrency=1` | 전체 157개 통과, 실패 0 |
| `npm run build` | 성공. 기존 tsconfig paths plugin 안내와 큰 bundle 경고 발생 |
| `./node_modules/.bin/tsc --noEmit -p tsconfig.app.json` | 실패: 14건 → 7건. 남은 오류 모두 UI 경로 |
| `npm run lint` | 실패: 68 errors / 5 warnings → 53 errors / 4 warnings |
| `git diff --check` | 성공 |

`npm run build`의 `tsc -b`는 루트 tsconfig.json을 사용한다. 별도 tsconfig.app.json의 noUnused·erasableSyntaxOnly 검사는 여전히 실패하므로 빌드 성공을 전체 타입 검사 통과로 해석하지 않는다.

기본 `node --test`는 157개 assertion 통과 후 기존 Vite 기반 cp-comment-proposal·cp-date 테스트의 프로세스 종료에서 SIGTRAP·SIGSEGV가 발생해 전체 exit 1이었다. 테스트나 설정은 바꾸지 않고 순차 실행하여 전체 통과를 확인했다. 정확한 네이티브 충돌 원인은 확정하지 않았다. `node --test tests/*.test.mjs`는 guard의 경로 미확인으로 실행되지 않았고, `node --test tests`는 Node 22에서 디렉터리 진입점을 찾지 못했다. 최종 전체 검증 명령은 위 순차 실행이다.

독립 Watcher 판정, 실서버 요청, 개발 화면 조작·시각 QA는 실행하지 않았다. 구현자 검토와 실행 검증을 독립 Watcher PASS로 기록하지 않는다.

## 미완료 Logic lint 39건

| 경로 | 건수 | 남긴 이유 |
| --- | ---: | --- |
| `src/entities/admin-settings/api/admin-settings.api.ts` | 3 | 관리자 목록·상세·감사 로그의 실제 응답 미확인. DTO 선언만으로 서버 계약이 검증된 것으로 간주하지 않음 |
| `src/entities/dashboard/api/dashboard.api.ts` | 10 | dashboard DTO 파일이 비어 있고 서버 응답·해당 API 테스트 근거 없음 |
| `src/entities/event/api/attendance/attendance.api.ts` | 3 | 목록·상세 DTO와 개발 mock은 있지만 실제 서버 응답 계약 미확인 |
| `src/entities/event/api/roulette/roulette.api.ts` | 3 | 목록·상세·아이템 응답의 서버 계약 미확인 |
| `src/entities/faq/api/faq.api.ts` | 2 | 목록 DTO는 항목 형태이며 전체 응답·상세 계약 미확인 |
| `src/entities/items/api/items.api.ts` | 3 | 목록·상세·이미지 업로드 응답 계약 미확인 |
| `src/entities/sales/api/sales.api.ts` | 3 | 집계 계산과 DTO는 있지만 실제 전체 응답 계약 미확인 |
| `src/entities/users/api/users.api.ts` | 3 | 사용자 목록·기기 로그·통계 응답 미확인. select-users 소비 코드만으로 서버 계약을 단정하지 않음 |
| event attendance·roulette DTO 및 items DTO | 4 | 빈 upload interface는 상속 alias가 아니라 필드가 없는 placeholder. 활성 호출부와 업로드 필드·FormData 계약 미확인 |
| `src/shared/lib/pub-sub/events.ts` | 5 | 해당 이벤트의 활성 publish·subscribe가 없고 선택 팝업 코드는 주석 상태. callback 인자·반환값을 추정하지 않음 |

필요한 후속 근거는 대상 endpoint의 최신 응답 명세 또는 실제 응답 예시, 업로드 요청 필드, 이벤트 발행·구독 signature다. 이 근거를 확보한 Logic 작업이 남은 계약을 정리한다. lint 규칙 완화·disable·unknown을 통한 오류 숨기기는 하지 않았다.

## UI 인계와 다음 조치

UI 타입 7건과 lint 14건·경고 3건은 기존 담당 범위다. 공용 useApi의 execute 계약과 debounce·throttle 호출 방식은 유지했다. `useFetchAdapter`의 render ref 오류와 select-users 내부 any는 이번 변경으로 해소되지 않는다. 생성된 mockServiceWorker의 경고 1건도 남아 있다.

사용자의 `명령 실행 승인` 후 보호 작업 `faa07eed468a2659b11241563a3b683d`로 이번 13개 파일만 stage+commit했다. 실행 결과는 `done`, 커밋은 `a4c4ec9`, 메시지는 `fix(logic): 기존 계약에 따라 타입 및 lint 오류 정리`이며 135줄 추가·44줄 삭제다. 커밋 후 목록·HEAD·clean 상태를 확인했다. 소스 변경이 없으므로 직전 157개 테스트·빌드 검증을 반복하지 않았다.

병합은 관계·형제 변경·검증을 다시 확인하고 `task/news-management-ui`를 대상으로 별도 승인받아 수행해야 한다. 전체 lint와 별도 타입 검사가 실패하므로 전체 오류 정리 또는 완료 통합 PASS를 주장하지 않는다.
