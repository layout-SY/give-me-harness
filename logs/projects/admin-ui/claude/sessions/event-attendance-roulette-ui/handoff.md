# 출석·룰렛 이벤트 화면 Logic 인계

## 역할·상태

- 보내는 host·session·role: Claude Code / event-attendance-roulette-ui / UI
- requested_roles: UI, Logic(인계) / confirmed_roles: UI / completed_roles: UI / next_role: Logic(제안)
- 판단 근거: 사용자가 "UI/Logic 분담 그대로" 승인(2026-09-17). UI는 View·props 계약·config·CSS·셸/메뉴, Logic은 controller·검증·payload·page 진입·routes.
- 선행 인계(읽기 전용): `.codex/logs/sessions/event-attendance-roulette-api/handoff.md` (API·hook 계약)
- 인계 기준 시점: 2026-09-17, lint·build·이벤트 테스트 24개 통과 직후

## 인계 대상 작업 위치

| 항목 | 값 |
| --- | --- |
| 작업 공간 이름 | event-api-shared (UI·Logic 순차 공유) |
| project | `/Users/okand/SynologyDrive/asan-metaverse-admin-ui` |
| branch | `feature/event-attendance-roulette-api` (기존) |
| worktree·실행 디렉터리 | `/private/tmp/asan-metaverse-admin-ui-event-api` |
| 확인 HEAD | `b4183792d5221a30ff678d4ebbb37b8202e6155e` (UI 변경은 미커밋) |
| 직접 부모 | `sy-main` |
| 공유 이유 | 같은 기능의 UI→Logic 순차 연결. 병렬 수정 없음. Logic 시작 전 미커밋 UI 변경 존재를 확인하고 덮어쓰지 않는다. |

## 미커밋 변경 (UI, unstaged·untracked)

- M `src/widgets/side-navigation/lib/build-navigation-items.ts` — `buildEventNavigationItems()` 추가
- M `src/widgets/side-navigation/model/_navigation2.ts` — 이벤트 메뉴 경로 `/manage/events/*` → `/events/*`
- ?? `src/widgets/side-navigation/model/_navigation7.ts` — 이벤트 셸 메뉴(출석 체크 `/events/attendance`, 룰렛 `/events/roulette`)
- ?? `src/app/router/event-admin-shell.tsx` — `EventAdminShell` (routes 미등록)
- ?? `src/shared/ui/tabs/` — HeroUI Tabs 어댑터(controlled, 문자열 key)
- ?? `src/widgets/event-admin/` — 공용 View·계약(`model/event-admin.types.ts`, `model/event-detail-tab.ts`)
- ?? `src/pages/event-attendance/`, `src/pages/event-roulette/` — View·controller 타입·config·CSS. **page 진입 컴포넌트와 hook은 없음**

위 UI 변경은 사용자 요청으로 commit `dad057f` (`feat(events): 출석·룰렛 이벤트 관리 화면 UI와 controller 계약 추가`, 40 files)에 포함됐다. 커밋 후 staged·unstaged·untracked 없음. Logic은 HEAD `dad057f` 기준으로 시작한다. `.claude` 세션 로그는 ignored 경로라 커밋에 포함되지 않았다. merge·push는 미실행.

## 사용자 확정 정책 (Logic 구현 기준)

1. 라우트: `/events` 셸 `EventAdminShell`. `/events` index → `/events/attendance`.
   - `/events/attendance` 목록, `/events/attendance/new` 등록, `/events/attendance/:eventId?tab=info|configs|rewards` 상세. 룰렛 동일.
2. 목록: cp-news 방식. page는 URL query, size 20(`ATTENDANCE_EVENT_PAGE_SIZE`/`ROULETTE_EVENT_PAGE_SIZE`), 필터 없음. 행 클릭 → 상세(`row.id === null`이면 이동하지 않음). 헤더 등록 버튼 → `/new`.
3. 상세 탭 3개의 데이터는 모두 `use{Kind}EventDetailQuery(eventId)` 하나. 탭은 `?tab=` 로 유지(없거나 잘못되면 `info`).
4. 신규 등록: 기본 정보 + 보상만(config 미포함 정책). POST 성공 시 목록으로 이동.
5. 등록 ID·code 자동 입력 + 수정 가능: 시작일 선택 시 id=`900`(룰렛 `901`)+`YYYYMM`, code=`YYYY_MM_ATTENDANCE`/`YYYY_MM_ROULETTE`. 사용자가 직접 수정한 필드는 시작일 변경으로 덮어쓰지 않는다(추가 확정 2).
6. 환경 설정 키는 고정. 표시 키·순서·kind는 `ATTENDANCE_CONFIG_FIELDS`/`ROULETTE_CONFIG_FIELDS`. 응답 `configs[].type`이 있으면 kind로 응답 우선.
   - IMAGE: 파일 선택 즉시 `upload{Kind}EventConfigImage` → url 확보 → **서버 저장값 기준** configs 전체(교체 키만 새 url)로 `PATCH /configs`. 입력 중인 TEXT 초안은 포함하지 않고 유지한다. url null이면 PATCH하지 않고 필드 errorMessage.
   - TEXT: 탭 저장 버튼으로 고정 키 전체를 한 번에 PATCH(수정 안 한 키도 저장값으로 채움).
   - 룰렛 PATCH는 항목마다 type 필수 → 응답 type, 없으면 고정 표 kind.
   - 응답에 없는 키는 표시·PATCH 모두 제외한다(추가 확정 3).
7. 출석 보상 type은 `DAILY`/`ACC`만(`ATTENDANCE_REWARD_TYPES`). DAILY는 캘린더(시작일=1일차, 날짜 = startAt(KST) + day-1), ACC는 별도 영역(day = 누적 출석 일수).
8. objectId: 직접 입력 기본. 행의 "검색"으로 `ItemSearchPopup`을 열어 아이템 **이름 keyword** 검색(`useItemListQuery({page:1,size,keyword,...null})` 권장) → 결과 선택 시 대상 행 objectId 채움. ID 검색 모드는 두지 않음.
9. 룰렛 `objectImageUrl`은 사장 필드. 화면 미표시. PUT/POST 요청 DTO에서 필드를 제거하지 말고 기존 응답값을 유지, null·신규 행은 `""`(추가 확정 4).
10. 룰렛 chance: 단위 해석 없이 입력값 그대로 표시·전송. 휠 조각은 chance 비율(`segment.weight`). 합계는 `chanceTotalLabel`에 그대로 합산 표시.
11. 보상 가져오기: 원본 eventId 직접 입력 → `get{Kind}Items` 조회 → 현재 편집 보상 전체 교체(미저장) → 저장 버튼으로 PUT. 새 이벤트 기간(일수)을 넘는 DAILY day가 있으면 warnings로 안내만 하고 저장은 허용한다(추가 확정 5). 가져온 항목의 id는 요청 DTO에 없으므로 버린다.
12. 시간: KST. 날짜 선택값 "YYYY-MM-DD" → ISO `+09:00` 변환. 표시도 KST.

## 역할별 상세 작업 (Logic)

작업 공간: 위 event-api-shared. 순서대로 진행한다.

### 1. 공통 lib (pages 각 도메인 `lib/` 또는 공유가 필요하면 제안 후 결정)
- KST 변환: `toKstStartIso(date)`, `toKstEndIso(date)`, ISO → `EventDateRange`, 표시 라벨(`YYYY-MM-DD HH:mm`). 기존 `src/shared/lib/utils/date.util.ts`(dayjs utc/timezone) 재사용 조사.
- ID·code 자동 생성, 숫자 입력 검증(id/objectId int64 문자열 → number 안전 범위, amount/chance number, day·sortOrder 정수 ≥1).
- 보상 행 편집 상태: 로컬 key 발급, 추가/삭제/순서 이동, 행 순서 → `sortOrder`(1부터) 재부여.
- DAILY day → 날짜 매핑, 월 캘린더 weeks 생성(일요일 시작, 이벤트 기간 달로 이동 제한), 기간 일수·초과 day 판정.
- configs 병합: 고정 표 + 응답 → `EventConfigField[]`; 저장값/초안 분리; PATCH payload 생성(출석 key/value, 룰렛 +type).
- 요청 DTO 생성: POST(id,code,startAt,endAt,items), PATCH(code,startAt,endAt,isActive), PUT items.

### 2. controller hook (pages/{event-attendance|event-roulette}/hook/)
- 목록: `EventAttendanceListController` / `EventRouletteListController` 반환. `use{Kind}EventListQuery({page,size})`. 결과 null·필드 null 구분(행 label은 "-").
- 등록: `EventAttendanceFormController` / `EventRouletteFormController`. `useCreate{Kind}EventMutation`. submit.label "등록", 성공 시 목록 이동.
- 상세: `EventAttendanceDetailController` / `EventRouletteDetailController`.
  - info.save.label "기본 정보 저장" → `useUpdate{Kind}EventMutation`
  - configs → `useUpload{Kind}EventConfigImageMutation` + `useUpdate{Kind}EventConfigsMutation`, `save.label` "텍스트 설정 저장", `isBusy`는 업로드·저장 중
  - rewards.save.label "보상 저장" → `useUpdate{Kind}EventItemsMutation`
  - summary는 저장된 서버 값 기준
  - 저장 성공 후 캐시 갱신은 entity mutation이 처리. 서버 재조회 값으로 편집 초안 재초기화 정책을 정한다.
- 아이템 검색·보상 가져오기 상태를 editor controller에 포함(`ItemSearchController`, `RewardCopyController`). 가져오기는 원본 ID를 query 키로 한 조회(`use{Kind}EventItemsQuery` 또는 `queryClient.fetchQuery`) 중 선택.
- 이미지 크게 보기 `onImagePreview(url)`: 기존 `src/shared/ui/image-modal`은 pubsub `open-image` 구독 방식인데 **현재 app·셸 어디에도 마운트돼 있지 않다**. 셸/페이지에 `ImageModal` 마운트 후 publish하거나 다른 방식을 제안한다.
- 파일 형식 검증(jpg/jpeg/png)은 controller에서 수행하고 field.errorMessage로 표시.

### 3. page 진입·라우트
- `pages/event-attendance/ui/event-attendance-{list|detail|form}-page.tsx` 에서 controller → View 연결, `index.ts`에 Page export 추가.
- `src/app/router/routes.tsx`에 `/events` + `EventAdminShell` + children 등록.
- 셸 진입 메뉴 연결 여부(다른 셸에서 /events로 가는 링크)는 요청 범위 밖.

## 연결 계약 (props/callback)

- 공용: `~/widgets/event-admin` — `EventBasicFieldsController`, `EventConfigTabController`/`EventConfigField`, `EventSaveController`, `ItemSearchController`, `RewardCopyController`, `EventLoadFailure`, `EventDetailTabController`/`EventDetailTabKey`, `EventSummaryValue`.
- 출석: `~/pages/event-attendance` — `EventAttendanceListController`, `EventAttendanceDetailController`, `EventAttendanceFormController`, `AttendanceRewardEditorController`(calendar, dayGroups, dayEditor, accumulated, warnings, summary), `ATTENDANCE_CONFIG_FIELDS`, `ATTENDANCE_REWARD_TYPES`.
- 룰렛: `~/pages/event-roulette` — `EventRouletteListController`, `EventRouletteDetailController`, `EventRouletteFormController`, `RouletteRewardEditorController`(segments, rows, highlightedKey), `ROULETTE_CONFIG_FIELDS`.
- View는 입력값을 문자열로만 받고 보낸다. 검증 메시지는 `*Error` 필드로 전달. 칩/행은 sortOrder 오름차순으로 전달한다.
- `EventBasicFieldsController.isIdEditable`: 등록 true, 상세 false. 상세는 `activation` 전달, 등록은 생략.
- `AttendanceCalendarController.emptyMessage`: 기간 미입력 등 캘린더를 그릴 수 없을 때 문구, 이때 `weeks`는 빈 배열.
- `dayGroups`: 목록 보기용. 기간 내 모든 일차를 포함할지 보상 있는 날만 포함할지 Logic이 정하되 View는 둘 다 표시 가능.

## 추가 확정 사항 (사용자 답변 2026-09-17)

1. 기간 시각: 시작일 `YYYY-MM-DDT00:00:00+09:00`, 종료일 `YYYY-MM-DDT23:59:59+09:00`으로 전송한다.
2. 자동 입력 ID·code를 사용자가 한 번이라도 직접 수정했다면, 이후 시작일을 바꿔도 **덮어쓰지 않는다**. 수정하지 않은 필드만 자동 갱신한다(필드별 "사용자 수정" 상태 관리).
3. 서버는 제공된 고정 키 상수를 그대로 configs로 응답한다고 본다. **응답에 없는 키는 화면에 표시하지 않고** PATCH에도 포함하지 않는다.
   - `EventConfigField`는 응답 configs에 존재하는 키로만 만든다. 표시 순서는 고정 키 표 순서, 표에 없는 응답 키가 오면 표 뒤에 응답 순서로 둔다(kind는 응답 type이 `IMAGE`면 IMAGE, 그 외 TEXT).
   - `isUnset`은 "키는 있으나 configValue가 null"인 경우만 뜻한다. 이 키에 값을 입력·업로드하면 PATCH에 포함한다(응답에 존재하는 키이므로).
   - PATCH payload = 응답에 존재하는 키 전체(TEXT 저장 시 초안 반영, IMAGE 교체 시 해당 키만 새 url, 나머지는 저장값). null 저장값은 `""`로 전송할지 여부는 명세상 non-null 필수이므로 `""`로 보낸다.
4. 룰렛 신규 보상 행의 `objectImageUrl`은 빈 문자열 `""`로 전송한다. 기존·가져온 행은 원본 값(null이면 `""`)을 유지한다.
5. 보상 가져오기 후 기간을 넘는 day는 **경고만** 하고 저장을 막지 않는다. 가져오는 보상은 item 기반이라 이벤트 기간과 무관하다는 것이 사용자 설명이다. warnings 문구도 "저장 불가"가 아닌 참고 안내로 작성한다.

## 실행한 명령·검증

| 명령 | 결과 |
| --- | --- |
| 중앙 formatting.py apply 직접 호출 | guard가 다른 저장소 대상으로 차단 → `npm run lint` PreToolUse 자동 포맷으로 대체(Prettier 적용 확인) |
| `npm run lint` | 1차 react-refresh 오류(탭 상수 export) 수정 후 통과 |
| `npm run build` | 통과(기존 tsconfig-paths 안내, 500kB chunk 경고) |
| `node --test tests/events-contract.test.mjs tests/events-query-mutation.test.mjs tests/logic-api-contract.test.mjs tests/logic-api-types.test.mjs tests/common-response-contract.test.mjs` | 24 pass / 0 fail |
| `git diff --check` | 통과 |

실행하지 않은 검증: 브라우저 렌더링·시각 확인(요청 없음), 전체 테스트 38개 파일, 실서버 연동. controller 부재로 화면은 아직 라우트에서 렌더되지 않는다.

## 후속 인계: 보상 objectName 연결 (2026-09-21, UI 화면 수정 이후)

사용자 확인 결과 보상 응답에 `objectName`이 추가될 예정이다. View는 이름을 표시할 자리를 이미 갖췄고, 계약이 선택 필드라 controller를 고치기 전에도 build가 통과한다.

| 계약(선택 필드) | 위치 | 의미 |
| --- | --- | --- |
| `AttendanceRewardChip.objectNameLabel?: string \| null` | `src/pages/event-attendance/model/event-attendance-reward.types.ts` | 캘린더·일차 목록 칩의 첫 줄. 없으면 `objectIdLabel` 표시 |
| `AttendanceRewardRow.objectName?: string \| null` | 같은 파일 | 일일·누적 보상 행의 ID 입력 아래 이름 |
| `RouletteWheelSegment.objectNameLabel?: string \| null` | `src/pages/event-roulette/model/event-roulette.types.ts` | 휠 조각 tooltip |
| `RouletteRewardRow.objectName?: string \| null` | 같은 파일 | 룰렛 보상 행의 ID 입력 아래 이름 |

Logic 작업:

1. `attendanceEventItemResponseSchema`와 `rouletteEventItemResponseSchema`에 `objectName: z.string().nullable()`을 추가한다. 다른 응답 필드와 같이 존재 필수·값 nullable 규칙을 따른다.
2. 요청 DTO에는 추가하지 않는다. 명세에 요청 필드로 확정되기 전까지 저장 시 이름을 보내지 않는다.
3. `attendanceDrafts`(`src/pages/event-attendance/lib/attendance-rewards.ts`)와 `rouletteDrafts`(`src/pages/event-roulette/lib/roulette-rewards.ts`) draft에 `objectName`을 보존한다. 보상 가져오기로 교체할 때도 원본 이름을 함께 가져온다.
4. controller에서 위 표의 필드를 채운다. `attendanceChip`은 `objectNameLabel`, `rowController`는 `objectName`, 룰렛 `segments`·`rows`도 동일하다.
5. 아이템 검색으로 objectId를 선택하면 선택 결과의 `name`을 draft `objectName`에 함께 넣는다(`useEventItemSearch`의 onSelect 계약 확장). ID를 직접 입력해 이름을 모르면 null로 두고 UI가 "이름 확인 중"으로 표시하게 둔다.
6. 회귀 테스트: 응답 objectName 보존, 요청 payload 미포함, 검색 선택 시 이름 반영.

사용자 확정(2026-09-21): `objectName`은 **응답에만** 포함한다. 요청 DTO에는 넣지 않는다. ID를 직접 입력해 이름을 모를 때는 별도 조회 없이 UI의 "이름 확인 중" 표시를 그대로 둔다.

## 룰렛 chance 합계 100 검증 (2026-09-21, 이 세션에서 구현 완료)

사용자 확정: chance 합계 기준은 **100**이고 초과는 **경고만** 한다(저장 차단 없음). 사용자가 이 세션의 역할을 통합 구현으로 넓히는 데 동의해 controller까지 함께 구현했다.

- `src/pages/event-roulette/lib/roulette-rewards.ts`: `ROULETTE_CHANCE_TOTAL`(100), `rouletteChanceTotal`, `rouletteChanceOverflow` 추가. 숫자로 읽히는 chance만 더하고 잘못된 입력은 기존 행 검증이 담당한다.
- `src/pages/event-roulette/hook/use-roulette-reward-editor.ts`: 초과 시 `warnings`에 초과량 문구를 추가한다. `isValid`와 payload는 바꾸지 않는다. `chanceTotalLabel`도 공용 합계 함수를 쓴다.
- 회귀 테스트: `tests/events-controller.test.mjs`의 "룰렛 chance 합계가 100을 넘으면 경고만 하고 저장은 막지 않는다"에서 90·100·115를 검증한다.
- 합계가 100 미만인 경우는 경고하지 않는다. 휠 caption의 "남은 chance"로만 보여준다.

## 관련 스킬·정책

task-role-routing(logic.md), git-branch-strategy, coding-convention, implementation-quality, data-fetch-layer, type-definition, documentation. Logic은 시작 시 이 문서·API handoff·실제 Git 상태를 함께 읽는다.
