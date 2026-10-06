# 시민제안·투표 API 연결 완료

Swagger에서 누락된 API 4개를 기존 화면에 연결했다. 구현 커밋 4b2aa3f와 문서 별도 커밋 0a39dce를 보존하고, 사용자 승인 후 2026-09-29 sy-main 병합을 완료했다. 병합 커밋은 84d47a8이며 병합 후 lint·build 검증과 관련 테스트 46개가 모두 통과했다.

## 위치와 승인

- 역할: Logic. 사용자의 “작업 진행”으로 현재 세션의 구현 승인을 확인했다.
- branch: feature/citizen-proposal-vote-api, 직접 부모 sy-main.
- worktree/명령 위치: /Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/citizen-proposal-vote-api.
- 구현 기준 HEAD: 4b0b7db45aa9d15bf918a1a084370594e138a124. 커밋 후 HEAD: 4b2aa3f.
- 원본 근거: 2026-09-28 성공 조회한 https://admin-api.oasis.shovvel.com:8443/v3/api-docs 와 기존 전역 인계 T01의 확정 계약.
- Git 상태: 22개 파일을 커밋한 뒤 git status --short 출력 없음. 작업 공간이 깨끗하다.

## 실제 변경

1. cp-proposal API·DTO·parser에서 PATCH /citizen/proposals/{proposalId}와 PATCH /citizen/proposals/{proposalId}/review-result를 추가했다. 기존 POST 처리 호출은 제거했다. 공통 ApiClient의 인증·오류·취소·envelope를 재사용하고 성공 data:null이 undefined로 정규화되는 경우까지 검증한다.
2. 상태 저장은 목록에서 쓰던 PROPOSAL_API_STATUS_BY_STATUS를 재사용한다. REVIEWING→UNDER_REVIEW, RETURNED→REJECTED 등을 보낸다. 성공 후 기존 조회를 취소하고 목록·해당 상세·제안 집계를 무효화한다.
3. 검토 결과는 reviewResult 문자열/null/누락을 기존 reviewComment로 매핑한다. 제출 시 trim·공백 거부·최대 5,000자·변경 여부를 확인한다. 성공 후 해당 상세만 재조회하며 후속 편집 초안을 이전 저장 응답으로 덮어쓰지 않는다.
4. GET /citizen/proposals/summary와 GET /citizen/votes/summary를 추가해 기존 KPI 계약에 연결했다. 검색 목록 total과 전역 집계를 구분하며 투표 total을 부분 집계의 합으로 만들지 않는다. 최초 로딩·집계 실패 표시·재시도는 기존 controller/KPI 계약으로 연결했다.
5. 담당부서 선택은 미지원 안내만 표시하고 변경 요청을 만들지 않는다.
6. 개발용 handlers 등록에서 제안·투표를 제외하고 /citizen/의 mock 전용 판정을 해제했다. 기존 테스트 전용 handler·fixture와 다른 도메인의 등록은 보존했다.

신규 파일은 제안·투표 summary query 2개, 제안 mutation options 1개, 연결 테스트 1개다. UI 구조·CSS·패키지·공통 API 동작은 변경하지 않았다.

## 검증과 검토

- 바인딩된 formatting.py apply: 실제 Prettier로 수정한 22개 파일 포맷 완료. 타입 보완 후 해당 파일을 다시 포맷했다.
- node --test tests/citizen-proposal-vote-connection.test.mjs tests/citizen-proposals-contract.test.mjs tests/citizen-proposals-msw.test.mjs tests/citizen-votes-contract.test.mjs tests/citizen-votes-msw.test.mjs tests/cp-comment-proposal-input-boundaries.test.mjs tests/mock-api-policy.test.mjs: 46/46 통과.
- 새 연결 테스트 14개는 실제 Axios·MSW·TanStack Query와 기존 SSR hook 검사 방식으로 method/body/인증/signal, 상태 매핑, 빈 성공·실패, null/누락, 입력 한도, 선택적 캐시 무효화·이전 조회 취소, 활성 상세/집계 재조회, KPI·부서 차단·개발 handler 비가로채기를 검증한다.
- npm run lint: 최종 exit 0.
- npm run build: 최종 exit 0. 중간 QueryFilters 배열의 tuple 추론 오류는 라이브러리 QueryFilters 타입을 명시해 수정했다.
- git diff --check: exit 0.
- 최초 테스트·빌드는 linked worktree 캐시 쓰기 EPERM이 있었고 필요한 실행 권한 승인 후 완료했다. formatter도 중앙 events.lock 기록 권한 승인 후 완료했다.
- 변경 검토: Swagger의 4개 method/path·요청 필드, 공통 envelope 처리, void 성공과 기존 상세 응답 가정 제거, 기존 소비자 연결, 관련 없는 handler 보존을 재확인했다.

## 남은 범위와 한계

실서버 업무 API의 저장·권한·CORS와 실제 브라우저 동작은 검증하지 않았다. 테스트 통과는 실제 운영 API 성공을 뜻하지 않는다. 브라우저 캡처/시각 QA는 수행하지 않았다. 빌드에는 vite-tsconfig-paths 전환 안내와 500 kB 초과 chunk 경고가 남았다. 이 작업의 기능 오류로 인한 빌드 실패는 없다.

사용자의 커밋 요청과 명령 실행 승인 후 보호 작업 991562b2827ea697208698795b8b4229를 한 번 실행했다. 결과는 done이며 커밋은 4b2aa3f, 메시지는 `feat: 시민제안·투표 누락 API 연결`이다. 22개 파일, 692줄 추가·115줄 삭제를 포함한다.

## 후속 병합 요청: 실행 승인 후 보류

- 사용자가 sy-main 병합을 요청하고 `명령 실행 승인`으로 보호 작업 ae6d6da6e35845be96296eb48bf6deb4를 승인했다. 2026-09-28 기본 checkout에서 해당 작업을 한 번 실행했다.
- 계획은 feature/citizen-proposal-vote-api → sy-main의 ff-only 병합, 린트·빌드와 별도 관련 테스트 검증이다. 브랜치·worktree 정리 및 원격 반영은 포함하지 않는다.
- 보호 실행기는 `source 또는 target에 미커밋 변경이 있습니다. 다른 작업을 stage·commit하지 않고 병합을 보류합니다.`라는 사유로 exit 2를 반환했다. 승인 기록은 저장됐고 작업 stage는 prepared다.
- source는 깨끗하지만 sy-main에 별도 점검 API·테스트·라우트 문서의 미커밋 변경이 있다. 제안·투표의 22개 변경 경로와 겹치지 않아도 실행기가 clean 상태를 요구했다. 다른 작업의 파일을 stage·commit·stash·복원하지 않았다.
- 실행 후 sy-main HEAD는 4b0b7db45aa9d15bf918a1a084370594e138a124, source HEAD는 4b2aa3fd7b7e66fb2281bdeded1f046a96a621ae로 이전과 같다. 병합 및 병합 후 검증은 실행되지 않았다.
- 선행 조건: sy-main의 다른 작업 변경을 해당 작업 흐름에서 보존·정리한 뒤 실제 HEAD·dirty 상태와 병합 전략을 다시 검토한다. 정책 실행기의 차단을 우회하지 않는다.

## 문서 별도 커밋 완료와 일반 병합 준비

- 이후 점검 API/controller 작업은 b5c35a8412a60c0bb5b9cccdf6710728c255c9e2로 sy-main에 커밋됐다.
- 사용자가 남은 docs/admin-routes.md를 별도 커밋한 뒤 병합하도록 지시하고 실행 승인했다. 보호 작업 e551ec56c199a43713dd69a33ab9a507 실행 결과는 done이다. 문서 한 파일 96줄을 `docs: 관리자 UI 라우트 목록 정리` 메시지로 커밋했으며 결과 HEAD는 0a39dce72431b4f5cfb4aac26f7cfac22f260cf7이다.
- 문서 내용은 현재 라우터, 인증 redirect와 관리 메뉴 builder에 대조했다. 커밋 후 sy-main과 제안·투표 source 작업 공간이 모두 깨끗한 상태임을 확인했다.
- sy-main이 전진해 일반 merge로 재검토했다. 검토 a39ed55fc4d847a9b5efa57a525c5d2e의 merge-tree 결과는 ff_only_possible=false, text_conflicts=false다. 점검·문서 변경과 제안·투표 변경은 파일 및 도메인 API/query key가 분리돼 있다. source 하위 branch는 없으며 문의 UI 형제의 미커밋 변경도 별도로 검토했다.
- 새 병합 작업 40375f015de44cf384c6939201da791a를 준비했다. source는 4b2aa3fd7b7e66fb2281bdeded1f046a96a621ae, target은 0a39dce72431b4f5cfb4aac26f7cfac22f260cf7이다. 병합 실행 승인 전이며, 완료 후 린트·빌드와 관련 테스트를 확인한다. 로컬 브랜치·worktree 삭제 및 원격 반영은 포함하지 않는다.

## 2026-09-29 병합 재확인과 문의 화면 작업 대기

- 이전 일반 병합 작업은 문의 branch의 계속된 변경으로 무효화됐다. 갱신한 작업 6393d1bbfd094467b53cfd25b32e3228도 사용자 실행 승인 후 문의 controller 파일 3개 추가를 감지해 실행 전에 차단됐다. 사용자는 이후 `문의 UI 작업 완료 후 병합`을 선택했다.
- 2026-09-29 문의 controller 커밋 840051ebedf7190c7eaf3f684d0dba9d4bd384a5가 deb11f92a84ca774033177383a137bd62bf21b2a로 sy-main에 병합된 것을 확인했다. 그 확인 시점에는 세 작업 공간이 모두 깨끗했다.
- 공식 검토 8922f6eec9e74cc89269a76a356693b6의 source는 기존 4b2aa3f, target은 deb11f9였고 merge-tree는 일반 병합의 텍스트 충돌이 없다고 판정했다. source 하위 작업도 없었다.
- 사용자의 `작업 진행` 요청 후 위 검토로 complete를 준비했으나, `검토한 저장소 또는 변경이 달라졌습니다. 재검토하세요.`라는 오류로 exit 2를 반환했다. 새 실행 작업은 생성되지 않았고 병합하지 않았다.
- 다시 확인한 문의 branch에는 src/app/router/routes.tsx, 문의 유형 설정, 메뉴 builder 수정과 inquiry/inquiry-type 화면·index·컬럼 등 미추적 파일이 생겼다. 관계 graph는 동일하며 이 문의 작업 공간 변경이 기존 검토와 달라진 근거다.
- 당시 사용자 선택을 유지해 문의 UI 작업 완료까지 병합을 보류했다. source 4b2aa3f와 sy-main deb11f9를 보존했으며, 해당 시점에는 병합 후 검증을 실행하지 않았다.

## 2026-09-29 sy-main 병합 완료

- 사용자의 재확인 후 병합 요청에 따라 문의 UI 커밋 b785adf141e636a891485d255bb0097bf6b3299c와 작업 공간의 clean 상태를 확인했다. 제안·투표 변경과 문의 controller·UI·라우트·메뉴의 영향 범위를 검토했다. 문의 UI 커밋 자체는 이번 병합에 포함하지 않았다.
- 공식 검토 b9619e4f876f4b6b892f1472fe9234a8을 바탕으로 보호 작업 574ac3099efc4124a855c568cc18adfb를 준비하고, 사용자의 `명령 실행 승인` 후 한 번 실행했다. 실행기는 exit 0, stage retained로 종료했다.
- source: feature/citizen-proposal-vote-api, 4b2aa3fd7b7e66fb2281bdeded1f046a96a621ae. target: sy-main, 병합 직전 deb11f92a84ca774033177383a137bd62bf21b2a.
- 병합 실행 위치: /Users/okand/SynologyDrive/asan-metaverse-admin-ui. 일반 merge 결과는 84d47a87f032ec5cc106f4fad8ec3a9709e901e1이며 메시지는 `merge: feature/citizen-proposal-vote-api 작업을 sy-main에 통합`이다.
- 보호 실행기에 지정한 병합 후 npm run lint·npm run build 검증이 통과했다. 공식 graph의 해당 source resolution에서 같은 작업 ID·병합 커밋과 verification=passed를 확인했다.
- 병합된 sy-main에서 위 7개 테스트 파일을 node --test로 실행해 46/46 통과, 실패·취소·건너뜀 0, exit 0을 확인했다.
- git merge-base --is-ancestor로 source 커밋의 sy-main 포함을 확인했다. 검증 후 sy-main과 source의 git status --short --branch에는 브랜치명만 출력돼 두 작업 공간 모두 깨끗하다.
- 승인 범위대로 source 로컬 branch와 linked worktree를 보존했다. 원격 push는 수행하지 않았다. 실서버 저장·권한·CORS와 실제 브라우저 동작의 미검증 범위는 위와 같다.

## 2026-09-29 사용자 요청에 따른 로컬 정리: 빈 폴더 처리에서 보류

- 사용자가 병합된 feature/citizen-proposal-vote-api 로컬 branch와 linked worktree 삭제를 요청하고 보호 작업 4b4590a44bf14e5abc229e6f3f8f57e9를 명시적으로 승인했다. 중앙 잠금 파일 쓰기 권한 오류로 실행 전에 중단된 뒤 재승인을 받아 필요한 쓰기 권한으로 실행했다.
- 실행 결과 기존 sy-main HEAD 84d47a87f032ec5cc106f4fad8ec3a9709e901e1을 유지했고, 지정한 lint·build가 모두 exit 0으로 통과했다. 최초 정리는 ignored 세션 폴더와 tsconfig.tsbuildinfo가 미보존 항목으로 판정돼 cleanup-deferred로 종료했다.
- 이 세션의 plan.md와 final-summary.md를 기본 작업 공간 /Users/okand/SynologyDrive/asan-metaverse-admin-ui의 동일한 .codex/logs/sessions/citizen-proposal-vote-connection/ 경로에 보존했다. tsconfig.tsbuildinfo는 해당 경로의 unknown/cleanup-backup/tsconfig.tsbuildinfo.b64에 원본 바이트를 보존했다. 세 파일 모두 원본과 보존본의 바이트 및 SHA-256 일치를 확인한 뒤 source의 파일을 제거했다. 기본 작업 공간의 기존 tsconfig.tsbuildinfo는 덮어쓰지 않았다.
- 같은 승인 작업의 공식 recover를 실행했지만, 파일이 없는 source의 .codex/logs/sessions/citizen-proposal-vote-connection/ 디렉터리도 미보존 ignored 항목으로 판정돼 정리가 보류됐다. 해당 폴더의 재귀 파일 목록은 빈 배열이었다.
- 빈 디렉터리만 제거하는 rmdir 명령은 PreToolUse의 `파일 변경은 대상이 명확한 Edit/Write/apply_patch 도구를 사용하세요.` 규칙에 차단됐다. 강제 삭제나 다른 명령으로 우회하지 않았다. 브랜치·워크트리 삭제는 아직 완료하지 못했다.
- 후속 조치: 중앙 정책의 별도 세션에서 완료 정리의 빈 ignored 디렉터리 처리와 디렉터리 삭제 도구 규칙의 충돌을 해결한 뒤, 동일 승인 작업의 recover로 재개한다. 애플리케이션 소스 변경이나 새로운 병합은 필요하지 않다. 현재 세션 산출물의 실제 위치는 기본 작업 공간의 위 경로다.
- 이후 사용자가 브랜치·워크트리 강제 제거를 명시적으로 요청했다. source의 추가 변경 없음, sy-main 포함, 기본 작업 공간의 세션 기록 보존을 다시 확인하고 기본 저장소에서 `git worktree remove --force /Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/citizen-proposal-vote-api && git branch -D feature/citizen-proposal-vote-api`를 요청했다. PreToolUse가 `브랜치 식별자를 보존하도록 관계 명령의 rename 또는 안전한 완료 정리를 사용하세요.`라는 사유로 명령 실행 전에 차단했다. 강제 제거도 실행되지 않았으며, 다른 명령으로 우회하지 않았다.
