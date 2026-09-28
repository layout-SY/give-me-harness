# 탐색

## 요청

news handoff 파악 후 controller 구현 진행. 기존 UI 커밋을 기준으로 승인된 격리 worktree를 생성했다.

## 조사 대상 경로

- `.claude/logs/sessions/2026-09-09-ui-f14c4487/handoff.md` 및 기존 news Logic handoff.
- `src/pages/cp-news`의 View·타입·표기 config·barrel 8개.
- `src/entities/news/api/`, `hook/`, `model/news-query-options.ts`, `model/news-mutation-options.ts`.
- `src/pages/cp-board/hook/`, `lib/cp-notice-form.model.ts`, `ui/cp-notice-form-page.tsx`.
- `src/shared/ui/table/table.tsx`, 현재 라우트·활성 navigation·MSW registry.
- `tests/news-*.test.mjs`, `package.json`, `tsconfig.app.json`, `vite.config.ts`, `eslint.config.js`.

## 현재 코드와 인접 구현의 사실

- news 전송·DTO·parser·query/mutation은 구현돼 있다. 새 API 계층을 만들 필요가 없다.
- 상세 query는 ID schema 검증 실패 시 disabled이지만 UI 오류 상태까지 제공하지는 않는다.
- 목록 응답의 `items`, `totalElements`, `totalPages`, `pinnedItemCount`는 독립적인 서버 값이다.
- 현재 cp-news View는 controller callback만 호출한다. form은 저장 중 입력·뒤로가기 등을 잠그고, 삭제 popup은 진행 여부와 오류를 별도로 표시한다.
- 기존 cp-board는 동일한 controller/View 구조지만 작성자·노출 기간·메인 노출·fixture ID 등 news에 없는 개념이 있어 전체 복사하지 않는다.
- Table은 page·pageCount를 직접 받을 수 있다. 서버 pagination을 별도 adapter로 재계산할 필요가 없다.
- 목록 등록·수정 열기, 폼 뒤로가기·mutation 이후 목록 복귀가 미연결이다.
- `src/mocks/handlers.ts`에는 news handler가 등록돼 있지 않다. 테스트는 `createNewsHandlers`를 명시 등록한다.
- 현재 라우트·활성 메뉴에 `/cp/news`가 없다. 이 경로 연결은 UI 후속 소유다.
- 프로젝트에 test script는 없고 Node 내장 test와 Vite SSR load, MSW·QueryClient를 사용한다.

## 불러온 스킬

task-role-routing 및 Logic·handoff·pipeline references, git-branch-strategy, skill-index, documentation, coding-convention, type-definition, implementation-quality, data-fetch-layer, recipe-data-fetch, recipe-data-dto, validation.

## 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| 공개 news query·mutation hook | 재사용 | DTO 검증·캐시 취소·무효화·삭제 상세 제거까지 기존 계약에 포함 |
| CpNewsListView·CpNewsFormView·CpNewsDeletePopup | 재사용 | 신규 controller의 정확한 props/callback 계약이 존재 |
| Table·폼 공용 UI | View를 통해 재사용 | 목록·입력·페이지네이션 표현은 이미 구현 |
| 기존 news MSW와 Node/Vite 테스트 | 재사용 | 실제 요청·응답과 QueryClient 동작 검증 가능 |

## 재사용하지 않은 후보와 이유

- cp-board 전체 controller: DTO·KPI·기존 ID와 UI 동작이 달라 news와 혼합하면 잘못된 계약을 가져온다.
- 일반 fetch adapter: 이미 news query hook과 서버 집계를 직접 소비할 수 있다.
- 공용 상태 store·새 테스트 프레임워크: 해당 페이지의 상태 분리에 필요하지 않다.

## 성능·의존성 영향

입력 변경마다 query를 호출하지 않고 적용된 검색·페이지로만 조회한다. 기존 QueryClient 캐시를 사용한다. 새 런타임 의존성은 추가하지 않는다. 격리 worktree의 `node_modules`는 없으므로 검증 전 기존 lockfile의 의존성 설치가 필요하다.

## 제약 조건 및 미확인 사항

- 실 API의 고정 공지 집계 관례를 MSW 구현으로 단정하지 않는다.
- 브라우저 MSW 등록과 기존 공지 수정 URL 처리 방침은 후속 결정 사항이다.
- 읽기·브랜치 생성만 실행했으며 새 source 구현·타입·lint·테스트 실행 결과는 없다.
- 원래 worktree 소유권 때문에 동일 위치의 create는 차단됐다. 새 격리 계약의 create는 성공했다.
- 현재 harness 기록은 스킬·탐색 true, 구현 승인 false다. 원래 scope에는 없던 테스트 경로 2개가 포함된 전체 scope에 구현 승인이 필요하다.

## 결론

새 page hook과 순수 요청·상태 model, 최소 page entry만으로 기존 API·View를 연결할 수 있다. source 변경 전 현재 전체 scope의 구현 gate가 충족돼야 한다.
