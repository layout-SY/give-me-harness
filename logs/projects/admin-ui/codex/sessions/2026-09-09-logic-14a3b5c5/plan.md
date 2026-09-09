# 계획

## 목표

UI 커밋 `49aa7392882479dcb6fb08eacd73fc432d2af726`의 `CpNewsListController`·`CpNewsFormController` 계약을 구현하여 news 목록·등록·수정·임시 저장·게시·삭제를 동작하게 한다. 공개 news hook과 기존 View를 재사용한다.

## 작업 유형

- feature: 기존 API·UI 사이의 페이지 상태·요청 매핑·기능 연결.

## 범위

- 작업 위치: `/private/tmp/asan-metaverse-admin-ui-news-management-logic-14a3b5c5`.
- branch: `task/news-management-logic`, V3·ACTIVE.
- parent·직접 merge target: `task/news-management-ui`.
- 분기 SHA: `49aa7392882479dcb6fb08eacd73fc432d2af726`.
- 계약 SHA-256: `5567cf5221dea8465566ce8d04c7355d61aa3beb29b27ea78af30f8fba90a79f`.
- 승인 scope: `src/pages/cp-news`, `tests/news-list-controller.test.mjs`, `tests/news-form-controller.test.mjs`.
- 예상 diff: 신규 페이지 소유 hook·lib·페이지 entry와 위 테스트 2개, `src/pages/cp-news/index.ts`의 페이지 export. 기존 View·표기 config·controller 타입은 기능상 필요가 입증되지 않으면 수정하지 않는다.

## 제외 사항

라우트·메뉴 연결, 기존 `/cp/boards/notices/:noticeId/edit`의 redirect·제거, 브라우저 MSW registry 변경, API 전송 모듈·공용 UI 변경, 패키지 추가와 관련 없는 lint 오류 수정은 이번 범위에 포함하지 않는다. UI 후속의 파일 소유권을 유지한다.

## 제약 조건

- 목록 필터·검색 입력과 실제 적용 query를 분리한다. 적용·초기화 시 1페이지로 이동한다.
- 빈 검색은 `by`·`keyword` 모두 생략하고, 검색어가 있으면 trim한 값과 검색 범위를 함께 전송한다.
- 서버 items 순서·집계·totalPages를 그대로 보존한다. 마지막 항목 삭제 등으로 현재 페이지가 응답의 범위를 벗어나면 유효 페이지로 복귀한다.
- 등록 payload의 5개 필드를 모두 매핑한다. PATCH는 미입력을 임의 기본값으로 덮지 않고 `isPinned: false`를 보존한다.
- 제목·본문의 공백만 있는 값은 임시 저장·게시 모두 막는다. 저장 직전에도 검증한다.
- 등록 응답 `void`를 성공으로 처리하고 목록으로 복귀한다. 기존 mutation options의 캐시 처리를 중복 구현하지 않는다.
- 수정·삭제 중 중복 요청과 경합을 막고, 실패 시 입력·삭제 확인 상태를 보존한다. 상세 ID 변경·unmount 후 이전 요청의 페이지 이동·오류 반영을 막는다.
- 조회 실패·잘못된 ID·빈 결과를 구분한다. disabled 상세 query를 loading으로 잘못 표시하지 않는다.
- 전체 보관 동작은 추가하지 않으며 `ARCHIVED` 상세는 실제 상태를 표시한다.

## 스킬 및 역할

- 확인된 역할: inject `logic`.
- 근거: API 소비·폼 DTO 매핑·hook·페이지 조합과 동작 테스트.
- 사용자 역할 확인: controller 구현 범위 보고 후 “작업 진행”. 이후 두 번의 branch 계약 “승인”은 각각의 SHA에 적용됨.
- Git 통합 담당자: 자식 task와 격리 worktree는 `codex`. 부모 UI task와 기본 worktree는 기존 Claude 담당.
- 산출물 책임: `owner`.
- 적용 스킬: task-role-routing, git-branch-strategy, coding-convention, type-definition, implementation-quality, data-fetch-layer, recipe-data-fetch, recipe-data-dto, validation, documentation. 폼 검증은 순수 함수, 부수 효과는 전용 hook 경계에 둔다.

| 작업 구간 | 위치·방법·목적 | 기대 결과 |
| --- | --- | --- |
| 목록 | `lib/`에서 query 매핑·페이지 보정, `hook/`에서 입력·query 상태와 조회·이동 조합 | 검색 적용·초기화·페이지 이동·오류 재시도가 controller 계약으로 동작 |
| 폼 | `lib/`에서 ID·필수값·POST/PATCH 매핑, `hook/`에서 상세·draft·mutation과 요청 보호 조합 | 등록·수정·임시 저장·게시·삭제 성공/실패가 View에 정확히 전달 |
| 페이지 조합 | `ui/`에 최소 page entry를 추가하고 barrel export | UI 후속이 준비된 페이지를 라우트에 연결 가능 |
| 검증 | 승인된 Node 테스트 2개와 기존 news 테스트, 대상 lint·타입 검사 | 요청 경계와 사용자 동작이 실행 근거로 확인됨 |

## 검증

1. 격리 worktree에 기존 lockfile의 의존성을 설치한다. 현재 `node_modules`는 없다. 패키지 정의를 변경하지 않는다.
2. 기존 Node/Vite 테스트 배치로 검색 쌍·첫 페이지·false PATCH·void 생성·잘못된 ID·실패 유지·페이지 보정을 검증한다. 가능한 동작은 기존 MSW와 QueryClient를 연결해 검증한다. 테스트 전용 프레임워크·과도한 harness를 추가하지 않는다.
3. `node --test tests/news-contract.test.mjs tests/news-form.test.mjs tests/news-msw.test.mjs tests/news-mutation.test.mjs tests/news-list-controller.test.mjs tests/news-form-controller.test.mjs`.
4. `npx eslint src/pages/cp-news --ext .ts,.tsx`, `npx tsc --noEmit -p tsconfig.app.json`, 승인된 정확한 명령으로 `npm run lint`, `npm run build`.
5. `git diff --check`와 변경 scope 확인. 기존 오류와 새 변경 오류를 분리해 기록한다.
6. Watcher 계약에 따른 변경 검토, 평가·owner 산출물 작성. 브라우저 캡처·시각 QA와 실서버 호출은 실행하지 않는다.

## 위험 요소 및 결정 사항

- 모든 기능을 하나의 controller에 넣는 최소안은 요청 보호·매핑 검증이 섞인다. 공용 store·추상 controller로 확장하는 안은 이 화면에 필요하지 않은 계약을 늘린다. 페이지 소유의 소규모 hook·순수 model 분리를 선택한다.
- 조회와 편집 상태는 분리해 상세 재조회가 사용자의 미저장 입력을 덮지 않게 한다.
- 목록에서 폼으로 이동한 뒤 돌아올 검색·페이지 상태는 페이지의 URL query로 보존하는 방법을 사용한다. 외부 URL을 복귀 대상으로 허용하지 않는다.
- 임시 저장·게시·삭제 성공은 `/cp/news`의 목록으로 복귀한다. 목록은 서버 응답을 기준으로 현재 페이지를 보정한다.
- 현 UI는 `fields.isSaving`으로 폼 입력과 이동을 잠그므로 삭제 진행도 폼의 busy 상태에 포함해 저장·삭제 경합을 방지한다.
- 라우트 연결은 UI 후속이므로 이 Logic 작업만으로 브라우저 진입점이 완성됐다고 보고하지 않는다.

## 승인

- 사용자 구현 의사: 확인됨 — 앞선 “작업 진행”. 구현 범위는 그때 보고한 controller·페이지 조합·동작 검증을 유지한다.
- branch SHA: 위 격리 계약 승인 후 `create` exit 0.
- 현재 기계 상태: `skill_confirmed: true`, `exploration_completed: true`, `ui_exploration_completed: true`, `implementation_approved: false`.
- 원인: 원래 구현 scope 기록은 `src/pages/cp-news`였고 자식 계약에는 테스트 경로 2개가 추가되었다. 현재 전체 scope의 구현 승인이 아직 기록되지 않았다. branch SHA 승인을 구현 승인으로 복사하지 않는다.
- 상태: 현재 전체 scope의 구현 승인 대기. 사용자에게 `Proceed`로 구현 gate 등록을 요청한다. source 변경·테스트·의존성 설치는 아직 실행하지 않았다.
- 필수 문구: `이 역할과 계획대로 진행할까요, 아니면 조정할 부분이 있나요?`
