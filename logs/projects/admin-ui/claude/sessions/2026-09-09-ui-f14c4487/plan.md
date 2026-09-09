# 계획

## 목표

공지사항(news) 전용 관리 화면의 UI 표현 계층과 Logic 인계용 controller props/callback 계약을 신설한다. `/admin/news` API·hook은 이미 구현되어 있으나 전용 화면이 없어 목록·등록·수정·삭제를 수행할 수 없다.

## 작업 유형

- feature

## 범위

- `src/pages/cp-news/model/cp-news-list.config.ts` — 한국어 표기 상수, 필터 항목, 테이블 컬럼
- `src/pages/cp-news/model/cp-news-list.types.ts` — `CpNewsListController` 계약
- `src/pages/cp-news/ui/cp-news-list-view.tsx` — 목록 View
- `src/pages/cp-news/model/cp-news-form.config.ts` — 유형·상단고정 칩 옵션과 화면 문구
- `src/pages/cp-news/model/cp-news-form.types.ts` — `CpNewsFormController` 계약
- `src/pages/cp-news/ui/cp-news-form-view.tsx` — 등록·수정 공용 View
- `src/pages/cp-news/ui/cp-news-delete-popup.tsx` — 삭제 확인 팝업
- `src/pages/cp-news/index.ts` — barrel export

## 제외 사항

- `src/app/router/routes.tsx`, `src/widgets/side-navigation/model/_navigation5.ts` 연결 — controller가 없어 페이지 컴포넌트를 구성할 수 없다. Logic 통합 후 별도 승인으로 수행한다.
- 기존 `/cp/boards/notices/:noticeId/edit`의 정리·redirect — 기존 진입점 동작 보존이 원칙이라 Logic 통합 후 결정한다.
- 노출 기간, 메인 노출, 작성자 검색 — news 요청 계약에 없어 이식하지 않는다.
- API 호출, 페이지 상태, 요청 DTO 매핑, 캐시·이동 처리 — Logic 역할.

## 제약 조건

- `entities/news`의 label 상수는 번역 키(`_news_*`)라서 화면 표기는 페이지 config에 둔다.
- 목록 응답의 `totalElements`, `totalPages`, `pinnedItemCount`와 항목 순서는 서버 값을 보존하며 View에서 재계산하지 않는다.
- `by`와 `keyword`는 함께 전송해야 하므로 검색 범위 선택에는 "전체" 항목을 두지 않는다.
- 상세 진입 ID는 숫자 newsId다.
- 외부 UI 의존성과 새 디자인 토큰을 추가하지 않는다.

## 스킬 및 역할

- 제안 역할: ui
- 역할 판단 근거: 화면 구조·표현·접근성·props/callback 계약은 UI 책임이며, 검색·페이지 상태·요청 매핑은 Logic 책임이다.
- 사용자 역할 확인: inject `--role ui`. 사용자가 계획 보고 후 `진행해`로 구현을 승인했다.
- Git 통합 담당자: claude
- 산출물 책임: owner

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| handoff·정책·재사용 자산 조사 | ui | task-role-routing, git-branch-strategy | 인계 계약과 공용 UI 재사용 판단 |
| 목록 config·계약·View | ui | coding-convention, styles, abstraction-strategy | 필터·테이블 표현과 controller 계약 |
| 폼 config·계약·View·삭제 팝업 | ui | coding-convention, styles, ui-library | 등록·수정 공용 화면과 삭제 확인 |
| 타입·lint·회귀 검증 | ui | implementation-quality | 신규 파일 무오류, 기존 news 테스트 유지 |
| 산출물 작성 | ui | documentation, portfolio | owner 8종과 Logic 인계 문서 |

## 검증

- `npx tsc --noEmit -p tsconfig.app.json`
- `npx eslint src/pages/cp-news`
- `node --test tests/news-contract.test.mjs tests/news-form.test.mjs tests/news-msw.test.mjs tests/news-mutation.test.mjs`
- 시각 QA·브라우저 캡처는 사용자가 요청하지 않아 수행하지 않는다.

## 위험 요소 및 결정 사항

- `ToggleSwitch`는 접근 가능한 이름을 받을 수 없고 shared 수정은 이번 scope 밖이므로, 상단고정은 `ariaLabel`을 지원하는 `ChoiceChipGroup`으로 표현한다.
- `Dropdown`은 index 계약이라 값 기반 controller 계약과 View에서 상호 변환한다. 해제(-1)는 "전체"로 되돌린다.
- 고정 항목이 서버 집계·페이지 크기에 포함되는 방식은 확정되지 않아 View에서 재정렬·재계산하지 않는다.

## 승인

- 상태: approved
- 사용자 승인: 계획 보고 후 `진행해`, branch proposal SHA `0aa18eee3ae6503590c79bfa855822f76df4e5ebac7d6221093038e9d70b9775`에 대해 `승인`
- 필수 문구: `이 역할과 계획대로 진행할까요, 아니면 조정할 부분이 있나요?`
