# News Logic 브랜치·worktree 정리 계획

## 범위와 결정

사용자가 `오케이 그럼 관련 워크트리 브랜치 삭제 작업 진행`으로 요청한 로컬 정리를 수행한다. 역할은 inject `logic`이며 애플리케이션 소스 변경은 없다. 정확한 Git 명령 묶음은 보호 실행기에 준비한 뒤 별도의 `명령 실행 승인`을 받는다.

- 실행 위치: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`
- 삭제할 linked worktree: `/private/tmp/asan-metaverse-admin-ui-news-management-logic-14a3b5c5`
- 삭제할 로컬 브랜치: `task/news-management-logic`
- Logic HEAD: `6f1d322c5e14802a0d7504d9d83890bfda215b92`
- 보존할 UI 브랜치: `task/news-management-ui`, HEAD `25c3ade2bcb26b72189945fd25921fcbb4b0e4b8`
- 중앙 문서: `/Users/okand/SynologyDrive/asan-agent-policy/logs/projects/admin-ui/codex/sessions/2026-09-09-logic-14a3b5c5`

## 확인 근거

1. Git 상태와 전체 branch·worktree 목록을 확인했다. 두 worktree의 추적·일반 미추적 변경은 없고, UI에 없는 Logic 커밋은 없다. `git merge-base --is-ancestor task/news-management-logic task/news-management-ui`는 exit 0이다.
2. 현재 관계 그래프는 revision 0, nodes가 비어 있다. 등록된 하위 관계는 없으며 기존 V3 소유권 기록을 권한 근거로 사용하지 않는다. Logic HEAD를 포함하는 로컬 브랜치는 Logic과 UI다.
3. 원본과 중앙 로그에서 상대 경로 목록이 같은 문서 10개를 확인했다. 정책이 명시적으로 허용한 `cat` 읽기의 전체 결과를 비교해 10개 모두 내용이 일치했다. Git 비추적 문서의 중앙 사본은 유지된다.
4. ignored 파일은 위 Logic 세션 문서, `node_modules/`, `dist/`, `tsconfig.tsbuildinfo`다. TypeScript 메타데이터 파일은 34,100바이트이며 빌드 입력 목록이 들어 있음을 확인했다. 해당 파일과 디렉터리까지 worktree 삭제의 구체적인 범위로 보고한다.
5. 승인된 `lsof -a -d cwd +D /private/tmp/asan-metaverse-admin-ui-news-management-logic-14a3b5c5`는 출력 없이 exit 1로 종료돼 조회 시점에 worktree 내부를 현재 디렉터리로 사용 중인 프로세스는 발견되지 않았다. 외부에서 새로 실행되는 프로세스까지 통제한다고 주장하지 않는다.
6. 이번 세션의 news 테스트 6개 파일은 46/46 통과했다. 이후 소스 변경은 없다. 이번 작업은 로컬 작업 공간 정리이므로 테스트·빌드를 반복하지 않는다. 기존 전체 lint·별도 app 타입 오류 해결이나 독립 리뷰 완료로 기록하지 않는다.

## 수행 순서

| 작업 위치 | 방법과 목적 | 기대 결과 |
| --- | --- | --- |
| 기본 UI worktree | 보호 실행기에 아래 Git 명령 묶음 준비 및 명령 실행 승인 | 정확한 삭제 대상·범위 고정 |
| 같은 실행 위치 | `git worktree remove /private/tmp/asan-metaverse-admin-ui-news-management-logic-14a3b5c5` | 연결 작업 폴더와 등록 제거 |
| 같은 실행 위치 | `git branch -d -- task/news-management-logic` | UI에 포함된 로컬 Logic 브랜치 제거 |
| 같은 실행 위치 | Git 상태·worktree·브랜치와 중앙 문서 확인 | UI HEAD·소스와 중앙 문서가 보존되고 대상만 삭제됐음을 확인 |

force 옵션은 포함하지 않는다. 일반 삭제가 실패하면 실제 오류와 잔여 상태를 보고한다. 원격 삭제·UI 브랜치 삭제·`sy-main` 병합은 포함하지 않는다.

## 현재 상태

읽기 전용 확인과 계획 기록을 마쳤다. Git 삭제 실행은 아직 하지 않았다.

## 보호 실행기 확인 후 수정된 절차

일반 Git 명령 묶음의 prepare는 `worktree 삭제·이동은 경로와 보존 조건을 확인하는 완료 정리 절차를 사용하세요`로 거부됐다. 해당 삭제 명령을 재시도하지 않는다. 위 표의 일반 삭제 명령은 실행 대상의 설명이며 현재 실행 경로로 사용할 수 없다.

현재 관계 그래프가 비어 있으므로 확인된 `sy-main → task/news-management-ui → task/news-management-logic`을 순서대로 등록한 뒤 공식 review·complete의 cleanup 절차를 준비한다. 관계 등록은 소스나 브랜치 HEAD를 옮기지 않으며 각각의 정확한 작업에 Git 명령 승인이 필요하다. 완료 검토와 정리 조건은 별도로 확인하며 아직 정리 성공을 보장하지 않는다.

첫 준비 작업은 `sy-main`을 기준 브랜치로 등록하는 operation `f87f35951c494a47a4532ce952454ee6`이다. fork는 현재 `sy-main` HEAD `5834f920fcceadbe79491791d5cf8a35ca7e2a98`이며 parent는 없다. 중앙 상태 경로의 sandbox 쓰기 제한으로 최초 준비가 실패했고, 정확한 같은 준비 명령의 호스트 권한 승인 후 prepared 상태로 저장했다. 실제 관계 등록은 실행 전이다.

후속으로 필요한 관계는 UI의 parent `sy-main`·fork `5834f920fcceadbe79491791d5cf8a35ca7e2a98`, Logic의 parent `task/news-management-ui`·fork `49aa7392882479dcb6fb08eacd73fc432d2af726`이다. 관계 등록과 완료·검증·cleanup의 구체적인 승인 경로를 따르며 직접 ref 변경·강제 삭제로 우회하지 않는다.

## 명령 승인 후 상태 변경 확인

사용자가 `명령 실행 승인`으로 첫 작업 `f87f35951c494a47a4532ce952454ee6`을 승인했다. 같은 execute를 한 번 제출했으나 PreToolUse가 `승인 후 브랜치 관계 또는 commit이 변경되었습니다`로 실행 전에 거부했다. 실제 등록·삭제 프로세스는 실행되지 않았다.

다시 조회한 그래프는 revision 2이며 다른 작업에서 `sy-main`과 그 자식 `task/fix-ui-lint-types`를 등록했다. news 관련 세 브랜치 HEAD는 그대로다. 이미 등록된 `sy-main`은 재등록하지 않으며 이전 준비 작업도 재실행하지 않는다. 다른 작업의 branch·worktree는 정리 범위가 아니다.

다음 준비 작업 `39ce4c01f7fa4aca92f8dad7abaf17f1`은 `task/news-management-ui`의 직접 부모를 `sy-main`으로 등록한다. fork는 `5834f920fcceadbe79491791d5cf8a35ca7e2a98`이다. 소스·HEAD 변경 없이 중앙 관계 정보만 등록하며 정확한 새 Git 작업의 승인이 필요하다.
