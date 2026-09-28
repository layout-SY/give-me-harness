# 인계 — 아이템 ID 채번과 item 계약 정리 (Logic)

## Assignment 이동

- 보내는 host·session·role: Claude Code · item-관리-UI · ui
- 받는 host·session·제안 role: 미정 host · 새 세션 · logic

## 역할 라우팅

- 요청 역할(`requested_roles`): ui
- 확인된 역할(`confirmed_roles`): ui
- 완료 역할(`completed_roles`): ui (아이템 관리 화면. 결과는 같은 session의 `final-summary.md`)
- 다음 제안 역할(`next_role`): logic
- 역할 판단 근거: ID 채번은 API 조회·계약 변환·폼 상태 전이를 포함한 기능 로직이며 UI 계층 경계 밖이다.
- 사용자 확인: 2026-09-18 "item id 관련 로직은 … 나중에 logic이 구현할 거니 핸드오프로 만들어놔. 지금은 그냥 관리자가 직접 id를 입력하는 방식으로"

## 목표 및 현재 상태

- 목표: 아이템 신규 등록 시 `id`를 클라이언트에서 채번해 등록 폼에 자동으로 채운다.
- 현재: 등록 화면(`/manage/items/new`)은 관리자가 ID를 직접 입력한다. 채번은 구현하지 않았다.
- 사용자 언급: 채번 문서에 다른 프로젝트의 흔적(예: 화폐 단위)이 남아 있어 **지금 바로 적용하지 않는다**. 착수 전에 아래 미확정 사항을 사용자에게 확인한다.

## 채번 규칙 (사용자 제공 문서 원문 요약)

결과 형식: `[mainCode][subCode][genderCode][seq3]` — 예: `221046` = ATTIRE(2) + TOP(2) + WOMAN(1) + 일련번호 046

```
itemId = Number( mainCode + subCode + genderCode + latestObjectId[3..5] ) + 1
```

### 입력

| 입력 | 역할 | 비고 |
| --- | --- | --- |
| `mainCategoryId` | 1번째 자리 | 없으면 채번하지 않음 |
| `subCategoryId` | 2번째 자리 | 메인 코드 표의 하위에서만 조회 |
| `gender` | 3번째 자리 | number가 아니면 채번하지 않음 |
| 최신 `objectId` | 4~6번째 자리 기준 | 같은 카테고리·성별 그룹의 최대 ID |

이름·가격·상태·이미지·판매 범위는 ID에 영향 없음.

### 메인 카테고리 코드

| mainCategoryId | 코드 | 의미 |
| --- | --- | --- |
| 1 | `1` | MONETARY |
| 6 | `2` | ATTIRE |
| 11 | `4` | MOUNT |
| 15 | `6` | CONSUMABLE |

### 서브 카테고리 코드 (`[mainCategoryId][subCategoryId]`)

| main | sub | 코드 | 의미 |
| --- | --- | --- | --- |
| 1 | 2 | `0` | SORIA |
| 1 | 3 | `1` | SORIA_PLUS |
| 1 | 4 | `2` | POINT |
| 1 | 5 | `3` | SUBSCRIPTION |
| 6 | 7 | `2` | TOP |
| 6 | 8 | `3` | BOTTOM |
| 6 | 10 | `4` | FOOTWEAR |
| 6 | 9 | `5` | HAIR |
| 11 | 12 | `0` | HOVERBOARD |
| 11 | 18 | `0` | BOOSTBOARD |
| 11 | 20 | `1` | AIRMOBILE |
| 11 | 19 | `2` | HOVERBIKE |
| 15 | 17 | `0` | RECOVERY |
| 15 | 16 | `0` | TICKET |
| 15 | 21 | `8` | BOX |

같은 코드를 쓰는 서브 카테고리(HOVERBOARD·BOOSTBOARD 등)는 같은 일련번호 공간을 공유한다. 표에 없는 카테고리는 해당 자리가 빈 문자열이 된다.

### 성별 코드

| gender | enum | 코드 |
| --- | --- | --- |
| NONE | 0 | `0` |
| MAN | 1 | `0` |
| WOMAN | 2 | `1` |

### 계산

```
genderCode = (gender === WOMAN) ? "1" : "0"
prefix     = mainCode + subCode + genderCode      // 세 입력이 모두 있을 때만, 아니면 ""
seq        = String(objectId).slice(3, 6)
nextId     = Number(prefix + seq) + 1
```

- `objectId`가 6자리가 아니면 `slice(3, 6)`이 깨진다. `0`이면 `Number(prefix) + 1`.
- CREATE 모드에서만 실행. 메인/서브/성별이 바뀔 때 재계산. 메인이 바뀌면 서브를 비우고 서브·성별이 다시 채워지기 전에는 채번하지 않는다.
- 실행 조건 불충족(모드≠CREATE, main 없음, sub 없음, gender가 number 아님) 시 return.
- 통과하면 `id = nextId`. 화면 ID 입력란은 disabled.
- 등록 payload는 `id`가 있을 때만 포함 (`...(id ? { id } : {})`). UPDATE는 기존 id 유지.

## 문서와 현재 코드의 계약 차이 (착수 전 사용자 확인 필요)

| 항목 | 채번 문서 | 현재 코드 (`src/entities/items`) |
| --- | --- | --- |
| 최신 ID endpoint | `GET /v1/items/latest/item` | `GET /admin/items/latest/id` (`items.api.ts` `getLatestId`) |
| 조회 파라미터 | `mainCategoryId, subCategoryId, gender` | `subCategoryId, gender` (`latestItemIdQuerySchema`, strict) |
| 응답 | `{ objectId: number }` | `number \| null` (`parseLatestItemId`) |
| 등록 DTO `id` | optional | `nullableId` 필수 키 (`postItemRequestSchema`) |
| 카테고리 ID·코드표 | 위 표 고정값 | 서버 카테고리 목록(`GET /admin/items/categories`)의 id. 표의 id와 실제 id 일치 여부 미확인 |

## 보내는 작업의 위치와 변경 상태

- project·저장소 루트: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui` (Git common dir)
- branch·worktree: `feature/item-ui` · `/private/tmp/asan-metaverse-admin-ui-item-ui`
- 인계 기준 commit: 부모 `sy-main` `b4e8883`(gender → `z.number().int()`, 사용자 변경을 승인 후 커밋). UI 결과 commit은 `final-summary.md` 참조.
- 보존할 내용: UI 세션이 만든 `src/pages/item/**` 등록 폼 구조.

## 인계 대상 작업 공간

### 작업 공간: item-ui

- 수행할 기능: 등록 폼 ID 자동 채번, latest ID API 계약 정합, 기존 item 테스트의 gender 정리
- 사용할 역할: logic
- 목적지 branch·worktree: `feature/item-ui` · `/private/tmp/asan-metaverse-admin-ui-item-ui` (기존 공간, UI 완료 후 순차 사용). UI가 먼저 `sy-main`에 병합되었다면 `sy-main`에서 새 작업 공간을 사용자와 정한다.
- 직접 부모: `sy-main` (relation graph 등록)
- 진입 전 확인: `git -C <worktree> status`, HEAD, `src/pages/item/hook/use-item-create-controller.tsx` 존재

## 역할별 상세 작업

### 역할·하위 작업: logic · ID 채번

- 남은 작업:
  1. 사용자에게 계약 차이 표를 확인받는다 (endpoint·파라미터·응답·카테고리 ID 일치).
  2. 확정된 계약으로 `items.dto.ts`의 latest 쿼리/응답 스키마, `items.api.ts` `getLatestId`, `items.parser.ts` `parseLatestItemId`, `query-keys.ts` `latestId`를 조정한다.
  3. 코드표와 계산을 순수 함수로 둔다(예: `src/entities/items/lib/item-id.ts`의 `buildItemIdPrefix`, `buildNextItemId`).
  4. 등록 controller(`src/pages/item/hook/use-item-create-controller.tsx`)에서 main·sub·gender가 모두 선택되면 `useLatestItemIdQuery`로 조회해 `id`를 채우고, `ItemCreateController.fields.isIdEditable`을 false로 전달한다. 메인 변경 시 서브 초기화는 이미 UI에 구현되어 있다.
  5. `postItemRequestSchema.id`를 optional로 바꿀지 사용자 확인 후 반영하고, payload 빌더(`src/pages/item/lib/item-form.model.ts` `buildItemCreatePayload`)를 맞춘다.
- UI 계약: 등록 view는 `fields.id`(string)와 `fields.isIdEditable`(boolean)만 사용한다. 값이 채번되면 controller가 `id`를 채우고 `isIdEditable=false`로 넘기면 입력란이 disabled가 된다.
- 기존 테스트 정리: `tests/items-contract.test.mjs`, `tests/items-query-mutation.test.mjs`가 gender에 문자열(`"COMMON"`, `"TEMP_GENDER"`)을 사용한다. gender number 전환(`b4e8883`) 이후 실패할 수 있으므로 숫자 계약으로 갱신한다.
- 완료 기준: 채번 순수 함수 단위 테스트(문서 예시 `221045 → 221046`, 비6자리·0·표 밖 카테고리), `npm run lint`, `npm run build`, 관련 `node --test` 통과.
- 미확정 사항: 위 계약 차이 표 전체, 화폐 단위 등 다른 프로젝트 흔적 정리 범위.

## 협업 순서와 Git 통합

- UI 완료·커밋 후 Logic이 같은 공간을 순차 사용하거나, UI 병합 후 `sy-main`에서 새 공간을 만든다. 공간 선택은 사용자 확인.
- 승인된 Git 작업: 없음(이 인계 범위). 모든 Git 변경은 사용자 승인 필요.
- 산출물 책임: 이 인계는 contributor 인계. Logic 세션은 자기 산출물을 새로 작성한다.

## 관련 경로와 스킬

- `src/entities/items/api/items.dto.ts`, `items.api.ts`, `items.parser.ts`, `model/query-keys.ts`, `model/item-query-options.ts`, `hook/use-latest-item-id-query.ts`, `model/item.enum.ts`
- `src/pages/item/lib/item-form.model.ts`, `src/pages/item/hook/use-item-create-controller.tsx`, `src/pages/item/hook/use-item-form-fields.ts`(`isIdEditable` 전달)
- 정책: `task-role-routing/references/logic.md`, `git-branch-strategy`

## 실행하지 않은 검증

- 채번 로직은 구현·검증하지 않았다.
