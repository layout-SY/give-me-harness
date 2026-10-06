# 문의 관리 Logic 인계

## 목표 및 현재 상태

문의 목록·상세·유형 관리 controller를 구현해 UI 세션에 전달하는 작업이다. **미완료**이며 controller·view·route 연결은 아직 구현하지 못했다. 기존 entity 5개 파일과 기존 테스트 1개 파일에만 변경이 있다. 연결 worktree의 새 디렉터리 생성이 sandbox에서 실패했다. 사용자 `명령 실행 승인` 후 쓰기 예약 복구는 완료했지만, 부분 편집의 정상 완료가 확인되지 않아 포맷은 아직 차단돼 있다.

## 최신 복구 결과

- 사용자 승인 작업 `bf0fe370373e40778a940621871fd4e4`를 기본 checkout에서 1회 실행하여 exit 0, stage `done`을 확인했다.
- 복구한 쓰기 ID: `d2adf1e26dae433ebfce184136d21451271a7f225bdacd03730f2be2beeb5f5b`. 실패한 편집 호출은 `exec-55172f9d-8c1b-48f6-8267-e10d2b89e862`다.
- 소스·커밋·branch 변경 없이 종료된 호출의 쓰기 예약만 해소했다. 동일 복구를 반복하지 않는다.
- 복구 뒤 `formatting.py check`는 여전히 10개 대상의 결과 미확인을 보고했다. 현재 formatter는 write-recovery 후 정상 수정 도구로 부분 작업을 마무리해야 이전 기록을 대체한다. 기록 파일을 직접 고치거나 포맷 완료로 간주하지 않는다.
- 처음 연결 worktree에서 준비한 `2266c3cd3493466692fc457187c63ed0`은 실행하지 않았다. wrapper가 workdir를 다르게 인식해 실행 위치 검사가 실패하여, 같은 저장소의 기본 checkout에서 복구 요청을 새로 준비했고 승인된 최신 요청만 실행했다.
- 현재 세션에서도 복구 실행이 가능했으므로, 반드시 새 세션에서만 복구할 수 있다는 앞선 설명은 정정한다. 새 controller 디렉터리 생성 권한은 별도로 남아 있다.

## Assignment 이동과 역할

- 보내는 host·session·role: Codex · `inquiry-controllers` · logic.
- 받는 세션: 이 worktree에 쓰기 권한을 가진 logic 세션. 이후 ui 세션.
- requested_roles: logic, UI 연결.
- confirmed_roles: 현재 logic. UI handoff에서 UI 구현은 후속 ui 세션으로 지정했다.
- completed_roles: 없음.
- next_role: logic → ui.
- 사용자 요청: handoff를 읽고 필요한 구현 후 UI 연결. 미정 3개 질문에도 모두 답변했다. 동일 질문을 반복하지 않는다.

## 확정된 사용자 결정

1. 유형 관리 표는 10개씩 조회한다. 문의 목록의 유형 필터는 size 10으로 모든 페이지를 조회한다.
2. 검색어가 있고 검색 대상이 미선택이면 TITLE로 검색한다. 검색어가 비면 by·keyword를 모두 생략한다.
3. 문의에서 사용하는 유형의 삭제 허용 여부는 서버가 판단한다. 실패는 기존 다이얼로그의 서버 오류 메시지로 알린다.
4. 나머지 화면·상태·props 계약은 `.claude/logs/sessions/inquiry-ui/handoff.md`의 확정 내용을 따른다. 문의 목록 size 10, sort 생략, 상태 표시는 접수/처리중/완료, 답변 POST 성공 뒤 별도 상태 PATCH 없음, 완료 버튼만 COMPLETED 요청, 유형 등록 code 선택·수정 name만 허용.

## 보내는 위치와 변경 상태

- project: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`.
- branch: `feature/inquiry-ui`.
- HEAD: `4b0b7db45aa9d15bf918a1a084370594e138a124`.
- 실제 worktree·실행 디렉터리: `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/inquiry-ui`.
- 확인 시점: 2026-09-28, 본 인계 작성 직전.
- 완료 commit: 없음. staged 변경: 없음.
- unstaged 변경 6개:
  - `src/entities/inquiries/model/inquiry.enum.ts`: 미사용 i18n 라벨 상수 2종 제거. src·tests에 사용처가 없음을 확인했다.
  - `src/entities/inquiries/index.ts`: INQUIRY_TYPE_CODES와 useAllInquiryTypesQuery 공개.
  - `src/entities/inquiries/model/query-keys.ts`: types 접두사 아래 전체 조회 key 추가.
  - `src/entities/inquiries/model/inquiry-type-query-options.ts`: 기존 API·parser를 재사용하는 전체 페이지 조회 추가. 중간 실패·잘못된 페이지·취소를 전파하고 부분 목록은 반환하지 않는다.
  - `src/entities/inquiries/hook/use-inquiry-type-list-query.ts`: 전체 조회 hook 추가.
  - `tests/inquiry-types-query-mutation.test.mjs`: 전체 페이지 조회·캐시 무효화·중간 실패·빈 결과·잘못된 페이지·취소 검증 4개 추가. 아직 실행하지 못했다.
- Git status 기준 untracked 소스: 없음. 자기 산출물은 `.codex/logs/sessions/inquiry-controllers/`이며 status에 표시되지 않는다.
- 보존할 기록: `.claude/logs/sessions/inquiry-ui/handoff.md`는 다른 세션 문서이므로 수정하지 않는다.
- 기본 checkout에서 별도로 진행 중인 maintenance 변경 및 `docs/admin-routes.md`를 건드리지 않았다.

## 인계 대상 작업 공간

### 작업 공간: inquiry-ui

- 기존 branch·worktree·실행 디렉터리·HEAD는 위와 같다. 같은 Git common directory를 확인했다.
- 직접 부모: sy-main. UI handoff의 relation create 완료 기록에서 확인.
- 같은 기능을 Logic → UI 순차로 연결하므로 공간을 공유한다. 새 branch/worktree는 필요 없다.
- 진입 시 HEAD·dirty 상태를 다시 확인하고 위 6개 변경을 보존한다.
- 이 경로의 새 디렉터리 생성 권한을 실제로 확보해야 한다. 현재 세션의 기본 cwd와 writable root는 기본 checkout이다. 현재 세션에서 권한을 부여할 수 있으면 이어가며, 그렇지 않으면 이 worktree를 쓰기 허용 workspace로 지정한 `--role logic` 세션에서 이어간다.
- commit·merge는 아직 승인받지 않았다. 기본 checkout의 다른 작업과 합치지 않는다.

## Logic의 남은 작업

1. 쓰기 예약 복구는 위 최신 결과대로 완료했다. 실제 diff를 읽고 정상 수정 도구로 부분 작업을 마무리하여 포맷의 미확인 기록을 해소해야 한다. 새 디렉터리 생성 권한을 먼저 확보한다. 중앙 상태 파일은 직접 수정하지 않는다.
2. entity 변경의 포맷과 새 4개 테스트를 먼저 검증한다. 전체 유형 hook은 `useAllInquiryTypesQuery(10)`이며 기존 유형 mutation의 types 접두사 무효화에 포함된다.
3. UI handoff의 타입을 type alias로 작성한다:
   - `src/pages/inquiry/model/inquiry-list.types.ts`, `inquiry-detail.types.ts`.
   - `src/pages/inquiry-type/model/inquiry-type.types.ts`.
4. `src/pages/inquiry/model/inquiry.config.ts`에 INQUIRY_ROUTES, INQUIRY_PAGE_SIZE, 상태·검색 옵션을 작성한다. 유형 page size·code options는 `src/pages/inquiry-type/model/inquiry-type.config.ts`에 둘 수 있다.
5. `src/pages/inquiry/hook/use-inquiry-list-controller.tsx`: 기존 문의 Query + 전체 유형 Query, 검색 초안/적용 상태, pagination, 로딩·오류·재시도·상세/유형 화면 이동을 연결한다.
6. `src/pages/inquiry/hook/use-inquiry-detail-controller.tsx`: route의 inquiryId, 조회 오류, 저장된 답변·편집 초안, POST/PUT/DELETE answer, 완료 PATCH, 문의 삭제와 목록 복귀. 잘못된 ID·중복 요청·실패 시 초안 보존을 확인한다.
7. `src/pages/inquiry-type/hook/use-inquiry-type-controller.tsx`: 10개 pagination, 등록 코드·이름, 선택 유형의 이름만 수정, 확인 후 삭제, 오류·재시도·목록 복귀.
8. 테스트는 기존 Node test + Vite SSR + MSW 방식을 사용한다. 새 프레임워크는 도입하지 않는다.

## UI의 후속 작업

- Logic 완료 뒤 같은 inquiry-ui 공간의 최신 타입·controller와 diff를 읽는다.
- `.claude/logs/sessions/inquiry-ui/handoff.md`의 목록·상세·유형 관리 view/page를 작성하고 controller를 props로 연결한다.
- `src/app/router/routes.tsx`에 `/manage/operations/inquiries`, `/manage/operations/inquiries/types`, `/manage/operations/inquiries/:inquiryId`를 등록한다.
- `src/widgets/side-navigation/lib/build-navigation-items.ts`에 메뉴를 연결한다.
- controller 타입과 config는 서로 중복 생성하지 않고 순차 수정한다. 현재 UI view/page/route는 하나도 추가되지 않았다.

## 재사용 근거와 검증 명령

- src/entities/inquiries의 DTO·API·parser·조회/mutation 훅·캐시 무효화 및 src/shared/api/common/response.dto.ts 재사용.
- src/pages/item/hook/use-item-list-data.tsx의 조회·오류 방식, src/pages/item-category/hook/use-item-category-controller.tsx의 선택·편집 방식, src/shared/ui/dialog 재사용.
- tests/events-controller.test.mjs와 tests/news-list-controller.test.mjs의 SSR 상태 전이 검증 참고.
- 포맷: 현재 bundle의 `python3 -I .../policy/.agent-policy/runtime/formatting.py apply`를 실제 worktree에서 실행한다.
- 테스트: `node --test --test-concurrency=2 tests/inquiries-contract.test.mjs tests/inquiries-msw.test.mjs tests/inquiries-mutation.test.mjs tests/inquiry-types-contract.test.mjs tests/inquiry-types-query-mutation.test.mjs` 및 새 controller 테스트.
- `npm run lint`, `npm run build`. package.json에 test script가 없어 `npm run test`는 사용하지 않는다.

## 실행 결과와 차단 근거

- npm ci --offline --ignore-scripts --no-audit --no-fund: 최초 sandbox EPERM 후 사용자 권한 승인으로 성공, 341개 설치. lockfile 변경 없음.
- apply_patch: plan 작성 성공. entity 5개 편집 후 새 `src/pages/inquiry/model` 디렉터리 생성 실패로 다중 patch 종료. 해당 새 파일은 존재하지 않는다.
- 명시적 mkdir의 권한 요청: 정책 훅이 Edit/Write/apply_patch 사용을 요구하며 차단.
- 절대 대상과 workdir를 적은 apply_patch shell의 권한 요청: 실행 위치를 확인할 수 없다는 정책 훅 오류로 차단. 소스 추가 없음.
- 기존 테스트 파일의 apply_patch: 성공.
- 중앙 포맷: exit 2, `포맷 미완료: 결과 미확인 코드 쓰기를 먼저 확인한 뒤 포맷하세요.`
- 보호 실행기 --help와 읽기 검색: 정책 훅 차단. 동일 명령을 재시도하지 않았다.
- lint·test·build: 포맷이 차단돼 미실행. PASS로 판단하지 않는다.

## 협업·통합

- Logic 수정·검증 완료 → UI 구현·연결·검증 → 사용자 승인 후 commit 및 feature/inquiry-ui → 직접 부모 sy-main 통합.
- 형제 citizen-proposal-vote-api와 기본 checkout의 다른 작업이 진행 중이다. 라우터·메뉴를 통합하기 전에 최신 변경을 비교한다.
- 산출물 책임: contributor. 원본 UI handoff의 미정 3개는 위 사용자 답변으로 모두 확정됐다. 업무 정책 질문은 반복하지 않는다.
