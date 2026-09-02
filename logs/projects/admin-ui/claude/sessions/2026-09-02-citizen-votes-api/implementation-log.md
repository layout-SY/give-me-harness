# 구현 로그

## 승인된 범위

- 브랜치: `task/connect-citizen-votes-api`
- 분기 기준·직접 merge 대상: `sy-main`
- 승인 parent HEAD: `e26b263afe2478cbabd3e34fdc82306e0715d059`
- 작업 목적: 시민투표 목록·상세를 실제 `GET /citizen/votes`, `GET /citizen/votes/{voteId}` 계약에 조회 전용으로 연결한다.
- 승인 경로: `src/entities/cp-vote/**`, `src/pages/cp-vote/**`, `src/mocks/cp-vote.handlers.ts`, 시민투표 계약·MSW 테스트, `tests/cp-date-input-boundaries.test.mjs`, `package.json`, `package-lock.json`, 현재 세션 로그 디렉터리.
- `yarn.lock`은 다른 활성 세션이 만든 미소유 동시 변경으로 판정됐으며 이 작업의 수정·검토·stage·commit 대상에서 제외한다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `src/entities/cp-vote/api/cp-vote.api.ts` | 목록·상세 resource를 `/citizen/votes`로 교체하고 반복 `sort` 직렬화와 `AbortSignal` 전달을 적용 | 실제 GET 계약만 호출한다. |
| `src/entities/cp-vote/api/cp-vote.dto.ts` | page·size·sort, 양의 정수 ID, 5개 상태, 목록·상세 응답과 집계 불변식을 Zod로 정의 | 외부 입력·응답이 runtime 경계에서 검증된다. |
| `src/entities/cp-vote/api/cp-vote.parser.ts` | 목록 응답을 보존하면서 `pageCount`를 계산하고 상세 응답을 검증 | backend에 없는 필드를 생성하지 않는 read model이 만들어진다. |
| `src/entities/cp-vote/hook/**`, `model/**`, `index.ts` | 실제 query key와 ID 활성화 조건을 적용하고 legacy mutation export·hook을 제거 | TanStack Query가 실제 요청 의존값과 취소 signal을 반영한다. |
| `src/pages/cp-vote/hook/**`, `model/**`, `lib/**` | 지원되지 않는 검색·mutation process를 제거하고 page/sort 기반 조회 controller로 재구성 | 목록 선택·pagination·retry·상세 이동만 남은 조회 orchestration이 된다. |
| `src/pages/cp-vote/ui/cp-vote-list-view.tsx` | Claude Code가 검색·필터·상태 처리 UI를 제거하고 실제 목록 필드만 표시 | read-only 목록과 기존 Table·Loading·retry 동작이 유지된다. |
| `src/pages/cp-vote/ui/cp-vote-detail-view.tsx` | Claude Code가 mutation·placeholder 섹션을 제거하고 실제 상세·집계 필드를 표시 | read-only 상세와 목록 이동·retry·RatioBar가 유지된다. |
| `src/mocks/cp-vote.handlers.ts` | 실제 endpoint, pagination, 다중 sort, size 제한, 400·401·404 envelope를 구현 | Node 테스트가 observable HTTP 계약을 직접 검증할 수 있다. |
| `tests/citizen-votes-contract.test.mjs` | DTO·parser·API URL·serializer 계약 7개를 추가 | schema와 transport 경계를 고정한다. |
| `tests/citizen-votes-msw.test.mjs` | 실제 `fetch` 기반 목록·상세·오류 계약 7개를 추가 | pagination·sort·상태 코드·응답 body를 검증한다. |
| `tests/cp-date-input-boundaries.test.mjs` | 삭제된 시민투표 mutation schema 경계를 제거 | 현재 read-only 범위와 회귀 테스트가 일치한다. |
| `package.json`, `package-lock.json` | `tsx@^4.23.13`을 추가하고 npm lock을 현재 manifest와 동기화 | clean-install에서 TypeScript 테스트 모듈을 직접 불러올 수 있다. |

## 결정 사항

1. **실제 조회 계약을 정본으로 사용한다.** 명세가 없는 mutation URI·payload·상태 전이를 추정하지 않고 legacy write surface를 삭제했다.
2. **지원되지 않는 검색 조건을 전송하지 않는다.** 목록 query는 `page`, `size`, 반복 `sort`만 유지하고 상태·작성자·제목·기간 검색 UI와 state를 제거했다.
3. **parser에서 placeholder 도메인 데이터를 만들지 않는다.** 작성자, 댓글, 처리 이력, 공개 정책, 상태별 전체 KPI는 실제 응답에 없으므로 model과 UI에서 제외했다.
4. **반복 sort는 Axios `paramsSerializer.indexes: null`로 보낸다.** `sort=startsAt,asc&sort=id,desc` 형태의 공개 계약을 유지한다.
5. **상세 ID와 집계 불변식을 경계에서 검증한다.** 양의 정수 ID만 query를 활성화하고 `totalCount = agreeCount + disagreeCount`가 아니면 parser가 거부한다.
6. **Node 테스트 loader에서 Vite server를 제거한다.** Node `v22.20.0`에서 assertion 완료 후 Vite close 중 발생한 native signal을 설정 완화로 숨기지 않고 `tsx/esm/api`의 `tsImport`로 실제 TypeScript 모듈을 직접 로드한다.
7. **npm lockfile은 manifest 전체와 동기화한다.** 최소 `tsx` 엔트리만 추가하면 기존 package-lock 불일치로 `npm ci`가 실패해, 승인된 `package.json`·`package-lock.json` 범위에서 정상 `npm install` 결과를 유지했다.
8. **공유 worktree의 미소유 변경을 분리한다.** `yarn.lock`은 별도 활성 세션의 변경으로 남기고 pathspec 기반 검증과 commit에서 제외한다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `node --test tests/citizen-votes-contract.test.mjs tests/citizen-votes-msw.test.mjs tests/cp-date-input-boundaries.test.mjs` | Node `v22.20.0`, 16/16 통과, exit 0 |
| 동일 16-test 명령 20회 연속 실행 | 20/20 exit 0, Vite 기반 테스트에서 관찰된 `SIGTRAP`·`SIGSEGV`·`SIGBUS` 재발 없음 |
| `npm_config_dry_run=true npm_config_ignore_scripts=true npm ci` | exit 0, package manifest와 npm lock 동기화 확인 |
| `npm run build` | `tsc -b`와 Vite production build 성공; 기존 대형 chunk 경고만 출력 |
| 변경 TypeScript·TSX·MJS 21개 대상 `npx eslint` | exit 0, 출력 없음 |
| `GIT_MASTER=1 git diff --check` | exit 0, 출력 없음 |
| TypeScript·Biome LSP | 설치돼 있지 않고 사용자가 설치를 거절해 미실행; build와 ESLint로 대체 |
| 브라우저·스크린샷·실제 backend | 사용자 지시에 따라 수행하지 않음 |

- `npm install`은 현재 dependency graph에서 high severity vulnerability 6개를 보고했다. 이번 read-only 연결 범위에서 `npm audit fix`는 수행하지 않았다.
- 전체 `npm run lint`에는 현재 변경 밖 기존 오류 73개와 경고 5개가 남아 있어 변경 파일 lint와 분리했다.

## Watcher 인계

- 정본 판정: `.codex/logs/sessions/2026-09-02-citizen-votes-api/review-log.md`의 승인 pathspec 대상 **PASS**.
- 승인 경로 발견 사항: 없음.
- Watcher가 직접 확인한 근거: 16/16 테스트, build, 변경 파일 ESLint, `npm ci` dry-run, `git diff --check` 성공.
- `yarn.lock`은 미소유·미검토 동시 작업 잔여물로 명시 제외하며 이 작업의 stage/commit에 포함하지 않는다.
- Evaluator는 현재 승인과 별개의 후속 개선점만 `evaluation-log.md`에 기록했고 현재 차단 요구사항은 없다고 판정했다.
