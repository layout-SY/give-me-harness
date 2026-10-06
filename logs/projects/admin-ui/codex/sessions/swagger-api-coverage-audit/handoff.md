# Swagger 전역 API 작업 인계

## 먼저 읽을 내용

**전체 Swagger 대조와 후속 작업 문서화를 완료했고, 애플리케이션 소스 구현은 시작하지 않았다.** 시민제안·투표용 별도 branch/worktree는 사용자 승인으로 생성되어 있다. 사용자가 “작업 전에 다른 세션이 이어갈 전역 핸드오프를 먼저 작성”하도록 요청하여, 이 문서 제공 시점에는 해당 공간도 깨끗하다.

이 인계는 **75 paths / 106 operations / 196 schemas**를 다룬다. 74개 operation은 기존 method·path 호출과 일치하고 32개는 일치 호출을 찾지 못했다(신규 호출 부재30 + 점검 GET/PATCH 경로·계약 불일치2). 일치한74개도 계약 완전 일치나 실서버 성공을 의미하지 않는다. 화면 호출37, API·hook까지35, API만2로 구분했다.

| 문서 | 제공 내용 |
| --- | --- |
| [작업 항목·구현 차이](./unknown/api-work-items.md) | T01~T13의 전체 operation 배정, F01~F10 상세, 기존 파일, 변경 방향, 미확정 질문, 재사용 자산, 검증·역할 인계 |
| [API별 상세 계약](./unknown/api-contracts.md) | 106개 method·path, 기능, parameter/body, DTO, 미디어 타입, 성공·오류 상태/예시, 구현 위치·상태 |
| [DTO 전체 사전](./unknown/api-schema-catalog.md) | 196개 schema 원문: required, enum, nullable, 배열·중첩·재귀, format, 길이·범위·기본값 |
| [오류·연결 방법](./unknown/api-errors-and-integration.md) | 26개 API의 52개 명시 오류 응답, 코드/필드 배열, 공통 client·parser·오류·cache·multipart·파일 처리 |
| [OpenAPI 원본 스냅샷](./unknown/openapi.snapshot.json) | 같은 세션에서 성공적으로 수집한 전체 명세, 모든 description/security/encoding 등 재확인 근거 |
| [초기 전체 대조표](./unknown/api-path-matrix.md) / [최종 요약](./final-summary.md) | 최초 정적 감사의 판정 근거와 범위·한계 |

**다른 세션의 진입 파일 절대 경로:** `/Users/okand/SynologyDrive/asan-metaverse-admin-ui/.codex/logs/sessions/swagger-api-coverage-audit/handoff.md`.
위 산출물은 기본 checkout의 이 경로에 있다. Git ignore 대상의 세션 기록이며 commit하지 않았으므로 **linked worktree·다른 clone에 자동 복제되는 파일이 아니다.** 같은 머신의 다른 세션은 이 절대 경로에서 읽는다. 후속 세션은 이 로그를 수정하지 않고 자기 세션 기록을 작성한다.

## Assignment 이동과 역할 라우팅

- 보내는 host/session/role: Codex / `swagger-api-coverage-audit` / inject `logic`.
- 받는 host/session: 아직 지정되지 않았다. 여러 후속 세션이 이 문서를 읽을 수 있으며 파일·브랜치 독점 소유권을 지정하지 않는다.
- `requested_roles`: API·DTO·hook·업무 연결의 Logic 조사 및 기술 인계.
- `confirmed_roles`: Logic(inject로 확인). 같은 역할 확인을 반복하지 않는다.
- `completed_roles`: Logic의 전역 정적 조사·문서화. 시민제안 소스 구현, Watcher PASS, UI 작업 완료를 뜻하지 않는다.
- `next_role`: T01은 Logic 구현/검증. T02~T13은 서비스 공백·공간·범위를 확인한 후 Logic 또는 필요한 UI 별도 세션을 제안한다.
- 판단 근거: 요청이 endpoint·DTO·오류·호출 패턴이며 현재 역할 범위다. 새 화면 구조/JSX/CSS 재설계는 이 승인에 없다.
- 사용자 확인: 시민제안·투표 별도 공간 구현 지시와 세 가지 계약 답변, Git 명령 실행 승인, 전역 핸드오프 선행 작성 요청이 있다.

## 근거의 시점과 신뢰 범위

- 조사·인계 일자: 2026-09-28 KST. 위치·HEAD·미커밋 상태를 문서화 중 재확인했다.
- 인계 기준 commit: `4b0b7db45aa9d15bf918a1a084370594e138a124`.
- 명세: [Swagger UI](https://admin-api.oasis.shovvel.com:8443/swagger-ui/index.html#/) → swagger-initializer.js → /v3/api-docs/swagger-config → [OpenAPI JSON](https://admin-api.oasis.shovvel.com:8443/v3/api-docs).
- 스냅샷: `Asan Digital Oasis Admin Api / v1`. 같은 세션의 최초 성공 응답을 보존했으며 이후 재조회는 HTTP502로 실패했다. **현재 시점의 서버 최신 상태를 재검증했다는 뜻이 아니다.** 다음 세션은 연결 가능하면 스냅샷과 변경분을 비교한다.
- 실제 로그인·업무 API 변경/삭제·소포 발송 등은 호출하지 않았다. static API 참조와 DTO 비교이며 live 통신·실데이터·인증 권한·배포 환경·CORS는 미검증이다.
- 오류 미기재80개는 오류가 없다는 뜻이 아니다. Void.data 빈 schema, 영상 상세, ParcelHistoryResponse.amount, 과거 영상 file-only 확정 주석 등은 확인 필요 항목으로 보존했다.

## 완료된 작업

1. 전체106개 operation과 호출 소스·DTO·parser·query/mutation·페이지 소비를 대조했다.
2. F01~F10의 기존 구현 차이와 후속 수정/확인 방법을 기록했다.
3. 기존 공통 envelope/page schema·에러 mapper·취소·query key·multipart·다운로드 재사용 경로를 확인했다.
4. 사용자 계약 답변 세 가지를 T01에 기록했다.
5. 승인된 시민제안 branch/worktree 생성 작업을 **한 번 완료**했다. 실행 operation ID: `085a4bf113df4935b5cfb2b4df24953b`. 재실행하지 않는다.
6. 전역 API 상세·schema·오류·작업별 인계와 원본 스냅샷을 자기 세션 기록에 작성했다.

## 대기 중인 작업과 확정 결정

- 시민제안·투표의 실제 source 수정/테스트는 남아 있다. branch를 만들었다고 API 연결이 완료된 것은 아니다.
- **담당부서:** 연결 제외, 선택 시 미지원 안내, 변경 요청 차단.
- **reviewResult:** null 또는 필드 누락 허용, 기존 입력란 빈 값 표시.
- **개발 MSW:** 시민제안·투표 가로채기 제거, dev에서도 실제 서버 요청.
- 위 세 결정과 이미 승인된 동일 Git 생성 작업을 다시 질문하지 않는다.
- 나머지 도메인은 전역 감사/인계 요청만 받았다. T02~T13의 구현 범위·서비스 공백·공간·Git 변경은 이 문서로 승인되지 않는다.
- 일반 `진행` 또는 구현 승인을 미확정 API/정책 질문의 답변으로 대체하지 않는다. 각 작업의 미확정 사항을 확인하고 해당 결정을 전제로 한 작업을 시작한다.

## 보내는 작업의 위치와 변경 상태

- project/저장소 루트: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`.
- 실제 문서 작성 workdir/worktree: 위 기본 checkout.
- branch: `sy-main`; HEAD: `4b0b7db45aa9d15bf918a1a084370594e138a124`.
- staged/unstaged/untracked: Git status 기준 없음.
- ignored 산출물: `.codex/logs/sessions/swagger-api-coverage-audit/`의 본 문서·관련 Markdown/JSON. 이 파일들은 status의 untracked에 나타나지 않는다.
- 완료한 source commit: 없음. 현재 작업의 app/package/config 변경 없음.
- 새 Git ref/공간: 아래 시민제안 branch와 linked worktree만 승인 생성.
- 다른 작업자 변경: 확인 시 두 공간 모두 깨끗함. 이후 변경은 반드시 보존하고 재확인한다.

## 인계 대상 작업 공간

<a id="citizen-workspace"></a>

### 작업 공간: 시민제안·투표 연결

- 기능: T01의 제안 상태/review-result PATCH, 제안·투표 summary, reviewResult 매핑, 부서 변경 차단, dev MSW 해제.
- 역할: Logic.
- project/common Git directory: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui` / `/Users/okand/SynologyDrive/asan-metaverse-admin-ui/.git`.
- 목적지 branch: `feature/citizen-proposal-vote-api`.
- worktree·명령 실행 디렉터리: `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/citizen-proposal-vote-api`.
- 상태: **실재하는 linked worktree**. `git worktree list --porcelain`과 해당 위치의 status/common-dir로 확인.
- HEAD/fork: `4b0b7db45aa9d15bf918a1a084370594e138a124`.
- 직접 부모: `sy-main`. 보호 실행기의 branch relation graph에 등록되어 있음.
- 기존 commit·미커밋 변경: fork 이후 작업 commit 없음, staged/unstaged/untracked 없음.
- 분리 이유: 사용자가 시민제안·투표를 별도 branch/worktree에서 진행하도록 요청했다.
- 공유 순서: 후속 Logic 작업은 이 공간에서 이어간다. UI 필요 시 같은 기능의 순차 작업 공간으로 공유 가능하지만 역할 범위와 미완료 계약부터 확정한다.
- 진입 전 확인: workdir·branch·HEAD·status·common-dir를 재조회한다. 본 문서 이후 변경이 있으면 차이를 읽고 기존 변경을 보존하며 이어간다.
- 승인된 Git 작업: 이 branch/worktree의 생성과 부모 관계 등록은 완료.
- 미승인: stage/commit/merge/공간 정리. 생성 승인으로 해석하지 않는다.
- 파일시스템: 기본 writable root 밖의 linked worktree이므로 필요한 도구 sandbox 승인은 Git 승인과 별개다. 다른 장소로 임의 이동하거나 임시 worktree로 우회하지 않는다.

### 작업 공간: 전역 감사 기록 참조

- 기능: 이 핸드오프와 스냅샷의 읽기 전용 참조.
- 역할: 후속 세션이 자신의 확인된 역할에서 참조.
- 실제 위치: 기본 checkout `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`, branch `sy-main`, HEAD `4b0b7db45aa9d15bf918a1a084370594e138a124`.
- 직접 부모: 기준 branch이므로 없음.
- 해당 문서 작성만 완료, 다른 세션이 이 로그를 고쳐서 소유권을 넘기는 흐름은 아니다.

### 작업 공간: T02~T13 후속 기능

- 역할·수정 목표·재사용 후보·질문·검증 기준: [작업 항목](./unknown/api-work-items.md)에 도메인별 기록.
- project: 같은 `asan-metaverse-admin-ui`.
- 목적지 branch/worktree·기준 commit·직접 부모: **미정, 생성하지 않음**. 새 작업의 사용자 요청과 최신 실제 저장소 상태를 확인해 결정한다.
- 실제 병렬 source 변경이면 각각 승인된 linked worktree를 사용한다. UI→Logic 순차 같은 결과물은 공간을 무조건 늘릴 필요가 없다.
- 새 공간 필요 시 중앙 정책의 지정 저장 폴더와 Git 보호 실행 경로를 따르고 생성 전 정확한 위치/대상/영향을 승인받는다.

## 역할별 상세 작업

구체적인 파일·DTO·props/callback·수정 순서·의존성·질문·검증은 [T01~T13 작업 문서](./unknown/api-work-items.md)에 있다. 핵심 소비 계약은 다음과 같다.

- T01 Logic: 기존 목록/상세 hook·controller와 `KpiStripItem[]`, `reviewComment/canSave/isSaving/save`, 상태/부서 callback을 활용한다. 새 PATCH는 void 성공이며 기존 `onSuccess(updated)`·detail cache 대입 가정을 바꿔야 한다.
- T02~T05/T11 Logic: 기존 API·hook 자산을 먼저 보정한다. “API 존재”와 “화면에 연결”을 분리하고 UI 담당에게 확정 query·mutation variables·row/detail·ID 출처·error/pending/cache를 전달한다.
- T06 Logic/UI: me·권한·메뉴·route/store의 계약을 먼저 확정한다. 역할 권한 body는 `permissionCodes:string[]`, 계정 role body는 `roleIds:integer[]`다. 서로 대체하지 않는다.
- T07~T10: 기존 호출부와 폼 mapping을 함께 확인한다. path 변경만 하거나 nullable/필수/정수를 DTO 한 곳에서만 바꾸면 실제 제출 흐름과 달라질 수 있다.
- T12~T13: 제품 사용 여부부터 확정한다. Swagger에 있다는 이유로 화면·폴링·관리 기능을 자동 생성하지 않는다.
- UI가 필요한 후속 세션은 현재 Logic 역할을 임의 확장하지 않는다. 역할·공간·선행 Logic 결과를 명시하여 인계한다.

## 협업 순서와 Git 통합

- 전역 handoff 제공 → 시민제안 기존 공간에서 승인 범위 구현 → 실제 포맷/관련 테스트/lint/build → 현재 변경 검토 → 별도 Git 승인 순서다.
- 다른 세션의 API 연결은 T별로 선택하되 해당 요청/정책 결정을 확인한다. 이 문서는 모든 작업에 대한 일괄 실행 명령이 아니다.
- 공유 영향 후보: common API/에러, auth/store/router/navigation, mock 등록/정책, 공통 contract tests. 각 작업 branch의 실제 diff를 비교하고 같은 파일의 동시 수정을 조율한다.
- 시민제안 통합 대상은 직접 부모 `sy-main`. 통합 직전 형제·하위·부모 변경과 미커밋 상태를 다시 검토한다. 완료한 생성 operation을 merge 승인으로 재사용하지 않는다.
- 산출물 책임: 이 세션은 owner. 후속 세션은 자기 로그에 실제 변경과 검증·미완료를 남긴다.

## 명령어 및 결과

| 수행 | 결과 |
| --- | --- |
| 정책 task-role-routing/git-branch-strategy/documentation와 handoff template 읽기 | 현재 역할·기록·승인 흐름 확인 |
| Swagger initializer/config/OpenAPI GET | 최초 전체 수집 성공, 후속 OpenAPI 재조회는502 |
| rg·API/DTO/parser/hooks/pages/shared API 읽기 | 106개 대조, F01~F10 및 추가 미확정 기록 |
| 보호 실행기 execute 085a4bf113df4935b5cfb2b4df24953b | 시민제안 branch/worktree 생성 완료 |
| git status/worktree list/common-dir/branch graph | 두 공간의 HEAD 동일·clean·부모관계 확인 |
| 문서 검증 | 106 operation/작업 배정·196 schema·261 refs·1,582 링크 오류0; 요청 parameter76/body45·성공 content106·오류 response52개 원문 일치 |

과거 복합 검색/임시 AST 명령 일부는 정책 guard에 의해 실행되지 않았고, sandbox 내 네트워크는 DNS 실패 후 승인된 curl로 수집했다. 실행되지 않은 명령을 검증 성공으로 계산하지 않는다. 이후 동일 차단 명령을 반복해서 우회하지 않았다.

## 실행하지 않은 검증

- formatter/lint/test/build: **소스 변경 없는 문서 작업이므로 미실행**. 이 문서에 있는 테스트 명령은 후속 구현 검증 계획이다.
- Watcher PASS/FAIL, 브라우저 캡처·시각 QA, 실제 업무 API·인증·운영 상태: 수행하지 않았다.
- 최신 OpenAPI 재수집: 후속502 때문에 성공하지 못했다. 저장한 스냅샷의 수집 시점 한계를 유지한다.

후속 소스 구현에서는 해당 작업의 현재 바인딩 정책 formatter를 실제 workdir에서 실행하고 관련 `node --test`, `npm run lint`, `npm run build`를 수행한다. 현재 package.json에는 `test` script가 없으므로 `npm run test`를 실행 완료로 기록하지 않는다.

## 관련 경로와 스킬

- 현재 source 재사용 기준: `src/shared/api/common/response.dto.ts`, `src/shared/api/api-client.ts`, `src/shared/api/common/api-result/`, `src/shared/api/error/`; 도메인별 실제 파일은 작업 문서의 링크 참조.
- 후속 세션은 자신의 inject bundle에서 `policy-task-role-routing`, `policy-git-branch-strategy`, `policy-documentation`을 읽고 적용한다.
- 구현 시 `policy-data-fetch-layer`, `policy-coding-convention`, `policy-type-definition`, `policy-validation`, `recipe-api-authoring` 등 작업에 필요한 현재 스킬과 인접 코드를 확인한다. 이 문서의 이전 bundle 경로를 새 세션의 정책 원본으로 강제하지 않는다.

## 다음 조치

다른 세션에 이 파일의 절대 경로와 선택할 T번호를 전달하면 전체 DTO/에러/기존 구현 차이까지 추적할 수 있다. 인계받은 세션은 지정 작업과 승인 상태를 확인하고, 최신 branch·worktree·HEAD·dirty 차이를 읽은 뒤 미확정 계약을 먼저 해결한다. 시민제안·투표는 이미 생성된 공간과 확정된 세 가지 답변을 사용해 이어간다.
