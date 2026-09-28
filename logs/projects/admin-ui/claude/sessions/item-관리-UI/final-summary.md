# 최종 요약 — 아이템 관리 UI

- 작업 위치: `/private/tmp/asan-metaverse-admin-ui-item-ui` · `feature/item-ui` (부모 `sy-main` `b4e8883`)
- Git: `sy-main`에 사용자 gender 변경 커밋(`b4e8883`), `feature/item-ui` worktree 생성. 이번 구현은 **미커밋**.

## 구현

| 경로 | 내용 |
| --- | --- |
| `/manage/items` | 목록: KPI(전체 건수), 필터(메인·서브 카테고리, 성별, 상태, 검색어), 체크박스 선택 + 상태 일괄 변경, 행 클릭 시 상세 이동 |
| `/manage/items/new` | 등록: ID 직접 입력, 분류·판매 정보, 메타버스 판매·이벤트 보상 제외 토글, 이미지 업로드(서브 카테고리 선택 후) |
| `/manage/items/:itemId` | 상세·수정: 같은 폼, 앱 노출 토글, 이벤트 보상 제외는 토글 API 즉시 반영, 이미지 삭제 API, 저장(PATCH), 삭제 |
| `/manage/items/category` | 카테고리 관리: 메인·서브 표 + 우측 등록/수정 패널, 삭제 |

- 구조: proposal과 같은 `page → controller → view`, `hook/`(controller·search-state·data·process), `model/`(config·types), `lib/`(순수 변환)
- 공용 변경: `Table`에 선택형 `selection` prop 추가(미전달 시 기존과 동일), `ToggleSwitch`에 `ariaLabel` 추가
- 셸·메뉴: `ManageAdminShell`, `buildManageNavigationItems`(아이템 관리 그룹만), `_navigation2`에 "아이템 목록" sublink
- entity 표시 상수: `item.enum.ts` 라벨 한국어, `ITEM_STATUS_COLORS`, `ITEM_PAYMENT_TYPES`(POINT)

## 구현 중 선택한 표시·동작 (사용자 확인 권장)

- 성별 라벨: NONE=공용, MAN=남성, WOMAN=여성 / 상태 라벨: 판매 대기·판매중·판매 보류·판매 종료
- 수정 PATCH는 모든 필드를 현재 값으로 보낸다(DTO가 전 필드 필수·nullable). 이벤트 보상 제외는 서버 값, 이미지는 새 업로드 uuid 또는 null
- 등록 필수 검증은 ID(양의 정수)와 가격 형식뿐이다. 이름 등 필수 여부는 서버 계약 미확인이라 강제하지 않았다
- NEW 배지 종료는 `datetime-local` 입력 → 브라우저 offset 포함 ISO
- 이미지 미리보기는 새 탭으로 연다(`ImageModal`이 앱에 마운트되어 있지 않음)

## 검증

- `npm run lint`: 통과
- `npm run build`: 통과(기존 chunk 크기 경고만)
- `node --test tests/item-form.test.mjs`: 6/6 통과
- `tests/item-category-*.test.mjs`, `tests/logic-api-types.test.mjs`: 통과
- `tests/items-contract.test.mjs`, `tests/items-query-mutation.test.mjs`: 14건 실패 — fixture가 gender 문자열(`"COMMON"`)을 사용. `sy-main`(`b4e8883`)에서도 동일하게 14건 실패함을 확인. Logic handoff에 기록
- 실행하지 않음: 전체 `tests/` 일괄 실행(hook이 glob 인자를 차단), 브라우저 수동 확인

## Logic 작업 확인 후 조정 (2026-09-18)

- Logic이 `entities/items/lib/item-id.ts`(채번 함수·코드표)와 `tests/item-id.test.mjs`를 추가하고, 등록 controller에 자동 채번을 연결했으며, items 테스트의 gender를 숫자로 갱신했다(14건 실패 해소).
- 확인된 위험: latest ID 계약이 문서와 달라(sub·gender만 조회) 서브 코드를 공유하는 카테고리의 ID 중복 가능, 6자리가 아닌 objectId의 처리가 문서와 다름, latest 조회 중 이전 입력 ID로 저장 가능.
- 사용자 결정: "id 자동 완성 로직은 사용하지 않는 형태로 구현 후에 마무리". 등록 controller를 관리자 직접 입력으로 되돌렸다. 채번 함수·테스트와 `latestItemIdQueryOptions.enabled`는 향후 사용을 위해 유지한다.
- 재검증: `npx eslint .`, `npx tsc -b`, `npx vite build` 통과, item 관련 테스트 7개 파일 48건 통과.
- `npm run lint`·`npm run build`는 format hook이 Logic이 수정한 `src/entities/items/index.ts`의 기록 불일치로 차단했다. 해당 파일은 `prettier --check` 통과. hook 해소를 위해 Logic 파일을 수정하지 않았다.

## 커밋·병합 (2026-09-18)

- `feature/item-ui` 커밋 `7bcc83e`(47 files) → `sy-main` ff-only 병합. `sy-main` HEAD `7bcc83e`
- 병합 후 검증: `npm run lint`, `npm run build` 통과(완료 작업 `15dd411f51054e24a65be4fd92294d06`)
- 정리 미포함: `feature/item-ui` branch와 worktree `/private/tmp/asan-metaverse-admin-ui-item-ui` 유지
- 형제 `feature/event-attendance-roulette-api` 병합 시 `routes.tsx`, `build-navigation-items.ts` 텍스트 충돌 가능
- 커밋 전 format hook 기록을 맞추려고 `src/entities/items/index.ts`를 동일 내용으로 재기록함(내용 변경 없음, 사용자 "무시하고 merge" 지시 후)

## 후속

- Logic: `handoff.md`(ID 채번, latest ID 계약 차이, items 테스트 gender 갱신)
- Git: 변경 commit·`sy-main` 병합은 사용자 승인 후
