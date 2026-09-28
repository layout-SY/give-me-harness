# 브랜치 삭제 후 남은 시민 토론 워크트리 정리 차단

## 후속 확인 — 2026-09-11

사용자에게 직접 삭제 명령을 안내한 뒤 확인 요청을 받아 조회했다. citizen-discussion-api는 Git worktree 목록과 실제 경로 모두 삭제됐다. citizen-discussion-api-resume은 Git에 detached@32e2265로 등록돼 있고 실제 경로도 남아 있다. 두 로컬 브랜치는 모두 없으며 sy-main@c19bdd58은 32e2265를 포함한다. 남은 요청은 resume worktree 삭제다. 이 세션이 직접 worktree remove를 실행한 결과로 기록하지 않는다.

## 요청과 현재 결과

사용자가 브랜치만 삭제되고 두 워크트리가 남았다는 설명을 확인한 뒤 `워크트리도 삭제해`라고 추가 요청했다. 삭제 대상은 다음 두 linked worktree다. 두 위치는 기본 checkout과 같은 Git common directory를 공유하며 현재 실행 위치가 아니다.

- /Users/okand/SynologyDrive/asan-metaverse-user-ui-worktrees/citizen-discussion-api, detached@d12dfe508e136c2fccefb84128c58a48c4ad4ea2.
- /Users/okand/SynologyDrive/asan-metaverse-user-ui-worktrees/citizen-discussion-api-resume, detached@32e2265e3581a2bc0590ff01f935ebc1e61423a0.

병합과 두 로컬 브랜치 삭제는 완료됐지만 이번 추가 워크트리 삭제는 수행하지 못했다. 현재 보호 실행기의 prepare가 직접 worktree remove를 거부하고, 지원하는 완료 정리는 살아 있는 source branch가 checkout된 worktree에만 적용된다. 삭제 요청을 승인 대기 작업으로 준비할 수 없어 새 `명령 실행 승인`을 요청하지 않았다. 파일·Git 메타데이터·승인 상태를 우회 변경하지 않았다.

## 실제 조회와 보존 대상

- sy-main@badf615ec74a435e9710774a51253a081e6db26d에는 resume 작업이 병합돼 있다. 기존 88ff206f 완료 작업에서 lint·build를 통과했고 두 source branch는 삭제됐다.
- 기존 worktree에는 24개 정책 파일의 미커밋 삭제, README·package.json 변경이 남아 있다. 독자적인 앱 소스 변경은 없고 README 고유 안내는 별도 보존 검토 대상이다.
- 기존 worktree의 ignored 항목: .codex/logs/sessions/2026-09-07-citizen-discussion-api-handoff/, node_modules/.
- resume worktree는 tracked clean이며 ignored 항목은 .codex/logs/sessions/2026-09-08-logic-d7a35053/, .codex/logs/sessions/2026-09-09-citizen-discussion-api-resume-72a6097e/, node_modules/, dist/다.
- 미보존 로그나 미커밋 변경의 강제 삭제를 실행하지 않았다. 기존 완료 작업의 archive에는 resume 로그 보존 기록이 있으나 이번 조회에서 모든 파일의 아카이브 동등성을 새로 검증하지 않았다.

## 실패한 준비 명령과 근거

현재 bundle의 보호 실행기를 python3 -I로 호출하고 프로젝트 root에서 아래 두 Git 명령을 하나의 prepare 대상으로 지정했다.

```sh
git -C /Users/okand/SynologyDrive/asan-metaverse-user-ui worktree remove /Users/okand/SynologyDrive/asan-metaverse-user-ui-worktrees/citizen-discussion-api-resume
git -C /Users/okand/SynologyDrive/asan-metaverse-user-ui worktree remove /Users/okand/SynologyDrive/asan-metaverse-user-ui-worktrees/citizen-discussion-api
```

prepare --host codex의 결과는 exit 2, `Git 작업: worktree 삭제·이동은 경로와 보존 조건을 확인하는 완료 정리 절차를 사용하세요.`다. 실제 git worktree remove는 실행되지 않았고 prepared 작업 ID도 생성되지 않았다.

읽기 전용으로 바인딩된 runtime의 CLI와 cleanup을 확인했다.

- git_operations.py의 일반 prepare는 worktree remove·prune·repair·move·lock·unlock을 일괄 거부한다.
- cleanup 447행은 source ref가 기존 source_head와 같은지 확인한다. 이미 ref가 삭제된 이번 상태는 충족하지 못한다.
- cleanup 451–456행은 operation.source_worktree가 있으면 해당 worktree가 source branch를 checkout했는지 요구한다. detached 정리 경로가 없다.
- cleanup 463–471행은 미커밋 파일이나 허용 생성물 외 ignored 파일이 있으면 정리를 보류한다.
- CLI 589–612행에는 독립 detached worktree 삭제 명령이 없다.
- 완료된 작업 88ff206f는 cleaned이고 source_worktree=null, 이전 5cf52338은 retained이므로 recover로 새 삭제 범위를 추가할 수 없다.

## 다음 조치

중앙 정책 저장소의 별도 세션에서 완료된 branch와 분리된 linked worktree를 명시적으로 정리하는 승인 경로를 보완해야 한다. 기존 branch를 되살리거나 관계 graph·operation JSON을 직접 바꿔 완료 조건을 우회하지 않는다. 현재 user-ui Logic 세션에서 중앙 정책 snapshot은 수정하지 않는다.

지원 경로는 같은 Git common directory·정확한 경로·detached HEAD·기준 branch의 commit 포함 여부를 확인하고, 기본 worktree·현재 실행 위치를 보호하며, 미커밋 변경과 ignored 로그를 먼저 보존·검증할 수 있어야 한다. 사용자 승인한 두 경로만 삭제하고 다른 worktree는 건드리지 않아야 한다. 회귀 검증에는 정상 detached 정리, 미보존 파일 차단, 다른 프로젝트와 기본 worktree 차단, 실패 뒤 동일 작업 복구를 포함한다.

정책 보완 후 새 user-ui inject 세션에서 이 기록과 실제 상태를 읽고 두 워크트리 삭제를 이어간다. 현재 이 추가 요청은 미완료이며 두 디렉터리는 그대로 남아 있다.
