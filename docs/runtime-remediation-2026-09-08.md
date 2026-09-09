# Hook·assignment·branch 흐름 개선 보고

승인된 개선안 1~5단계에 따라 중앙 원본·테스트·운영 문서를 수정했다. 소비자 파일, 기존 소비자 branch·worktree, 실행 중인 세션은 변경하지 않았다. 중앙 Git commit도 만들지 않았다.

## 책임 구분

| 책임 | 구현 |
| --- | --- |
| 호스트 이벤트 등록 | `adapters/codex/events.json`, `adapters/claude/events.json`, OpenCode plugin |
| 이벤트 진입점·판정 순서 | `policy/guards/managed_policy_guard.py` |
| 도구 입력·경로·관리 파일 판정 | `policy/guards/tool_paths.py` |
| 성공·실패·미확인 결과, host 응답 | `policy/guards/event_protocol.py` |
| 구현 승인·종류별 계약 승인·명령 승인·탐색 근거 | `policy/guards/approval_policy.py` |
| 산출물 검사·assignment 귀속 예약·결과 반영 | `policy/guards/artifact_policy.py` |
| 지속 상태·원자적 쓰기·프로세스 lock·소유권 | `policy/guards/runtime_state.py` |
| Git 명령 분류·계보·scope·상태 판정 | `policy/guards/branch_guard.py` |
| 실제 create·finish·verify·close·preserve·resume | 공통 git-branch-strategy의 `scripts/branch_workflow.py` |
| 세션 준비·원래 bundle 재개 | `lib/agent_policy/injection.py` |
| 로그 출처와 중앙 복사 | `lib/agent_policy/log_mirror.py` |
| 명시적 인계·복구·정책 퇴역 | `lib/agent_policy/assignment.py`, `recovery.py`, `maintenance.py` |

기존 관리 guard의 약 2,270줄을 역할별 모듈로 분리했다. 진입점은 약 520줄이다. 모듈은 격리 Python에서도 같은 bundle 내부의 명시적 경로로만 로드하며, renderer가 모든 runtime 모듈을 세 호스트의 실행 위치에 포함한다.

## 이벤트가 동작하는 시점

| 사건 | 처리 | 상태 변화 |
| --- | --- | --- |
| launcher start | 프로젝트·worktree·잔존 정책 검사, role bundle 준비 | 새 assignment 또는 명시적인 기존 assignment 재개 |
| SessionStart | native session 연결, 현재 작업 초점의 Git context 제공 | 기존 승인 보존 |
| 사용자 prompt | 명시적 구현 승인·철회, 종류별 SHA 승인, 명령 승인 구분 | 일반 질문은 승인 상태 유지; 복수 대기 계약은 SHA 명시 필요 |
| PreTool | 입력 분류 → 관리 경로·산출물·branch·scope·capability·Git 소유권·구현 준비·명령 승인 검사 | 허용 단계에서 실행 예약. 확정 binding은 쓰지 않음 |
| PostTool / 지원되는 실패 callback | 도구 ID와 실행 결과 확인 | 성공만 귀속 확정·탐색 근거 반영. 실패 예약 해제. 미확인은 복구 대상으로 유지 |
| compact / 동일 assignment resume | 기존 bundle·상태와 작업 초점 복원 | 전체 승인 초기화 없음 |
| Stop / idle | 기록된 산출물 출처에서 중앙 로그 수집 | 자동 merge·close·Git add·commit·로그 삭제 없음 |
| 명시적 lifecycle 명령 | 승인 계약과 실제 HEAD·소유권을 실행 위치의 lock 안에서 검사 | 해당 lifecycle 상태만 전이 |

Codex는 Bash의 비정상 종료에도 PostToolUse가 발생할 수 있으므로 결과의 종료 코드를 확인한다. 0.153.2가 종료 코드와 workdir를 생략하는 형식은 같은 도구 호출의 완료 기록으로 보완한다. 실제 원인과 회귀 검증은 [읽기 근거 누락 수정](codex-read-evidence-fix-2026-09-08.md)에 기록했다. apply_patch의 성공 결과도 별도로 처리한다. Claude는 PostToolUse와 PostToolUseFailure를 연결한다. 권한 UI에서 취소된 실행처럼 실패 callback이 없는 경우는 미확인 예약 복구 대상이다. [Codex hooks](https://learn.chatgpt.com/docs/hooks), [Claude hooks](https://code.claude.com/docs/en/hooks)

OpenCode의 before callback은 비동기 Python 검사가 끝날 때까지 기다린다. 비정상 종료·timeout·잘못된 판정 출력은 차단한다. Bash 종료 코드가 없으면 성공 근거로 승격하지 않는다. compact에는 session ID를 전달하고 idle 수집 실패는 로그·알림으로 보고한다. [OpenCode plugin events](https://opencode.ai/docs/plugins/)

## 결함별 변경

| ID | 변경 결과 |
| --- | --- |
| F01 | 중앙 snapshot 읽기를 소비자 source 변경 범위 검사와 분리. 동일 관리 파일의 쓰기는 차단 |
| F02 | OpenCode 검사 오류 시 차단. Python 진입점 의존성 오류·잘못된 JSON도 차단하며 host timeout 전에 내부 제한 시간 8초 적용 |
| F03 | 실패·미확인 결과와 경로를 출력하기만 한 echo는 탐색 근거에서 제외 |
| F04 | 질문·compact·resume 시 승인 보존. task·role·계약 변경과 명시적 철회를 별도로 처리 |
| F05 | 구현, proposal/scope/finish, 실행 명령 승인을 분리. 기존 plan.md 내용 변경과 child의 구현 범위 확대는 구현 재승인 필요 |
| F06 | Codex writable home을 assignment마다 격리. 재개는 원래 native session·home·검증된 bundle 사용 |
| F07 | finish 내부에서 승인된 target worktree 선택 또는 단일 worktree의 안전한 target 전환 |
| F08 | ff-only/merge-commit을 계약에 포함. integration HEAD·source ancestry·merge 부모를 verify와 close에서 검증 |
| F09 | PRESERVED·READY_TO_MERGE·MERGED_VERIFIED의 진단·복구 진입 허용. 일반 source 변경 권한은 ACTIVE에 한정 |
| F10 | assignment의 산출물 이동 출처 기록. 최신 위치 우선 수집, 반복 수집 무변경, cleanup 전 수집 실패 시 worktree 보존 |
| F11 | 같은 host라도 assignment가 다르면 같은 Git worktree의 소유권 공유 불가. target 통합 예약, 명시적 handoff, 종료한 Git 소유권 해제 |
| F12 | pre 예약과 post 확정 분리. 도구 ID별 예약, 중복 결과 방지, 실패 처리와 누락 결과의 명시적 복구 |
| F13 | OpenCode의 기본 status/diff/log/worktree list 조회 허용. 모호한 옵션은 승인 유지; diff --output 등 변경 옵션은 guard에서 차단 |
| F14 | 필수 portfolio binding, overlay digest, 최종 role bundle의 참조 검사, 비활성 hookify 제외, Claude 고정 모델 제거, type alias·page/hook arrow 문서 정리 |

review/orchest는 source를 수정할 수 없고 자기 산출물과 조사를 담당한다. logic/ui/generate는 승인된 branch scope의 source를 수정할 수 있다. Git 권한은 role 이름으로 추론하지 않고 branch의 integrator host와 assignment 소유권으로 검사한다. branch metadata의 역할 목록과 launcher role 이름은 동일한 필드가 아니다.

구현 승인 시 존재하는 귀속 `plan.md`는 파일 해시로 연결한다. 문서가 아직 없으면 대화의 계획 내용을 기계적으로 해시했다고 주장하지 않는다. child의 구현 범위는 승인된 경로 범위에 포함되는지 확인한다. 복잡한 glob의 포함 관계를 증명할 수 없는 경우 재승인이 필요할 수 있다.

## branch·worktree 완료와 복구

finish 계약에는 source/target 전체 HEAD, source/통합 worktree, merge 방식, 검증 argv, cleanup 여부가 포함된다. 구형 V3 ff-only 계약은 기존 권한 범위에서 호환한다. V1/V2 계약을 자동 승격하지 않는다.

성공한 병합의 결과 기록이 누락되면 같은 finish 명령이 실제 Git 결과와 승인된 HEAD·부모 관계를 대조해 기록을 복구한다. verify는 프로젝트에 등록된 정확한 argv만 실행한다. close는 검증 결과 HEAD를 다시 확인하며, cleanup 실패를 CLOSED로 기록하지 않는다. 동일 결과에 대한 verify·close 재시도가 가능하다.

| 상황 | 중앙 명령 | 승인 전 / 승인 후 |
| --- | --- | --- |
| 결과 callback 누락 | `assignment-recover --project <project> --assignment <ID> --call-id <ID> --outcome confirmed|cancelled` | 현재 HEAD·파일 해시·예약·입력을 담은 계약 출력 / 귀속 예약만 확정·해제 |
| 충돌 또는 실패한 ff-only 중단 | `integration-recover --project <project> --finish-file <file> --finish-sha256 <SHA>` | target HEAD·dirty 파일·MERGE_HEAD·통합 예약 검토 / 일치하는 병합만 abort하고 source ACTIVE 복원 |
| 담당 세션 교체 | `assignment-handoff --project <project> --from-assignment <ID> --to-assignment <ID> --handoff-file <file>` | 정확한 Git 소유권·진행 중 통합·handoff 해시 검토 / 같은 host·role의 준비된 assignment로 인계 |
| 소비자 기준 branch의 정책 잔존물 | `maintenance-plan --project <project> --branch task/<name> --worktree <new-path> --host <host>` | 정확한 diff·HEAD·해시·새 V3 worktree 계약 출력 / `maintenance-apply`가 승인한 퇴역 변경만 적용 |

앞의 세 복구·인계 명령은 검토한 SHA를 동일 명령의 `--approved-sha256`으로 지정해야 상태를 바꾼다. 유지보수는 `maintenance-apply --project <project> --plan-file <file> --approved-sha256 <SHA>`로 적용한다. 복구 검토 후 실제 상태가 바뀌면 기존 승인을 재사용하지 않는다.

handoff는 구현 승인과 다른 assignment의 산출물 쓰기 권한을 복제하지 않는다. 인계 중단 시 journal이 양쪽 assignment를 차단하며 승인된 동일 계약을 재실행해 마무리한다. 새 target은 `start --resume-assignment <target-ID>`로 준비된 실행을 시작한다. 실제 native session이 아직 없으면 native resume 인자를 붙이지 않는다.

## 검증과 한계

수정 전 실패 재현 로그와 수정 후 테스트를 남겼다. F10/F11/overlay digest는 중앙 Git HEAD의 이전 구현을 임시 환경에서 실행해 기존 실패를 추가 확인했다. 소비자 Git history나 `archive/**`를 정책 원본으로 사용하지 않았다.

기본 검사 외에 다음을 검증했다.

- 실제 launcher bundle·assignment를 사용하는 세 호스트의 `proposal → 승인 → create → 구현·산출물 → commit → finish → verify → close` 이벤트 재생
- Codex의 별도 worktree 전체 흐름과 그 위치의 로그 수집
- 병렬 sibling의 ff-only/merge-commit 통합, 승인 후 HEAD 변경 거부, 충돌·검증 실패 시 보존
- 같은 산출물의 동시 최초 쓰기, 같은 host의 Git 소유권 충돌, 인계 중단·재실행
- 실패·미확인·중복 callback, plan 변경, 여러 승인 대기 계약, child scope 확대, 명령 workdir 변경
- cleanup 전 로그 수집 실패, 병합 성공 직후 기록 유실, verify·close 재시도
- 실제 OpenCode의 inject config·plugin 로딩과 최종 보호 명령 권한

Git 검사 성능은 같은 임시 V3 저장소의 `active_branch_denial`을 각 5회 측정했다. Git subprocess 호출은 매회 37회에서 21회로 감소했다. 실행 시간 중앙값은 655.79ms에서 375.37ms로 감소했다. 전체 대화 지연 측정은 아니며, 이벤트를 넘어 HEAD·dirty를 캐시하지 않는다.

Codex·Claude에서 모델을 실제로 호출하는 대화 세션은 실행하지 않았다. 전체 lifecycle 검증은 실제 Git·Python guard·launcher bundle에 host payload를 재생한 테스트다. OpenCode는 설치된 CLI의 실제 config 로딩도 확인했다. 최종 설정에는 사용자 전역 `oh-my-openagent` plugin과 기본 agent가 함께 있었다. 중앙 설정·정책이 이 사용자 전역 plugin의 모든 동작을 통제한다고 보장하지 않는다.

hook이 관찰하지 않는 후속 shell 입력, 미등록 MCP 도구, 별도로 연결하지 않은 native child session은 이 검증 범위 밖이다. 다른 native session은 같은 assignment의 권한을 자동 상속하지 않는다. OS sandbox, 사용자 직접 실행, 문서 내용의 의미적 타당성은 별도의 경계다.

## 실제 소비자 적용 상태

`bin/agent-policy audit`에서 중앙 계약과 admin-ui는 통과했다. user-ui의 현재 checkout은 `package.json`, `README.md` 두 잔존 참조로 실패한다. 현재 V1 branch는 `task/reservation-list-handoff`이다.

추가 확인 결과 user-ui의 **sy-main에는 퇴역 정책 정리가 이미 반영되어 있다**. 따라서 기준 branch에 새 퇴역 diff를 만들려는 maintenance-plan은 변경 없음으로 거부했다. 이 경우 필요한 작업은 기존 V1 기능 변경을 최신 sy-main 기반의 새 V3 task로 이관하는 것이다.

검토용 이관 패치는 다음 3개 기능 파일만 포함한다. 기존 checkout의 23개 정책 파일 삭제 상태와 로그는 그대로 보존했다.

- `src/features/meeting-reservation/ui/MeetingReservationListPage.tsx`
- `src/features/meeting-reservation/ui/parts/ReservationCard.tsx`
- `src/features/meeting-reservation/ui/parts/meeting-reservation-parts.css`

검토 기준 sy-main HEAD는 `933a07f51410af29f86c454e8c1918d2cc445e87`, 기존 task HEAD는 `4d6110e75b8fcf55838d4dd9998ebc864d2c078c`이다. 패치 SHA-256은 `fa723939d08d3223c9736be594c9d32e9731644d1d96a3a841704e12514c887d`이며, 기준 파일의 임시 사본에서 `git apply --check`가 통과했다. 이는 기능 테스트 통과나 V3 branch 생성 승인을 뜻하지 않는다.

실제 소비자 이관은 승인된 개선안 6단계의 별도 대상이다. 새 V3 branch·scope·worktree 계약, 이관 diff 검토·기능 검증, 활성 세션 handoff와 새 inject 실행이 남아 있다. 기존 V1 metadata 덮어쓰기나 소비자 파일 변경은 수행하지 않았다.

## 최종 실행 결과

| 검증 | 결과 |
| --- | --- |
| `python3 -m unittest discover -s tests -v` | **164개 통과**, 504.025초 |
| `python3 tests/smoke_opencode_plugin.py` | 설치된 OpenCode의 실제 inject config·plugin·보호 명령 권한 **통과** |
| `bin/agent-policy audit` 중앙 계약 | **PASS** |
| 같은 audit의 admin-ui | **PASS**, 260개 bundle 파일 |
| 같은 audit의 user-ui | **FAIL**, 현재 V1 checkout의 `package.json`, `README.md` 잔존 참조 2건 |
| `git diff --check` | **통과** |
| user-ui 이관 패치의 기준 파일 사본에서 `git apply --check` | **통과**, 소비자 적용 없음 |

전체 audit의 종료 코드는 user-ui 항목 때문에 1이다. 중앙 테스트 통과를 소비자 이관·배포 완료로 해석하지 않는다.

실행 로그는 `/private/tmp/asan-policy-complete-suite.log`, `/private/tmp/asan-policy-complete-audit.log`에 두었다. 성능 측정은 `/private/tmp/asan-policy-git-benchmark.json`, 기존 구현의 추가 실패 재현 결과는 `/private/tmp/asan-policy-extra-baselines.json`에 기록했다. 소비자 검토용 패치는 `/private/tmp/asan-user-ui-v3-feature-migration.patch`, 기준 HEAD·패치 해시·검사 결과는 `/private/tmp/asan-user-ui-v3-migration-review.json`이다.
