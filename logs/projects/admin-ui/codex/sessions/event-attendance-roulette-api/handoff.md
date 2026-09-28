# 출석·룰렛 이벤트 API·화면 연결 인계

## 현재 결과 (2026-09-18)

출석·룰렛 API 16개와 UI의 목록·등록·상세/설정/보상 화면 연결을 완료했다. UI commit `dad057f`의 View·props를 재사용하여 Logic controller·검증·요청 매핑·페이지 진입·라우트를 추가했다. 전체 테스트 271개, lint, 타입 검사·build, diff 공백 검증 통과. 실서버·브라우저 기능 검증은 미실행.

후속 사용자 요청 반영: sortOrder의 전체 배열 연번 동작을 확인하고 유지했다. 출석·룰렛 화면 isActive는 null 대신 false를 기본값으로 사용한다. 토글을 표시하고 기본값 false도 다른 필드 수정 없이 저장할 수 있으며 목록·상세 요약도 false로 표시한다. 관련 테스트 51개, lint·build·diff 검사를 통과했다. 이 후속 수정은 아래 5개 파일의 미커밋 변경이다.

## 역할과 작업 위치

- host / session / role: Codex / event-attendance-roulette-api / Logic.
- requested_roles: Logic, confirmed_roles: Logic, completed_roles: Logic, next_role: 없음(추가 검토·통합 요청에 따라 지정).
- 사용자 승인: UI 핸드오프 기준 연결을 지시했고, 미저장 초안 유지·null 저장 차단·widgets 공용 로직·기존 날짜/이미지 모달 재사용을 승인했다. 아이템 검색은 최대 5건으로 확정했다.
- project: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`
- 작업 공간: `event-api-shared`, UI와 Logic이 순차 사용한 기존 공간.
- branch: `feature/event-attendance-roulette-api`, 직접 부모: `sy-main`.
- worktree·실행 디렉터리: `/private/tmp/asan-metaverse-admin-ui-event-api`.
- 현재 HEAD: `1b8e7336b382def67d97edf74b5a25192732fea0`.
- 분기 기준: `f3627abcd440709ccec1b98a6b37238fcf6936e2`.
- API commit: `b418379`; UI commit: `dad057f`; Logic 연결 commit: `1b8e733` (`feat(events): 출석·룰렛 관리 화면에 API 연결`).
- 사용자 승인 후 소스·테스트 39개 파일을 커밋했다. 1836줄 추가·9줄 삭제. 커밋 후 staged·unstaged·untracked 없음. 다음 작업 시작 시 실제 상태를 다시 확인한다.
- 이후 현재 unstaged 변경: src/widgets/event-admin/lib/event-form.ts, src/widgets/event-admin/hook/use-event-basic-fields.ts, src/widgets/event-admin/hook/use-event-info.ts, src/widgets/event-admin/hook/use-event-list-controller.ts, tests/events-controller.test.mjs. staged·untracked 없음. isActive 후속 수정의 Git 변경은 요청받거나 실행하지 않았다.
- 보호 실행 작업 `60f18b6a1cb1d92aa1e09621266adf55`로 stage·commit 완료. merge·push는 실행하지 않았으며 해당 Git 작업의 별도 승인이 필요하다.
- 다음 작업도 위 기존 branch/worktree에서 변경을 보존하며 순차 수행한다. 신규 공간 생성 예정은 없다.
- `.claude/logs/sessions/event-attendance-roulette-ui/handoff.md`는 UI 인계의 읽기 전용 근거다. 현재 문서와 plan/final-summary는 자기 세션 산출물이며 ignored 경로이므로 다른 작업 공간에 자동 전달되지 않는다.

## 화면 사용

| 경로 | 동작 |
| --- | --- |
| /events | /events/attendance로 이동 |
| /events/attendance 또는 /events/roulette | 목록, URL page, size 20, 등록·상세 이동 |
| /events/{종류}/new | 기본 정보+보상 등록. 성공 후 목록 이동 |
| /events/{종류}/{eventId}?tab=info | 코드·기간·활성 여부 전체 PATCH |
| /events/{종류}/{eventId}?tab=configs | 이미지 즉시 교체, 텍스트 일괄 저장 |
| /events/{종류}/{eventId}?tab=rewards | 보상 편집·가져오기·전체 PUT |

`{종류}`는 attendance 또는 roulette. 다른 셸에서 이벤트 셸로 진입하는 새 링크는 작업 범위에 포함하지 않았다.

- 상세 세 탭은 `use{Attendance|Roulette}EventDetailQuery(eventId)` 하나를 사용한다. 탭이 없거나 잘못되면 info다.
- 보상 가져오기는 원본 eventId로 해당 종류의 items query options를 `queryClient.fetchQuery`에 전달한다. 결과를 편집 목록 전체로 교체하며 저장 전까지 서버에 반영하지 않는다.
- 목록 id가 null인 행은 상세 이동하지 않는다. null 목록/data/meta는 빈 목록과 구분하여 재조회 오류로 표시한다.
- 등록 시작일을 선택하면 ID는 900/901+YYYYMM, code는 YYYY_MM_ATTENDANCE/ROULETTE. 사용자가 직접 수정한 필드는 이후 시작일 변경으로 덮어쓰지 않는다.
- 날짜는 KST. 시작 00:00:00+09:00, 종료 23:59:59+09:00. 저장된 서버 요약과 편집 초안을 구분한다.
- objectId는 직접 입력하거나 이름으로 검색한다. 검색은 page 1, size 5, 화면도 최대 5건이다. 추가 결과는 검색어를 좁혀 조회한다.
- 출석 DAILY는 시작일 기준 달력, ACC는 누적 일수 영역이다. 일차 목록은 보상이 있는 일차만 표시하며 기간 밖에서 가져온 보상도 포함한다. 빈 일차 추가는 달력에서 한다.
- 기간 초과 DAILY는 경고만 하고 저장을 허용한다. 같은 일차 보상의 순서를 변경할 수 있으며 PUT/POST의 sortOrder는 전체 편집 배열 순서로 1부터 재부여한다. 날짜·DAILY/ACC별로 다시 시작하지 않는다. 예: 1일차 보상 두 개는 1·2, 다음 2일차 보상은 3이다. 서버가 일차별 연번을 요구하는지는 확인하지 않았으며 이번 요청에서는 현 구현만 확인했다.
- 룰렛 chance는 단위를 변환하지 않는다. objectImageUrl은 화면에 표시하지 않고 기존·가져온 값을 유지한다. null·신규는 빈 문자열이다.

## API 계약과 재사용

- 공개 진입점: `~/entities/event`. factory: `createAttendanceEventApi(client)`, `createRouletteEventApi(client)`; 인스턴스: `eventAttendanceApi`, `eventRouletteApi`.
- ApiClient·Axios 인증·ApiResponseDto·공용 오류 처리를 그대로 사용한다. endpoint에 /v1을 붙이지 않는다.
- 공용 목록 DTO: shared의 `PageSummaryResponseDto<T>` = items/totalElements/totalPages. 기존 total/page/size 구조의 PageResponseDto는 변경하지 않았다.
- 요청은 PATCH 포함 명세 필드와 값이 모두 필수이며 null 불가. 응답 객체 필드는 존재 필수, 값은 nullable.
- 화면 모델의 isActive는 응답 값이 null이면 false로 변환한다. API schema와 query cache의 원본 nullable 값은 유지하며 PATCH에는 boolean을 전송한다.
- 보상 type은 DAILY/ACC, config type은 IMAGE/TEXT. configKey/configValue는 임의 문자열을 허용한다.
- 출석 상세의 items와 GET /items는 같은 `attendanceEventItemResponseSchema` 및 DTO를 사용한다.
- 출석 config PATCH는 key/value, 룰렛은 key/value/type. 출석 요청에 type을 추가하지 않는다.
- URL eventId는 int64 문자열 지원. body id/objectId는 정밀도를 잃지 않는 안전한 정수로 입력 검증 후 number로 전달한다.
- API의 성공 반환은 string 또는 null이다. 성공을 반환값의 truthy 여부로 판정하지 않는다.

| 작업 | API 메서드 | hook 이름 (종류 = Attendance 또는 Roulette) |
| --- | --- | --- |
| 목록 | getList({params,signal?}) | use{종류}EventListQuery |
| 상세 | getDetail({eventId,signal?}) | use{종류}EventDetailQuery |
| 보상 조회 | getItems({eventId,signal?}) | use{종류}EventItemsQuery |
| 등록 | postEvent({payload,signal?}) | useCreate{종류}EventMutation |
| 기본 정보 | patchEvent({eventId,payload,signal?}) | useUpdate{종류}EventMutation |
| 보상 저장 | putItems({eventId,payload,signal?}) | useUpdate{종류}EventItemsMutation |
| 설정 저장 | patchConfigs({eventId,payload,signal?}) | useUpdate{종류}EventConfigsMutation |
| 이미지 | uploadConfigImage({eventId,payload:{file},signal?}) | useUpload{종류}EventConfigImageMutation |

직접 API를 호출할 때는 `unwrapApiResult`와 종류별 parser를 거친다. 일반 화면에서는 위 hook/options를 사용한다.

## 설정·초안·요청 생명주기

1. 응답에 존재하는 config 키만 표시·저장한다. 고정 표 순서 뒤에 미등록 응답 키를 응답 순서로 표시한다.
2. type은 응답 우선, null이면 고정 표 kind, 표에도 없으면 TEXT다. null configValue는 미설정으로 표시하고 요청에는 빈 문자열을 보낸다.
3. 이미지 선택 시 JPG/JPEG/PNG MIME을 검증하고 업로드한다. URL을 얻은 다음 서버 저장값 전체에서 해당 키만 바꿔 PATCH한다.
4. IMAGE 저장에는 편집 중인 TEXT를 포함하지 않는다. 업로드/재조회 중에도 TEXT 초안은 유지한다.
5. TEXT 저장은 응답에 존재하는 키 전체를 보내며 텍스트 초안을 반영하고 나머지는 저장값을 유지한다.
6. 업로드 실패·null/빈 URL·화면 이탈 취소는 후속 PATCH를 실행하지 않는다. 기존 ImageModal을 이벤트 셸에 마운트하고 open-image pubsub으로 연다.
7. 미저장 기본 정보·보상은 서버 재조회로 덮어쓰지 않는다. 저장 성공한 탭만 초안을 초기화하고 되돌리기는 최신 서버 값을 사용한다.
8. 편집 가능한 null 값은 빈 입력과 검증 메시지로 표시한다. 보상 type/day null, 표시할 수 없는 DAILY day, configKey null 등은 해당 탭 저장을 막고 이유를 표시한다. isActive는 후속 사용자 요청에 따라 null도 false로 기본 처리한다. 활성 토글을 표시하고 서버 null의 기본값 변환도 저장 가능한 변경으로 취급한다. 다른 필수 입력이 유효하면 바로 false를 저장하거나 true로 변경할 수 있다.
9. 객체 기본 속성과 이름이 같은 임의 configKey도 실제 값만 읽는다.
10. 요청별 guard는 중복 저장·늦은 결과를 막는다. 페이지는 eventId별 key로 수명을 분리한다. 저장/업로드 signal은 Axios로 전달된다. 검색·가져오기 query는 캐시 요청을 사용하며 화면 종료 후 결과 반영을 막는다.

## 캐시 갱신

- 등록: 같은 종류 목록 + 등록 id 상세/items.
- 기본 정보: 같은 종류 목록 + 해당 상세.
- 보상 PUT: 해당 상세와 items 둘 다.
- config PATCH: 해당 상세.
- 이미지 업로드 자체: 캐시 갱신 없음.
- entity mutation은 관련 조회를 취소한 후 invalidate하고 활성 query를 재조회한다. 다른 종류·ID·도메인 캐시는 유지한다.

## 변경 파일과 연결 구조

- `src/entities/event/api/{event.dto,attendance/attendance.dto,roulette/roulette.dto}.ts`: enum 제한.
- `src/widgets/event-admin/lib/`: 날짜·ID·숫자 검증, config payload·업로드 순서, 요청 guard, 보상 입력/순서 공통 처리.
- `src/widgets/event-admin/hook/`: 기본 필드, 목록·상세 상태, 기본 정보 저장, 설정, 검색, 보상 가져오기, 요청 생명주기.
- `src/pages/event-attendance/{hook,lib}/`: 목록·등록·상세 및 출석 보상 controller, 달력·일차·요청 매핑.
- `src/pages/event-roulette/{hook,lib}/`: 목록·등록·상세 및 룰렛 보상 controller, 이미지 URL 보존·요청 매핑.
- 각 pages의 `ui/event-*-{list,form,detail}-page.tsx`와 index: controller를 기존 View에 전달한다.
- `src/app/router/routes.tsx`, `event-admin-shell.tsx`: 라우트 및 기존 ImageModal 마운트.
- `src/shared/lib/utils/date.util.ts`: 기존 기본 시간대를 보존하며 선택적 timeZone 인자를 추가했다. 이벤트는 Asia/Seoul로 호출한다.
- `tests/events-controller.test.mjs`: 신규 모델·SSR controller·요청 생명주기 검사. 기존 events 계약/통합 테스트는 확정 enum으로 업데이트했다.
- UI commit에 포함된 View·CSS·props 및 다른 세션 로그는 보존했다.

## 검증과 다음 작업

- 후속 isActive 수정: 관련 6개 파일(events-controller, events-contract, events-query-mutation, logic-api-contract, logic-api-types, common-response-contract)의 node --test 51 pass / 0 fail / 0 skipped. 포맷·lint·타입 검사/build·diff 검사 통과. 날짜·종류가 다른 보상 네 개의 전체 sortOrder, null 활성 기본값·토글 변경·저장 가능 여부를 검증했다.
- 아래 전체 271개 결과는 직전 Logic 연결 commit의 검증이다. 후속 수정에서는 관련 범위를 재검증했다.
- 중앙 formatting.py apply: 성공. 수정한 소스·테스트만 포맷했다.
- 전체 tests 디렉터리 39개 파일을 명시한 node --test: 271 pass, 0 fail, 0 skipped (최종 실행 약 17.2초).
- npm run lint: 통과.
- npm run build: 타입 검사·Vite build 통과. 기존 vite-tsconfig-paths 안내와 500kB chunk 경고가 있다.
- git diff --check: 통과.
- 임의 configKey와 잘못된 DAILY day 두 경우는 수정 전 테스트 실패를 재현하고 수정 후 전체 테스트에서 통과했다.
- 검증 범위: 실제 Axios/MSW API 계약 16개, DTO/nullable/enum, 캐시·취소, KST·ID·payload, 초안 유지, 이미지 업로드→설정 저장 및 실패·취소, 조회 실패, 5건 검색 조건.
- 실서버 요청, 실제 브라우저 기능 확인, 시각 QA는 미실행이다. SSR 테스트는 DOM 클릭·라우터 이동을 실제 브라우저에서 검증한 것이 아니다.
- 구현 차단 요인·미정 계약은 없다. 다음에는 실제 API 환경에서 화면 기능을 확인하고 필요 시 사용자가 지정한 Git 작업을 수행한다.
- 통합 시 현재 직접 부모 sy-main과 형제 branch 변경을 다시 검토한다. 이번 작업에서 merge·push는 하지 않았다.
- 필요한 정책: 현재 세션에 바인딩된 task-role-routing, git-branch-strategy, coding-convention, data-fetch-layer, type-definition, validation, implementation-quality, documentation. usePubSub은 기존 hook 계약을 재사용한다.
