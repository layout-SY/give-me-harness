# 영상·플레이리스트 API 구현 계획

승인된 Logic 범위에서 기존 ApiClient → DTO/parser → TanStack Query options → hook 구조를 재사용하여 11개 API를 구현한다.

- 작업 위치: `/private/tmp/asan-metaverse-admin-ui-video-api`
- branch: `feature/video-api`, 직접 부모: `sy-main`
- 분기 HEAD: `f3627abcd440709ccec1b98a6b37238fcf6936e2`
- 역할: requested_roles / confirmed_roles = Logic, 작업 책임 = owner
- 사용자 작업 지시: “sy-main 브랜치에서 작업 브랜치 분기하는 거 잊지 말고 작업 시작”. linked worktree 생성은 별도 Git 승인으로 완료했다. 소스 작성은 중앙 PreToolUse 훅에서 한 차례 차단되었으나 후속 사용자 `진행` 승인 후 시작했다.

## 확정 계약

- 영상 등록·수정 DTO는 `{ file: File }`이고 multipart의 `file`만 전송한다. 최신 사용자 지시로 기존 명세의 미정 `data` 객체를 대체하고 수정에도 파일을 필수로 둔다. 썸네일 파일도 필수다.
- 일반 요청·응답 필드는 키 존재 필수, 값은 nullable로 정의한다. 경로 ID와 파일은 필수이며 null을 허용하지 않는다.
- 공용 페이지 응답 DTO를 재사용한다. 명세의 응답 page/size 0을 보존한다. 목록 요청은 page/size/sort를 입력받고 임의 기본값이나 페이지 번호 변환을 추가하지 않는다.
- videoId는 명세대로 전달받는다. uuid와 숫자 ID의 관계 및 영상 상세 문자열의 의미는 추측하지 않는다.
- 플레이리스트 PATCH도 name/description/videoIds 키를 모두 요구하며 null을 허용한다.

## 탐색·재사용 근거

- `src/shared/api/api-client.ts`, `axios-instance.ts`, `axios.interface.ts`, `with-abort-signal.ts`, `common/api-result.ts`, `common/response.dto.ts`
- `src/entities/items/api/items.api.ts`, `items.dto.ts`, `items.parser.ts`, `model/item-query-options.ts`, `model/item-mutation-options.ts`, `hook/use-item-mutations.ts`
- `src/entities/news/api/news.api.ts`: sort 배열 직렬화
- `tests/items-contract.test.mjs`, `tests/item-category-query-mutation.test.mjs`: node:test, tsx, Vite SSR와 실제 Axios/MSW 경계 검증
- 기존 영상 관리 entity/page는 탐색 범위에서 발견하지 못했다. 메뉴는 주석 처리되어 있다. 승인된 신규 `src/entities/video/`에서 공용 자산을 사용한다.
- 적용 스킬: task-role-routing, git-branch-strategy, skill-index, data-fetch-layer, api-authoring, coding-convention, type-definition, documentation, implementation-quality. 기준은 inject로 지정된 중앙 bundle이다.

## 수행 순서·예상 변경

1. `src/entities/video/api/`에서 두 API factory와 DTO/parser를 작성하여 명세와 확정 계약을 전송 경계에서 보장한다.
2. 같은 entity의 `model/`, `hook/`, barrel에서 4개 query와 7개 mutation을 제공하고 성공 시 관련 캐시를 갱신한다. 영상 변경은 영상 정보를 포함하는 플레이리스트 상세 캐시도 갱신한다.
3. `tests/video-contract.test.mjs`, `tests/video-query-mutation.test.mjs`에서 nullable/필수 키, multipart, 11개 경로, 인증·취소, 오류·캐시 갱신을 검증한다. 테스트 데이터는 확정 계약만 사용한다.
4. 실제 workdir에서 중앙 `formatting.py apply` 실행 후 관련 테스트, `npm run lint`, `npm run build`를 수행한다. package.json에 test script는 없다.
5. 변경 diff를 검토하고 `final-summary.md`에 검증 결과와 실제 서버에서 미확인인 범위를 기록한다.

## Git 상태

- 생성 완료 작업: `bb89217efa5e49e1b2332e28adca1535`
- 앞선 worktree 미지정 작업은 실행기 요구사항으로 실패했으며 ref 변화가 없음을 확인했다.
- 후속 커밋 요청과 Git 실행 승인으로 `57bbb3c`에 구현·테스트 19개 파일을 커밋했다.
- 후속 `merge 진행`과 `명령 실행 승인`에 따라 작업 `f434c46048bc499b84f18816a0957fff`로 직접 부모 `sy-main`에 병합했다. 결과는 `0e7c671b511f8e6cecebcce8946a13ee24d8c339`이며, 병합 결과에서 테스트 20개와 lint·build가 통과했다. source branch와 linked worktree는 보존했다.

## 완료 확인

2026-09-17 KST 기준 소스 17개·테스트 2개 파일을 작성했다. 자동 포맷, 전용 테스트 16개, 공용 응답 테스트 4개, lint·타입 검사·build가 통과했다. 썸네일 변경 시 대상 영상 상세 캐시도 갱신하도록 최종 보완했다. 상세 결과와 실제 서버 미확인 범위는 `final-summary.md`, 후속 연결 계약은 `handoff.md`에 기록했다.
