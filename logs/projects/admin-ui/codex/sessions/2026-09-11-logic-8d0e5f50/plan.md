# 계획

## 목표

UI 인계 문서 `.claude/logs/sessions/2026-09-10-ui-d44e64a8/handoff.md`의 Logic 작업 1~5를 구현한다. 브라우저 MSW에 기존 news handler를 등록하고 controller의 화면 이동을 주입된 callback으로 분리한다.

## 작업 유형

- hybrid: 기존 mock 등록과 controller 이동 책임 분리.
- 작업 위치: `task/news-management-ui`, `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`.
- 시작 HEAD: `7c5f91cf14e925c27b671c9d205939d42d631395`, 시작 시 미커밋 변경 없음.

## 범위와 수행 순서

| 작업 구간 | 역할 | 스킬 | 수행 방법·목적·기대 결과 |
| --- | --- | --- | --- |
| `src/mocks/handlers.ts` | Logic | data-fetch-layer, implementation-quality | 기존 `createNewsHandlers()`를 등록해 전체 handler 배열에서도 news CRUD가 처리되게 한다. |
| `src/pages/cp-news/hook/*` | Logic | coding-convention, type-definition | 목록 열기와 폼 닫기 callback을 주입받고 URL 이동 책임을 페이지로 옮긴다. |
| `src/pages/cp-news/ui/*-page.tsx` | Logic의 기능 연결 | coding-convention | 새 hook 인자를 연결하고 UI 후속 작업 전까지 현재 경로와 검색 query를 유지한다. |
| `tests/news-list-controller.test.mjs`, `tests/news-form-controller.test.mjs`, `tests/news-msw.test.mjs` | Logic | implementation-quality | callback·ID 방어·전체 handler CRUD를 확인하고 기존 경합·늦은 응답 검증을 유지한다. |
| 현재 세션 산출물 | Logic | documentation | 승인 결정, 변경·검증 결과와 다음 UI 작업의 연결 계약을 기록한다. |

## 제외 사항과 제약 조건

- 화면 state 조합, 라우트·barrel 정리는 후속 UI 책임이다.
- View와 `model/*.types.ts` 공개 controller 타입, API·DTO, mock 초기 데이터와 in-memory 동작을 유지한다.
- 검색·페이지 query, `Number.isSafeInteger`, 요청 guard, mutation 캐시 무효화는 기존 구현을 재사용한다.
- 임시 페이지가 `newsListPath`를 사용하므로 삭제하지 않는다.
- 패키지·환경 파일 변경, Git 변경, 시각 QA는 이 작업에 포함하지 않는다.

## 스킬 및 역할

- 확인된 역할: inject `logic`. 사용자도 Logic 인계 작업을 요청했다.
- 적용 스킬: task-role-routing 및 logic·handoff·pipeline 참조, git-branch-strategy, skill-index, coding-convention, data-fetch-layer, implementation-quality, type-definition, documentation.
- 새 branch/worktree 없이 기존 공간에서 Logic → UI 순차 연결한다.
- 승인된 Git 작업: 없음.
- 산출물 책임: 현재 assignment의 `owner`. UI 인계를 위해 `handoff.md`도 작성한다.

## 검증

- 변경된 세 테스트 파일을 `node --test --test-concurrency=1`로 실행한다.
- `npm run lint`, `npx --no-install tsc --noEmit -p tsconfig.app.json`, `npm run build`, 전체 `node --test --test-concurrency=1 --test-reporter=spec`, `git diff --check`를 확인한다.
- worker 시작 코드와 개발 환경의 `VITE_ENVIRONMENT` 값만 읽어 활성 조건을 확인한다.

## 위험 요소 및 확정된 결정

- 기존 저장·삭제 성공은 이력을 교체하지만 목록 버튼은 이력을 추가했다. 인자 없는 `onClose()`로 합치는 동안 세 동작 모두 `replace: true`로 통일하는 차이를 설명하고 사용자 승인을 받았다.
- 공통 handler 배열을 실제 요청으로 검증해 기존 handler가 news 경로를 가로채지 않는지 확인한다.
- 브라우저 실행·사용자 화면 조작은 이번 자동 검증 범위에 포함하지 않는다.

## 승인

- 상태: approved.
- 사용자 응답: “그렇게 진행하고 작업 진행해”. 임시 이력 처리 통일과 보고한 Logic 구현 범위의 진행 승인이다.
- 이 문서는 승인된 계획과 실제 수행 구간을 작업 종료 시 기록한 것이다.
