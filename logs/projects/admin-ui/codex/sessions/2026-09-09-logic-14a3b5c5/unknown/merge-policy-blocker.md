# 서로 다른 host의 자식·부모 병합 권한 제한

## 실제 finish 요청의 차단 근거

사용자의 추가 `merge 시작해` 요청 후 기존 계약의 finish 명령을 도구에 제출했다. PreToolUse는 명령 실행 전에 다음 이유로 거부했다: `Git worktree의 통합 소유자가 다른 assignment입니다: /Users/okand/SynologyDrive/asan-metaverse-admin-ui (owner=f14c4487b1bc4431a3ac89583753fad6)`.

따라서 아래 소유권 충돌은 코드 확인에 더해 실제 도구 거부 결과로 확인됐다. Git merge 프로세스는 시작되지 않았고 finish 영수증·target HEAD 변경은 없다. 같은 상태에서 finish를 재시도하지 않는다. readiness 조회상 해당 finish SHA는 여전히 pending이며, 소유권 검사가 먼저 거부하므로 명령 실행 승인이나 반복되는 일반 merge 지시만으로 해결되지 않는다.

사용자는 news Logic 자식 브랜치를 UI 부모에 병합하라고 요청했고, UI의 Git 소유권을 현재 Codex 세션으로 인계해 진행하는 방향도 승인했다. 그러나 현재 완료 workflow와 공개 assignment-handoff 명령의 조건을 함께 충족할 수 없어 실제 인계·병합은 수행하지 않았다. 사용자 승인 부족으로 분류하지 않는다.

## 확인한 Git 상태

- source: task/news-management-logic, HEAD 6f1d322c5e14802a0d7504d9d83890bfda215b92.
- target: task/news-management-ui, HEAD 49aa7392882479dcb6fb08eacd73fc432d2af726.
- source에 추가된 commit은 위 1개이며 fast-forward 가능하다. 양쪽 worktree는 clean이다.
- source Git 담당 host: codex. 격리 worktree claim owner: 14a3b5c529a94f6d8c36fb91cfee693d.
- target worktree claim owner: f14c4487b1bc4431a3ac89583753fad6, host claude, role ui.
- 현재 assignment는 host codex, role logic이며 이미 native session이 시작돼 있다.

## 서로 충족할 수 없는 조건

1. 바인딩된 managed_policy_guard의 branch_workflow_integrator_denial은 finish·verify·close 실행 host가 source branch의 Git 담당자와 같아야 한다고 검사한다. 따라서 현재 source의 실행 host는 codex다.
2. 같은 guard의 git_ownership과 branch_workflow의 assert_integration_owner는 integration_worktree의 claim이 실행 assignment와 같아야 한다고 검사한다. 현재 target worktree는 claude UI assignment가 소유한다.
3. 중앙 공개 assignment-handoff의 구현인 lib/agent_policy/assignment.py는 source·target의 host와 role이 같아야 하며 target의 native_session이 아직 없어야 한다. claude/ui에서 이미 실행 중인 codex/logic으로 넘기는 현재 요청은 두 조건 모두 맞지 않는다. 상태를 변경하거나 이 조건을 우회하지 않았다.
4. 기존 UI 세션에서 현재 source의 완료 계약을 실행하는 방안도 1번의 source Git 담당 host 조건을 충족하지 못한다. 어느 한 세션이 바로 실행하면 된다고 안내해서는 안 된다.

최초에는 인계로 진행할 수 있다고 안내했으나 공개 인계 도구의 제한 확인이 부족했다. 실제 구현을 읽고 위와 같이 정정했다. 같은 인계 승인을 다시 요구해 해결할 수 있는 문제가 아니다.

## 준비된 병합 계약

- finish proposal SHA-256: 9f248106a7264e1a3004091c0f519a0e359d5b58001a16ca36fe64dd672f7747.
- 파일: 기본 프로젝트의 .git/asan-agent-policy/finish-proposals/9f248106a7264e1a3004091c0f519a0e359d5b58001a16ca36fe64dd672f7747.json.
- 방식: ff-only. source·target은 위 전체 HEAD에 고정돼 있다.
- integration worktree: 기본 프로젝트 폴더. 사후 검증: npm run build, npm run lint 순서. cleanup 없음, 자식 branch·worktree 보존.
- 계약 생성만 exit 0으로 완료했다. 해당 SHA에 대한 별도 사용자 승인과 finish·verify·close는 아직 수행하지 않았다.
- 계약 생성 최초 시도에서 grill-me-review·portfolio-log의 템플릿 필수 구조 누락이 발견됐다. 실제 점검·구현 근거를 템플릿 구조에 맞춰 보완한 뒤 계약 생성이 통과했다. 독립 Watcher 판정을 작성한 것은 아니다.

## 검증과 후속

news 테스트 46개·대상 lint·build는 통과했다. 전체 lint는 기존 범위 밖 68개 오류·5개 경고로 실패한다. 별도 app 타입 검사도 기존 14개 오류가 남아 있다. 사후 lint 실패를 임의로 성공 처리하거나 완료 계약에서 검사를 제거하지 않았다. 권한 문제가 해결돼도 전체 lint가 실패하면 현재 workflow의 verify·close는 완료되지 않는다.

중앙 정책 작업에서 서로 다른 host의 child→parent 병합에 필요한 Git 소유권 계약과 실행 주체를 지원해야 한다. 재현 근거는 source 담당 host 검사와 target claim 검사, 같은 host·role만 허용하는 인계 구현이다. 정책을 고칠 경우 이 교차 host 사례와 권한 없는 assignment의 거부를 회귀 테스트로 확인한 뒤 audit·새 inject 세션을 사용한다. 현재 프로젝트 세션은 중앙 정책·claim·branch metadata를 직접 수정하지 않는다.

소스·테스트 commit은 보존돼 있다. 다음 담당은 이 문서와 handoff를 읽고 실제 HEAD·claim을 재확인해야 한다. 새 정책 또는 HEAD 변경 뒤에는 기존 finish SHA를 그대로 승인하지 말고 적용 가능한 계약을 다시 확인한다.
