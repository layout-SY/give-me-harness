# 구현 로그

## 승인된 범위

- branch: `task/news-management-ui` (V3, parent·merge target `sy-main` @ `5834f920fcce`, 역할 `ui`, Git 통합 담당자 `claude`)
- proposal SHA-256: `0aa18eee3ae6503590c79bfa855822f76df4e5ebac7d6221093038e9d70b9775`
- 승인된 작업 경로: `src/pages/cp-news`

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `src/pages/cp-news/model/cp-news-list.config.ts` | 신규. 유형·상태·검색 범위 한국어 표기, 상태 배지 색/톤, 필터 항목, 테이블 컬럼 7개 | 번역 키 노출 없이 목록 표기 확보 |
| `src/pages/cp-news/model/cp-news-list.types.ts` | 신규. `CpNewsListController`(search·table·error)와 하위 계약 | Logic이 구현할 목록 controller 인터페이스 확정 |
| `src/pages/cp-news/ui/cp-news-list-view.tsx` | 신규. `PageHeader` + `FilterBar` + `SectionCard`/`Table` 목록 화면 | 필터·검색·페이지·등록/수정 진입·조회 오류 표현 |
| `src/pages/cp-news/model/cp-news-form.config.ts` | 신규. 유형 칩 옵션, 상단고정 칩 옵션, 화면 문구, 본문 행 수 | 등록·수정 공용 표기 확보 |
| `src/pages/cp-news/model/cp-news-form.types.ts` | 신규. `CpNewsFormController`(fields·delete·load)와 mode | 등록·수정·삭제 controller 인터페이스 확정 |
| `src/pages/cp-news/ui/cp-news-form-view.tsx` | 신규. 등록·수정 공용 폼 화면 | 제목·본문·유형·상단고정 입력과 임시 저장·게시·삭제 액션 |
| `src/pages/cp-news/ui/cp-news-delete-popup.tsx` | 신규. `Popup` 기반 삭제 확인 | 대상 ID·제목 확인, 처리 중·실패 표현 |
| `src/pages/cp-news/index.ts` | 신규. View·controller 타입·표기 상수 barrel | Logic이 계약을 단일 진입점에서 가져온다 |

## 재사용한 자산과 새로 만든 자산

재사용: `PageHeader`, `FilterBar`, `ActionBar`, `Table`, `Dropdown`, `TextInput`, `TextArea`, `ChoiceChipGroup`, `SectionCard`, `DefinitionList`, `Popup`, `Button`, `Loading`, `_cp-admin.css` 토큰.

새로 만든 것: `src/pages/cp-news` 하위 페이지 전용 파일 8개. 공용 UI 승격이나 새 CSS 파일, 새 의존성은 없다.

## 핵심 로직·요청 처리

View는 API를 호출하지 않는다. 표현과 이벤트 전달만 담당하며 다음 경계를 지켰다.

- 목록 집계(`itemCount`, `pageCount`, `pinnedItemCount`)는 controller가 전달한 서버 값을 그대로 표시하고 재계산·재정렬하지 않는다.
- 조회 실패는 `error.isVisible`로 표를 대체해 표시하고, 빈 목록과 구분한다.
- 폼은 `canSaveDraft`/`canPublish`/`isSaving`으로만 버튼을 제어하고 검증·요청 매핑은 controller에 남겼다.
- 저장 실패(`saveErrorMessage`)와 상세 조회 실패(`load.isFailed`), 삭제 실패(`delete.errorMessage`)를 각각 다른 자리에 표시한다.
- 수정 진입은 `table.onOpenEdit(row.id)`로 숫자 newsId만 전달한다.

## 결정 사항

1. 상단고정은 `ToggleSwitch` 대신 `ChoiceChipGroup`으로 표현했다. `ToggleSwitch`는 접근 가능한 이름을 받을 수 없고, shared 수정은 승인된 scope 밖이다.
2. `Dropdown`이 index 계약이라 controller 계약은 값 기반으로 두고 View에서 index를 변환했다. 해제(-1)는 유형·상태에서 "전체"로, 검색 범위에서는 기존 값 유지로 매핑했다.
3. 검색 범위 드롭다운에는 "전체"를 넣지 않았다. `by`와 `keyword`가 한 쌍이어야 하기 때문이다.
4. KPI 스트립을 넣지 않았다. 목록 API가 상태별 전체 집계를 제공하지 않아 현재 페이지 행으로 만든 수치는 사실과 다르다.
5. 삭제 팝업은 공용 feature로 만들지 않고 페이지 로컬 컴포넌트로 두었다. 사용처가 하나다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `npx tsc --noEmit -p tsconfig.app.json` | `src/pages/cp-news` 오류 0건. 기존 파일 14건 오류는 이번 변경 전부터 존재 |
| `npx eslint src/pages/cp-news --ext .ts,.tsx` | PASS (출력 없음) |
| `node --test tests/news-*.test.mjs` | 28/28 PASS |

## 알려진 위험과 제한

- controller가 없어 화면을 실제로 렌더해 확인하지 못했다. 브라우저 동작·시각 QA는 수행하지 않았다.
- 라우트·메뉴에 연결되지 않아 현재 사용자 접근 경로가 없다.
- 기존 `/cp/boards/notices/:noticeId/edit`와 진입점이 중복될 수 있으며 정리 방침은 미정이다.
- `npm run build`는 사용자 명령 승인 절차가 필요해 실행하지 않았고, 타입 검증은 `tsc --noEmit`으로 대체했다.
- 프로젝트 전체 lint의 기존 오류(직전 기록 68 errors / 5 warnings)는 이번 변경과 무관하게 남아 있다.

## 다음 담당자 인계

Logic 담당이 `~/pages/cp-news`의 `CpNewsListController`, `CpNewsFormController`를 구현하고 `~/entities/news`의 공개 hook과 연결한다. 세부 계약은 `handoff.md`에 정리했다.
