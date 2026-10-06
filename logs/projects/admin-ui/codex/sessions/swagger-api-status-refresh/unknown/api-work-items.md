# Swagger API 작업 현황 — 2026-09-30 갱신

**후속 진행 반영:** T03 이용 내역의 API·query 보정과 UI 없는 controller 구현 `7ff8247`은 `sy-main@987616b`에 병합됐다. 2026-09-30 병합 후 관련 테스트 21개·lint·build를 다시 실행해 통과했고 기본 checkout은 깨끗하다. UI 연결은 남아 있다. [구현 결과](../final-summary.md)와 [연결 계약](../handoff.md)을 참조한다. 아래 최초 갱신의 기본 브랜치 기준과 후속 작업 공간의 상태를 구분한다.

**T01 시민제안·투표 연결은 sy-main 반영 완료, T07 점검은 API·controller 반영 완료, T05 문의는 controller 반영 및 UI 별도 브랜치 구현 상태다. 나머지 항목에는 계약 보정·연결·제품 결정이 남아 있다.**

이 문서는 기존 감사 문서의 진행 상태를 갱신하는 진입 문서다. 아래 현재 상태가 기존 작업 문서의 “미구현/미정” 설명보다 우선한다. 서버 명세 원문과 상세 설명은 기존 자료를 계속 참조한다.

## 기준과 자료

- 확인일: 2026-09-29 KST.
- 기본 작업 위치: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`.
- 현재 기준: `sy-main@84d47a87f032ec5cc106f4fad8ec3a9709e901e1`.
- 이전 감사 기준: `4b0b7db45aa9d15bf918a1a084370594e138a124`.
- 현재 기본 checkout의 staged·unstaged·untracked 변경: 없음. 이 문서와 세션 기록은 Git ignore 대상이다.
- [OpenAPI 원본](../../swagger-api-coverage-audit/unknown/openapi.snapshot.json): 2026-09-28 수집본, 75 paths / 106 operations / 196 schemas. 이번에 JSON을 읽어 규모를 재확인했다. 최신 서버 명세 재수집은 하지 않았다.
- [전체 API 계약](../../swagger-api-coverage-audit/unknown/api-contracts.md), [DTO schema](../../swagger-api-coverage-audit/unknown/api-schema-catalog.md), [오류 계약](../../swagger-api-coverage-audit/unknown/api-errors-and-integration.md).
- [이전 상세 작업 문서](../../swagger-api-coverage-audit/unknown/api-work-items.md), [이전 대조표](../../swagger-api-coverage-audit/unknown/api-path-matrix.md): 최초 감사 이력이며 당시 수치를 현재 수치로 읽지 않는다.
- 이전 기준 이후 변경된 파일과 주요 잔여 DTO를 확인했다. 106개 operation 전체에 대한 신규 독립 감사나 실서버 검증을 수행한 것은 아니다.

## 기준 커밋 이후 반영

| 커밋 | 변경 | 현재 판정 |
| --- | --- | --- |
| `4b2aa3f`, 병합 `84d47a8` | 시민제안 상태·검토 저장, 제안·투표 summary, 개발 가로채기 해제 | T01의 승인된 연결 범위 sy-main 반영 |
| `b5c35a8` | maintenance 7개 API·DTO·query/mutation·controller | T07 Logic 반영, 화면 소비는 별도 |
| `840051e`, 병합 `deb11f9` | 문의 목록·상세·타입 controller, 타입 전체 조회 | T05 Logic 반영, 기존 mutation parser 과제 유지 |
| `0a39dce` | 관리자 라우트 문서 | API 계약 변경 없음 |

현재 HEAD 뒤의 기본 checkout 미커밋 소스 작업은 없다. 별도 `feature/inquiry-ui@b785adf`에는 문의 화면·라우트·메뉴 구현 커밋이 있고 `sy-main`에 아직 포함되지 않았다. 해당 worktree의 status는 깨끗하다.

## T01 — 시민제안·투표: 승인된 연결 완료

- 두 PATCH와 제안·투표 summary GET 4개가 추가되었다. 기존 목록·상세와 함께 8개 operation의 API가 존재한다.
- 근거: `src/entities/cp-proposal/api/cp-proposal.api.ts`, `src/entities/cp-vote/api/cp-vote.api.ts`, `src/pages/cp-proposal/hook/`, `src/pages/cp-vote/hook/use-cp-vote-list-data.tsx` 및 커밋 diff.
- reviewResult의 문자열/null/누락 매핑, 상태 enum 변환, void 성공 후 재조회, summary KPI 연결을 반영했다.
- 담당부서는 기존 확정대로 미지원 안내와 요청 차단을 유지한다. 미완성 API로 다시 구현 목록에 넣지 않는다.
- 개발용 시민제안·투표 MSW 가로채기를 제거했다.
- [완료 기록](../../citizen-proposal-vote-connection/final-summary.md)은 병합 후 관련 테스트 46개·lint·build 통과를 기록한다. 이번 세션에서 재실행한 결과는 아니다.
- 남은 한계: 실제 서버 권한·CORS·저장 동작과 브라우저 동작은 이 갱신으로 검증되지 않는다.

## T02 — 사용자: 계약 보정과 화면 연결 남음

- 응답 status는 명세 `SUSPENDED`, 로컬 enum은 `SUSPEND`. 변경 요청의 `SUSPEND`와 구분해야 한다.
- 포인트 direction은 명세 `RECHARGE/DEDUCT`, 로컬은 `RECHARGE`만 있다. 금액의 정수 여부와 명세 minimum 0/로컬 positive 차이, 사유 필수 여부도 확인 대상이다.
- 권한 변경 성공 parser는 `z.string()`이므로 빈 성공 응답 계약을 확인해야 한다.
- 근거: `src/entities/users/api/admin-users.dto.ts`, `admin-users.parser.ts`, `src/entities/users/model/admin-user.enum.ts`와 원본 schema.
- 다음 작업: 요청·응답별 schema 보정 후 기존 API/query/mutation을 연결할 화면과 userId 출처 확정. 차감·사유·권한 선택 정책은 임의로 정하지 않는다.

## T03 — 이용내역: API·controller sy-main 병합 완료

- `feature/usage-api-controller`에서 objectName 응답·필수 날짜·검색 enum·정수 계약을 보정했다. 사용자 확정대로 행 필드는 필수·null 허용이다.
- 화면 없는 `usePointUsageController`, `useItemUsageController` 구현 완료. 날짜 기본값 없는 대기, 역전 기간 차단, 검색 기준/검색어 쌍 입력, 제출·초기화·페이지·재시도를 제공한다.
- 구현 공간: `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/usage-api-controller`, 분기 기준 `c6ed8d3`, 구현 커밋 `7ff8247`. 사용자 수동 병합 후 기본 checkout의 `sy-main@987616b`에 포함됨을 확인했다. branch·worktree는 보존했다.
- 검증: 구현 시 formatter·diff 검사 통과. 병합 후 관련 테스트 21/21·lint·build 재실행 통과. 실제 서버 동작은 미검증.
- 다음 작업: 공개 controller 계약을 사용하는 UI 연결. 표시 화면·라우트·메뉴는 아직 결정하지 않았다.

## T04 — 영상·플레이리스트: 계약 충돌 해소 선행

- 기존 `src/entities/video/api/video.dto.ts`에는 사용자 확정 계약으로 등록·수정 file-only가 명시돼 있다. 기존 감사에서 확인한 Swagger data+file 표현과의 충돌을 임의로 덮어쓰지 않는다.
- 다음 작업: 실제 multipart 계약·상세 응답·nullable 의미 및 플레이리스트 입력/순서 범위 확인 후 기존 DTO·전송·parser 보정.
- 현재 이전 감사 이후 해당 도메인 변경은 없다. 세부 차이와 질문은 기존 T04를 참조한다.

## T05 — 문의·문의 타입: Logic 반영, UI 병합 및 응답 확인 남음

- `src/pages/inquiry/hook/use-inquiry-list-controller.tsx`, `use-inquiry-detail-controller.tsx`, `src/pages/inquiry-type/hook/use-inquiry-type-controller.tsx`가 sy-main에 있다.
- 문의 타입 선택은 `useAllInquiryTypesQuery`의 서버 목록으로 연결됐고, 상세 controller에는 답변 등록/수정/삭제·완료·문의 삭제 동작이 있다. 이전 문서의 모든 연결 결정을 “미정”으로 일괄 유지하지 않는다.
- 기본 브랜치의 `src/app/router/routes.tsx`에는 문의 라우트가 아직 없다.
- **별도 구현:** `feature/inquiry-ui@b785adf`, worktree `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/inquiry-ui`. 문의 목록·상세·타입 UI, `/operations/inquiries`, `/operations/inquiries/types`, `/operations/inquiries/:inquiryId`와 메뉴 연결이 커밋돼 있다. `git log sy-main..feature/inquiry-ui`로 미병합을 확인했다. 화면을 새로 중복 작성할 과제가 아니다.
- **잔여 계약:** `src/entities/inquiries/api/inquiry.dto.ts`의 `inquiryMutationResponseSchema = z.string()`과 `inquiry.parser.ts`를 문의·타입 mutation options에서 계속 사용한다. Swagger Void의 실제 payload가 null이면 공통 정규화 후 파싱 실패할 수 있다. 실제 성공 body 확인 전 null 또는 문자열로 계약을 새로 단정하지 않는다.
- 다음 작업: 빈 성공 응답 계약 확인·필요한 보정, 별도 UI 커밋 검토·검증 및 사용자 Git 승인 후 통합. UI 구현 존재와 운영 API 동작 성공은 별개다.

## T06 — 로그인·계정·역할·권한·메뉴: 기반 계약과 신규 연결 남음

- 기존 `/menus`, `/me/menus` API는 있으나 관리 메뉴 children이 로컬 `string[]`이다. 명세의 재귀 객체 배열과 차이가 남아 있다.
- `src/features/auth/use-auth.ts`의 로그인 후 메뉴 연결 TODO가 남아 있다. `/v1/admins/me`는 신규 `/me`와 동일 계약으로 세지 않는다.
- accounts·roles·permissions와 `/me` 등 누락 호출은 기존 T06 범위대로 후속 대상이다. `src/entities`·`src/features/auth`의 검색 및 기준 이후 diff에서 신규 구현을 확인하지 못했다.
- 다음 작업: 로그인 초기화/실패 정책, ID 관계, 서버 메뉴와 route 매핑, 권한 적용 시점 확정 후 기존 auth·menus 자산 확장.

## T07 — 점검 설정: 7개 API·controller 반영 완료

- `src/entities/maintenance/api/maintenance.api.ts`는 `/maintenance`, `/one`, `/version`, `/time`, `/on`, `/off`의 GET 2개·PATCH 5개를 구현한다.
- 기존 `/v1/maintenance` 및 override, configKey/configValue 계약 불일치는 이번 구현으로 교체되었다. config 배열을 한 PATCH로 전송한다.
- [기존 완료 인계](../../maintenance-api/handoff.md)에 기록된 조회 필드 필수/non-null, PATCH data:null, 기존 8개 key 계약을 다시 미정으로 돌리지 않는다.
- `src/pages/maintenance/index.ts`가 목록·단건·변경 controller와 UI 계약을 공개한다. 현재 src 검색에서 실제 화면 소비는 확인되지 않았고 기본 router에도 maintenance 라우트가 없다.
- 다음 작업: 점검 화면이 필요하면 기존 controller를 사용하는 UI 연결 범위를 정해 진행한다. 시간대 변환이나 추가 업무 제약을 자동 추가하지 않는다.
- 이전 완료 기록의 관련 테스트 27개·lint·build 통과는 과거 검증 결과이며 이번 재실행 결과가 아니다.

## T08 — 공지사항·댓글: 응답 매핑과 3개 API 연결 남음

- 명세 목록 `isPinnedCount`와 `src/entities/news/api/news.dto.ts`의 `pinnedItemCount`가 다르다. 기존 parser는 로컬 schema를 그대로 사용한다.
- batch PATCH 및 공지별 댓글 GET/DELETE 3개는 기존 감사의 미연결 과제로 남아 있다. 이후 해당 도메인 변경은 없다.
- 다음 작업: 고정 공지 개수 매핑 보정, 일괄 변경/댓글 관리의 사용 위치·허용 필드·권한·삭제 UX 확정 후 기존 news API·query·controller 확장.

## T09 — 아이템·분류: 필수값·정수 검증 보정 남음

- `src/entities/items/api/items.dto.ts`의 생성 요청은 여러 명세 필수 필드에 null을 허용하며 saleAmount도 일반 number다.
- 명세 CreateItemRequest의 required 목록과 saleAmount integer를 재확인했다. UI의 편집 중 빈 상태와 제출 DTO를 구분하여 검증해야 한다.
- 다음 작업: 기존 `src/pages/item/lib/item-form.model.ts`와 DTO의 제출 검증을 함께 점검·보정. newBadgeUntil·분류 관계·빈 값 처리 등 미확정 업무 규칙은 확인한다.
- 이미 화면에서 사용하는 요청이므로 우선 조사 후보로 권장한다. 현재 시간을 넣거나 임의 기본값을 만드는 방식은 승인된 대안이 아니다.

## T10 — 출석·룰렛: 부분 수정·보상 정수 검증 남음

- `src/entities/event/api/event.dto.ts`의 PATCH는 code/startAt/endAt/isActive를 필수로 요구한다. 명세 optional과 차이가 있다.
- attendance/roulette DTO의 objectAmount, roulette chance는 일반 number다. 명세의 정수·최소값 계약과 맞추는 작업이 남아 있다.
- 기존 items 단독 GET이 화면에서 사용되지 않아도 상세 응답의 items를 사용한다는 기존 감사 판단을 유지한다. 불필요한 추가 조회를 만들지 않는다.
- 다음 작업: DTO·폼 매핑 검증 보정. chance 단위·합계·상한, 생략된 수량의 기본값 등은 확인 후 처리한다.

## T11 — 소포: 발송 검증·응답 필드·화면 연결 남음

- `src/entities/parcels/api/parcel.dto.ts`의 userId/itemId/amount는 일반 number이고 amount 최소값만 검사한다.
- 명세 schema에 있는 목록 amount가 명세 예시와 로컬 DTO에 없는 문제는 실제 반환 계약 확인이 필요하다.
- 다음 작업: 정수 검증, 수신자·아이템 ID 출처, 발송 사유/범위, 목록 amount와 표시 위치 확정. 기존 바이너리 export 처리를 재사용한다.

## T12 — 외부 대시보드: 제품 사용 여부 결정 선행

- 기존 감사의 4개 GET 미구현 상태를 바꾸는 source 변경은 확인되지 않았다.
- 저장된 명세는 외부 공유용·서버 고정 Mock 집계를 설명한다. 실제 운영 통계로 단정하지 않는다.
- 다음 작업: admin-ui 사용 여부·표시 위치·날짜/시간대·공개 호출과 실데이터 제공 계약을 먼저 확인한다.

## T13 — 감사 내역·상태 확인: 제품 사용 여부 결정 선행

- `/admin/audit`, `/health` 신규 호출을 해당 src 검색과 기준 이후 diff에서 확인하지 못했다.
- 다음 작업: 감사로그 화면·조회 권한·페이지/정렬 기준, health의 사용 위치·map 키·인증/호출 주기 필요성을 확정한다. 자동 폴링이나 신규 화면을 임의로 추가하지 않는다.

## 다음 작업 권장 순서

아래는 제안이며 기능 구현·Git 실행 승인이 아니다.

1. **문의 마무리(T05):** 기존 UI 커밋을 활용할 수 있으므로 빈 성공 응답 계약을 확인하고, 통합 검토·검증 후 UI 병합을 진행한다.
2. **현재 화면의 계약 보정(T09 → T08 → T10):** 아이템 필수값/정수, 공지 고정 개수, 이벤트 보상/부분 수정 순으로 검토한다. 신규 기능 확장과 기존 계약 보정을 분리한다.
3. **기존 API의 연결 준비(T02·T03·T11):** 사용자·이용내역·소포 DTO와 ID/업무 계약을 맞춘 뒤 화면에 연결한다.
4. **UI 연결(T07):** 점검 controller는 준비됐으므로 필요한 화면 범위 확정 후 UI 역할로 진행한다.
5. **선행 결정이 큰 기능(T04·T06·T12·T13):** 영상 계약 충돌, 권한/메뉴 정책, 외부 통계·감사/health 사용 범위를 확정한 뒤 구현한다.

## 검증과 제한

- 수행: Git status/log/diff/worktree 조회, 기본 checkout의 API·DTO·parser·controller 읽기, 문의 UI worktree의 상태·라우트 확인, 원본 JSON 규모·주요 schema 대조, 작성 문서의 로컬 링크·작업 번호 검사.
- 미수행: 앱 소스 변경, 최신 원격 OpenAPI 수집, 업무 API 호출, 앱 테스트·lint·build, 브라우저 검증, commit·merge·push.
- 이번 문서는 저장된 명세 대비 개발 진행을 갱신한다. 서버 API 명세 자체가 최근 변경됐다는 뜻은 아니다.
