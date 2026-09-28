# 아이템 관리 UI 계획

- host·role: Claude Code · UI (inject `--role ui`)
- 작업 위치: `/private/tmp/asan-metaverse-admin-ui-item-ui` · `feature/item-ui` (부모 `sy-main`, fork `b4e8883`)
- 사용자 승인: 2026-09-18 "너가 계획한 대로 작업 진행"

## 사용자 결정

| 항목 | 결정 |
| --- | --- |
| 라우트 | `/manage` 신규 셸, 메뉴는 "아이템 관리" 그룹만 표시 |
| 화면 | 목록(우측 상세 패널 없음) · 상세/수정 · 등록 · 카테고리 관리, 삭제·일괄 상태 변경·이벤트 보상 토글·이미지 삭제 포함 |
| status·gender | `item.enum.ts` 값 사용, 라벨은 한국어(i18n 미사용) |
| gender DTO | 사용자가 `z.number().int()`로 변경 (sy-main `b4e8883`) |
| paymentType | `POINT` 고정, 선택 UI 없음 |
| saleEnv | 필드 유지, 화면 미사용 |
| 카테고리 | `parentName === null` → 메인, 그 외 `parentName`이 메인 이름인 서브 |
| Item ID | 현재는 관리자 직접 입력. 채번 로직은 Logic handoff |
| 수정 image | 신규 업로드 uuid, 미변경 시 null |
| 다중 선택 | shared Table에 선택 props 확장 |
| 참고 디자인 | 없음. proposal 패턴을 따른다 |

## 경로

- `/manage/items` 목록, `/manage/items/new` 등록, `/manage/items/:itemId` 상세·수정, `/manage/items/category` 카테고리 관리

## 예상 변경

- `src/app/router/manage-admin-shell.tsx`, `routes.tsx`
- `src/widgets/side-navigation/model/_navigation2.ts`(아이템 메뉴 sublink), `lib/build-navigation-items.ts`
- `src/entities/items/model/item.enum.ts`(한국어 라벨·상태 색·POINT), `src/entities/items/index.ts`(enum export)
- `src/shared/ui/table/table.tsx`·`table.css`(선택 props)
- `src/pages/item/**`, `src/pages/item-category/**`
- `tests/item-form.test.mjs`

## 검증

- 포맷 트리거 → `npm run lint`, `node --test`(관련 테스트), `npm run build`
