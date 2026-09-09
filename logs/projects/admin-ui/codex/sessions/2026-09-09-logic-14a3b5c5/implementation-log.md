# 구현 기록

news 목록·폼 controller와 페이지 export를 구현했다. 관련 테스트 46개와 프로젝트 빌드는 통과했다. tsconfig.app.json을 사용한 별도 타입 검사와 전체 린트에는 기존 범위 밖 오류가 남아 있다.

## 승인·위치

- assignment `14a3b5c529a94f6d8c36fb91cfee693d`, host `codex`, role `logic`, 책임 `owner`.
- worktree: `/private/tmp/asan-metaverse-admin-ui-news-management-logic-14a3b5c5`.
- branch `task/news-management-logic`, parent·직접 target `task/news-management-ui`.
- 기준 HEAD `49aa7392882479dcb6fb08eacd73fc432d2af726`.
- 계약 SHA `5567cf5221dea8465566ce8d04c7355d61aa3beb29b27ea78af30f8fba90a79f`.
- 사용자 `proceed` 후 전체 scope의 구현 승인·탐색 조건을 확인했다. 승인된 plan은 수정하지 않았다.

## 변경

| 경로 | 내용·목적 |
| --- | --- |
| `src/pages/cp-news/lib/cp-news-list.model.ts` | 검색·URL 매핑, 페이지·복귀 경로 정규화 |
| `src/pages/cp-news/hook/use-cp-news-list-controller.ts` | 입력과 적용 검색 분리, query 소비, 서버 집계·오류·이동 callback |
| `src/pages/cp-news/lib/cp-news-form.model.ts` | ID·필수값 검증, POST·PATCH 매핑, 미입력·false 구분 |
| `src/pages/cp-news/lib/cp-news-form-request.ts` | 저장·삭제 경합 및 종료된 화면의 callback 차단 |
| `src/pages/cp-news/hook/use-cp-news-form-controller.ts` | 상세·draft·mutation·오류·삭제 확인 상태 연결 |
| `src/pages/cp-news/ui/cp-news-list-page.tsx` | 목록 controller와 기존 View 조합 |
| `src/pages/cp-news/ui/cp-news-form-page.tsx` | 생성·수정 진입점과 ID별 편집 생명주기 분리 |
| `src/pages/cp-news/index.ts` | 목록·생성·수정 페이지 export |
| `tests/news-list-controller.test.mjs` | 검색·상태·집계·페이지 보정 테스트 7개 |
| `tests/news-form-controller.test.mjs` | payload·상태·실패·경합·생명주기 테스트 11개 |

## 선택과 재사용

공개 news query·mutation·DTO·MSW와 기존 View·controller 타입을 재사용했다. API 계층이 담당하는 캐시 취소·무효화·삭제 상세 제거를 중복 구현하지 않는다. 서버 items 순서와 집계 값을 다시 계산하지 않는다.

입력 draft와 적용 URL query를 분리하고 적용·초기화 시 1페이지로 이동한다. 목록 복귀 목적지는 `/cp/news`로 고정하며 허용된 검색·페이지 query만 보존한다. 상세 재조회 위에 편집한 필드만 덮어 입력을 유지하고 PATCH는 실제 달라진 필드·상태만 전송한다. void 성공 뒤 목록으로 돌아가며 새 ID를 가정하지 않는다.

공용 store·추상 controller 대신 page-local model·hook으로 나눴다. 저장·삭제 두 흐름의 동일한 잠금·생명주기 규칙만 helper로 추출했다. 새 패키지·테스트 프레임워크는 없다.

## 검증

| 명령 | 결과 |
| --- | --- |
| `npm ci --offline --ignore-scripts --no-audit --no-fund` | exit 0, 341개 설치 |
| `node --test tests/news-contract.test.mjs tests/news-form.test.mjs tests/news-msw.test.mjs tests/news-mutation.test.mjs tests/news-list-controller.test.mjs tests/news-form-controller.test.mjs` | 최종 exit 0, 46/46 통과, 신규 18개 포함 |
| `npx eslint src/pages/cp-news --ext .ts,.tsx` | exit 0 |
| `npx tsc --noEmit -p tsconfig.app.json` | 기존 범위 밖 오류 14개로 실패; cp-news 오류 없음 |
| `npm run lint` | exit 1, 기존 오류 68개·경고 5개; cp-news 오류 없음 |
| `git diff --check` | exit 0 |
| `npm run build` | 사용자 `명령 실행 승인` 후 동일 worktree에서 1회 실행, exit 0; tsc -b 및 Vite 빌드 성공 |

최초 테스트는 44/46이었다. SSR 오류 snapshot에서 mount 자동 재조회가 확정 오류를 loading으로 바꿨다. 테스트 QueryClient의 retryOnMount를 false로 설정해 확정 상태를 관찰하도록 수정했다. 기존 기대값·제품 동작·기존 테스트는 완화하지 않았다.

타입 오류는 dao table-rows, event attendance·roulette DTO, select-users, dialog store, reason-prompt-host에 있다. 모두 미변경 파일이며 UI handoff의 기존 오류 14개와 일치한다. 전체 린트도 기존 68개 오류·5개 경고와 일치한다.

## 제한과 다음 단계

사용자 요청과 staging·commit 각각의 명령 승인 후 `6f1d322c5e14802a0d7504d9d83890bfda215b92` 커밋을 생성했다. 메시지는 `feat : 공지사항 목록과 폼 controller 구현`이다. 소스·테스트 10개·738줄 추가를 포함하며 커밋 전 cached diff 검사와 커밋 후 HEAD·경로·clean 상태를 확인했다. Git 변경 명령에는 git -C로 자식 worktree를 명시해 부모 소유권 오판을 해소했다. 정책상 명령 승인 차단은 사용자 승인으로 해결했고 병합은 실행하지 않았다.

빌드는 tsconfig.json을 사용하며 별도 tsconfig.app.json의 noUnusedLocals·noUnusedParameters·erasableSyntaxOnly 검사와 설정이 다르다. 두 타입 검증 결과를 혼동하지 않는다. Vite는 tsconfig paths 플러그인의 내장 기능 전환 안내와 500 kB 초과 청크 경고를 출력했으나 빌드는 성공했다. 설정·패키지는 변경하지 않았다.

독립 Watcher·merge는 미수행이다. 실제 DOM·브라우저 이동·실 API·시각 QA는 확인하지 않았다. 라우트·메뉴·브라우저 MSW 등록은 UI 후속이며 현재 코드만으로 브라우저 진입점이 완성되지는 않는다.
