# 검토 로그

## 1. 현재 변경 판정

**PASS — 중앙 원본 구현과 자동 검증 기준을 충족함.**

이 판정은 중앙 저장소 변경에 한정한다. 소비자 프로젝트 sync, legacy retire와 실행 중 세션 재시작은 아직 수행하지 않았으므로 배포 완료 판정은 아니다.

## 2. 검토 목적

이번 검토는 다음 두 종류의 실패를 동시에 찾는 데 초점을 맞췄다.

1. 기존 host별 문서를 제거하는 과정에서 필요한 역할·workflow·산출물 의미가 사라지는 의미 회귀
2. Git parser, hook event, session binding과 worktree lifecycle에서 위험한 명령이 허용되거나 정상 작업이 잘못 차단되는 실행 회귀

## 3. 검토 범위

### 문서·역할

- 공통 진입 문서와 host adapter의 의존 방향
- `logic|ui|orchest|review|generate` role profile
- Planner, Publisher, Implementer/Generator, Refactorer, Watcher, Evaluator, Harness 책임
- feature/refactor/hybrid/audit/retry/escalation workflow
- handoff, 파일 소유권과 Git integrator 계약

### 산출물

- owner 8종과 contributor handoff 구분
- Claude portfolio prompt 구조 보존
- 공통 union schema의 역할별 필드 보존
- cross-host/session read-only와 current-session write
- unknown 문서 위치와 host 미상 root
- Stop의 dirty+committed source 변경 감지

### hook·runtime

- Codex legacy Python hook 기능 대 공통 guard 기능
- 세 host의 UserPrompt/PreTool/PostTool/Stop 연결
- Codex native deny payload와 Claude/OpenCode exit code
- exact command approval와 implementation approval 상태 분리
- proposal full SHA approval binding

### Git·branch

- global option, alias, nested shell parsing
- never-agent command의 승인 불가
- checkout path와 compound branch/merge 판정
- immutable create/finish proposal
- dirty isolated worktree
- scope, integrator, parent/target lineage
- preserve/resume와 owner-only finish/verify/close

### renderer·inject·배포

- 공통 파일의 세 host 동일 렌더
- role별 bundle 선택
- external worktree 절대 runtime path
- project·branch·task·session-dir validation
- 중앙 audit와 consumer diff

## 4. 점검 결과

| 점검 항목 | 판정 | 근거 |
| --- | --- | --- |
| 공통 정본 독립성 | PASS | `.agent-policy/common/AGENT_POLICY.md`를 모든 adapter가 직접 참조하고 Codex 경유 없음 |
| host 역할 고정 제거 | PASS | 공통·adapter Markdown에서 금지 문구 자동 감사, 역할은 role profile로 선택 |
| 기존 Claude 역할 의미 보존 | PASS | 역할별 책임·금지·종료·retry 의미를 pipeline/workflow references로 이동 |
| 기존 Claude schema 의미 보존 | PASS | Planner~Harness role-specific 필드를 common union schema에 포함, audit marker 추가 |
| OpenCode 8종 보존 | PASS | runtime registry required 목록과 세 host template bytes 동일성 테스트 |
| Claude portfolio 형식 보존 | PASS | 사례 metadata와 여섯 필수 section을 source audit에서 검사 |
| contributor 책임 경계 | PASS | handoff/preserve만 허용, finish 계열은 owner-only 테스트 |
| 다른 host/session Read | PASS | read tool은 허용되는 회귀 테스트 |
| 다른 host/session Write | PASS | structured write와 Git stage가 모두 차단되는 테스트 |
| unknown 문서 | PASS | current session의 `unknown/`만 허용하고 root 오배치 차단 |
| legacy Codex hook 제거 | PASS | adapter hook directory 삭제와 `hooks.base.json={"hooks":{}}` audit |
| common guard 기능 포괄 | PASS | user-prompt, post-tool, pre-tool, documentation-stop 함수·등록·동작 테스트 |
| `functions.exec` alias | PASS | 세 host에서 shell alias가 공통 guard를 통과하는 회귀 테스트 |
| `git -C . reset --hard` | PASS | 세 host 모두 사용자 전용 denial, command approval 후에도 denial |
| `git -C . push` | PASS | 세 host 모두 사용자 전용 denial, command approval 안내 없음 |
| nested/alias push | PASS | `sh -c`, Git alias 문자열도 fail-closed |
| stale guard 무시 | PASS | inject snapshot runtime만 사용하며 `FULL_SHA_PATTERN` 누락 fixture를 거부 |
| proposal 불변성 | PASS | purpose/role/scope/reason/worktree를 포함한 SHA-256 변경 테스트 |
| parent SHA 길이 | PASS | 축약 SHA는 40자리 전체 SHA 안내와 함께 거부 |
| dirty isolated create | PASS | 기준 dirty 유지, 별도 worktree clean branch 생성 테스트 |
| V3 lifecycle | PASS | preserve/resume, finish/verify/close 상태 전이 테스트 |
| target 검증 제한 | PASS | 등록된 lint/test/build argv만 허용, shell wrapper 차단 |
| Python cache 제외 | PASS | renderer/source digest에서 `__pycache__`, pyc 제외 테스트 |
| 중앙 source 계약 | PASS | `bin/agent-policy audit` central-contract PASS |
| 소비자 무결성 | PASS | admin-ui/user-ui 각각 183 managed files audit PASS |

## 5. 자동 테스트 결과

### 전체 테스트

```text
python3 -m unittest discover -s tests -v
Ran 89 tests in 76.840s
OK
```

포함된 주요 test group:

- `BranchGuardTests`: proposal, isolated worktree, scope, lineage, lifecycle, dangerous Git
- `GuardTests`: managed path, session artifact, common readiness, command approval, Stop
- `InjectionTests`: role bundle, host home/plugin, worktree validation, no consumer mutation
- `LogMirrorTests`: host channels, unknown, incremental no-delete collection
- `RenderingTests`: common source invariant, template bytes, host-neutral 문구, hook schema
- `SyncTests`: deterministic render, manifest, source digest, common hook 실제 실행

### 중앙·소비자 감사

```text
[central-contract] PASS
[admin-ui] PASS (183 managed files)
[user-ui] PASS (183 managed files)
```

### 소비자 예상 diff

두 프로젝트 모두 다음으로 동일했다.

```text
current=false
add=99
change=82
stale=0
legacy=11
manifest missing
```

이 결과에서 `current=false`와 manifest missing은 중앙 변경을 아직 sync하지 않은 배포 전 상태를 뜻한다. `stale=0`은 현재 manifest가 관리하던 파일 중 새 renderer가 버려진 stale 경로로 판정한 것은 없다는 뜻이다. legacy 11개는 별도 retire 조건을 검토해야 한다.

### patch 품질

```text
git diff --check
PASS
```

## 6. 구현 중 발견된 검토 이슈

### 이슈 A — preserve test fixture 순서

- 증상: `test_preserve_requires_handoff_and_contributor_cannot_finish`가 handoff 문구 대신 session directory 귀속 누락 문구를 받아 실패했다.
- 원인: guard가 잘못된 것이 아니라 테스트가 실제 start 계약인 `ASAN_SESSION_DIR` 없이 preserve를 먼저 호출했다.
- 조치: 구현을 완화하지 않고 fixture에 현재 Claude session directory를 선언했다.
- 재검증: 해당 테스트와 전체 suite PASS.

### 이슈 B — 초기 공통 schema의 세부 역할 필드 유실 가능성

- 증상: 공통 schema가 일반 필드 중심이면 기존 Claude Planner/Publisher/Generator/Refactorer/Watcher/Evaluator/Harness 출력 계약이 삭제될 수 있었다.
- 원인: host 고정 문구 제거와 역할 의미 제거를 혼동할 위험.
- 조치: 삭제 전 schema를 역할별로 재추출해 union schema와 템플릿에 복구하고 audit에 필드 불변식을 추가했다.
- 재검증: source contract audit PASS.

### 이슈 C — tool alias를 통한 guard 누락 가능성

- 증상: `functions.exec`를 shell로 정규화하지 않으면 동일 Git 명령이 도구 이름에 따라 다르게 판정될 수 있었다.
- 원인: host별 tool naming 차이.
- 조치: normalized tool name과 shell tool 집합을 공통화했다.
- 재검증: 세 host reset/push 테스트 PASS.

### 이슈 D — external diagnostic redirect 오탐

- 증상: `2>&1`, `2>/dev/null`이 산출물 shell write 오류로 차단될 수 있었다.
- 원인: shell token 중 redirect를 모두 저장소 파일 mutation으로 취급.
- 조치: fd duplication, `/dev/null`, 저장소 밖 진단 경로를 구분하고 실제 repo target만 scope 검사한다.
- 재검증: harmless redirect와 managed target redirect 테스트 PASS.

### 이슈 E — trusted workflow source 구분

- 증상: inject script와 sync-deployed script 중 한 경로만 신뢰하면 정상 workflow가 차단되거나 stale consumer 파일을 신뢰할 수 있었다.
- 조치: inject는 현재 bundle의 exact script, sync는 common deployed exact script만 인정하고 host legacy path는 배제했다.
- 재검증: stale consumer fixture와 trusted create/integrator 테스트 PASS.

## 7. 발견 사항

| 심각도 | 경로·상태 | 발견 사항 | 필수 조치 |
| --- | --- | --- | --- |
| 정보 | admin-ui, user-ui | 새 정책이 아직 배포되지 않아 `current=false`, manifest missing | 별도 sync 승인 전에는 변경하지 않음 |
| 정보 | consumer legacy | 각 프로젝트 legacy 11개, 그중 기존 Codex test hook hash mismatch 표시 | retire 전 audit SHA와 실제 파일을 재검토 |
| 정보 | 현재 중앙 branch | V3 도입 전 생성되어 V3 metadata가 없음 | 이번 branch에 가짜 metadata를 소급 기록하지 않음 |
| 정보 | role enforcement | 역할 경계는 prompt 계약이고 별도 semantic hook 없음 | 실제 침범 사례 발생 시 후속 검토 |
| 정보 | consumer session | sync 뒤 기존 session은 오래된 snapshot을 유지할 수 있음 | handoff 후 새 session 시작 |

## 8. 범위 외 변경 확인

- 소비자 저장소에 sync를 실행하지 않았다.
- 소비자 파일을 직접 수정하지 않았다.
- push, reset hard, clean, update-ref를 실행하지 않았다.
- 기존 중앙 수집 로그의 내용을 수정하지 않았다.
- 사용자 소유의 다른 작업 파일을 restore/stash하지 않았다.
- 폐기된 외부 정책 저장소, 백업 또는 `asan-harness`를 참조하지 않았다.

## 9. 반복 문제와 escalation

- `retry_count`: 1 — preserve 테스트 fixture 수정 후 통과
- `repeat_issue_detected`: false
- `escalation_needed`: none
- 사용자 선택이 남은 항목: 소비자 sync, legacy retire, 세션 재시작 시점

## 10. 최종 결론

중앙 정책 변경은 사용자가 지정한 host-neutral 역할, role-aware inject, 공통 8종, Claude portfolio 구조, legacy hook 단일화, cross-session read-only와 Branch Contract V3 요구를 충족한다. 크리티컬 명령은 세 host와 shell alias에서 승인 불가 사용자 전용으로 검증됐다. 중앙 commit 대상으로 승인할 수 있으며, 소비자 배포는 별도 승인 단계로 유지한다.

## 11. 후속 코드 리뷰 — worktree-aware guard

### 11.1 해결된 P0/P1 항목

| 심각도 | 기존 상태 | 영향 | 수정 후 판정 |
| --- | --- | --- | --- |
| P0 | task cwd에서 `git -C <primary>` add가 task branch 기준으로 허용 | `sy-main` primary index 직접 변경 | invocation target branch를 재평가해 차단 |
| P0 | primary Git directory와 task work tree 조합을 구분하지 않음 | primary index/HEAD를 task 경로처럼 위장 | absolute Git directory 일치 검사로 차단 |
| P1 | sync hook이 cwd의 ignored runtime을 실행 | 외부 worktree에서 모든 tool fail-closed | configured primary 절대 runtime 사용 |
| P1 | primary cwd에서 `git -C <task>` add가 base branch로 오탐 | 승인된 isolated task 작업 불가 | task target에서 scope·integrator 검사 후 허용 |
| P1 | session state hash에 worktree root 포함 | 같은 session 이동 시 승인·binding 유실 | Git common directory identity로 통합 |
| P1 | structured absolute target이 event root 밖이면 검사 누락 | 외부 worktree scope 또는 managed file 우회 | target Git root를 찾아 같은 repo에서 재검사 |
| P1 | unapproved scratch switch 후 commit 복합 명령 허용 가능 | 승인 계보 밖 commit 생성 | switch target 계약과 compound Git 작업 차단 |
| P1 | `.git/**`가 scope `.`에 포함될 수 있음 | config/ref/index 제어 파일 직접 편집 | scope보다 우선하는 제어 경로 차단 |

### 11.2 정확성 검토

- `GitInvocation`은 subcommand와 target root를 한 객체로 묶어 이후 함수가 event root를 실수로 재사용할 가능성을 낮춘다.
- `same_git_repository()`는 경로 prefix가 아니라 Git common directory를 비교하므로 primary와 linked worktree는 같게, unrelated repository는 다르게 판정한다.
- V3 metadata에 worktree가 있으면 `active_branch_denial()`이 실제 top-level과 정확히 일치하는지 확인한다. direct branch 계약의 빈 worktree는 기존 primary workflow와 호환된다.
- Git ownership 검사는 invocation마다 `changed_paths`·`staged_paths`를 읽으므로 `git -C`가 다른 index를 가리킬 때 artifact path도 그 index 기준이다.
- binding record의 이전 형식에는 `worktree`가 없으므로 현재 root fallback이 적용된다. 새 형식은 절대 worktree를 기록하되 같은 Git common repo인지 재검증한다.
- runtime policy root는 inject bundle env를 우선하고 sync는 실행 중인 guard 파일의 primary 위치에서 도출한다. event Git root와 정책 파일 root를 혼동하지 않는다.

### 11.3 보안·안전 검토

- never-agent 명령은 repository context parsing 전 text/argv 양쪽에서 차단돼 `git -C`, 외부 저장소 또는 malformed option으로 승인 경로에 들어가지 않는다.
- unsafe global option은 조회 명령에는 불필요한 차단을 늘리지 않되 mutation에서는 fail-closed한다.
- `GIT_DIR/GIT_WORK_TREE` 환경 변수는 shell prefix에서만 판단한다. commit message 안의 같은 문자열을 환경 override로 오인하지 않도록 Git token 앞 prefix만 검사한다.
- `cd`는 command segment의 실행 명령 위치를 확인하므로 `git commit -m cd` 같은 인자를 directory change로 오인하지 않는다.
- 다른 저장소를 향한 structured write는 scope가 넓어도 허용하지 않는다.
- symlink resolve 뒤 repository membership을 검사해 repo 내부 symlink를 통한 외부 파일 mutation을 허용하지 않는다.

### 11.4 구현 중 회귀와 처리

1. `dataclass`가 동적 exec module에서 실패한 문제는 targeted branch test 전부가 setup 단계에서 실패해 즉시 드러났다. runtime loader를 바꾸는 대신 standalone guard 호환성이 높은 `NamedTuple`로 교체했다.
2. helper 삽입 위치 오류로 `repository_relative()` body가 끊긴 문제는 artifact Write가 binding되지 않고 implementation gate로 넘어가는 증상으로 확인했다. 함수 body 복원 후 관련 7개 test를 우선 재실행하고 전체 suite를 돌렸다.
3. 초기 테스트가 top-level 일치만 검증한 뒤 추가 위협 모델에서 Git directory/worktree mismatch를 발견했다. 코드와 테스트를 같은 turn에서 보강했다.

이 세 문제는 모두 중앙 source 내부의 미커밋 단계에서 발견됐고 소비자 sync나 외부 Git mutation 없이 해결됐다.

### 11.5 문서 일관성 리뷰

다음 문구를 전수 검색했다.

- cwd 기반 `ROOT=$(git rev-parse ...)` hook: 제거됨.
- 격리 worktree 생성 즉시 무조건 새 세션: 제거됨.
- CLOSED 후 같은 session 전환: 공통 template, skill, 상세 전략에 유지됨.
- PRESERVED 병행 시 별도 worktree·session: 유지됨.
- role을 특정 host에 고정하는 표현: 새 변경에 추가되지 않음.

### 11.6 잔여 위험

- shell function이나 변수로 `git` executable 이름 자체를 숨기는 모든 문법을 해석하지는 않는다. 기존 nested/unparsed fail-closed와 structured tool 원칙을 유지한다.
- sync worktree에 host 설정 파일 자체가 없는 소비자 구성은 host가 hook을 로드하지 못할 수 있다. 이번 수정은 이미 로드된 sync hook의 runtime anchor 문제를 해결하며, host 설정 배치 방식 변경은 별도 배포 설계 범위다.
- worktree 경로가 외부 프로세스에 의해 삭제·재생성되면 Git common directory와 V3 metadata 검사가 실패해 작업을 차단한다. 자동 fallback은 하지 않는다.
- target integration의 finish→verify→close 상태 기계는 기존 V3 계약을 유지했다. 자동 rollback이나 primary dirty 정리는 여전히 하지 않는다.

## 12. 후속 리뷰 결론

핵심 변경은 허용 범위를 넓히는 예외가 아니라 판정 좌표를 event cwd에서 실제 Git target으로 옮긴 것이다. 정상 primary→task 작업과 위험 task→primary 작업이 서로 반대 결과를 갖는 회귀 테스트가 있으며, session common identity와 CLOSED rebind까지 end-to-end로 연결했다. 현재 발견된 P0/P1 항목은 중앙 source 기준으로 해소됐다.

## 13. 검증 후 리뷰 상태

96개 전체 test, 중앙 contract audit와 두 소비자 183-file audit가 모두 통과했다. 최종 consumer diff는 각 add 99/change 82/legacy 11/manifest missing이며 자동 sync하지 않았다. 코드 리뷰 기준 차단 이슈는 없고, 실제 host smoke와 소비자 배포만 별도 운영 승인 항목으로 남는다.

## 14. 사용 가이드 리뷰

### 14.1 정확성

- agent-policy start의 mode, host, role, worktree, branch, task, responsibility, session-dir 인자를 실제 help와 대조했다.
- branch_workflow.py의 proposal/create/preserve/resume/finish-proposal/finish/verify/close 인자를 실제 parser와 대조했다.
- scope·role·verify-command 반복 사용이 구현과 일치한다.
- inject는 sync 불필요, 새 launcher 실행 필요라는 현재 bundle 수명 주기를 정확히 설명한다.
- sync absolute runtime과 host 설정 배치의 차이를 숨기지 않는다.

### 14.2 역할 중립성

예시는 특정 host가 특정 역할을 소유한다고 규정하지 않는다. Claude-ui와 Codex-logic 같은 현재 관행은 규칙으로 쓰지 않았고, 어떤 host도 logic/ui/orchest/review/generate를 선택할 수 있다고 명시했다.

### 14.3 안전성

- dirty primary의 기존 변경에 대한 commit·stash·reset·restore를 권하지 않는다.
- raw branch create, raw V3 merge와 worktree remove를 권하지 않는다.
- Git push, reset hard, clean, update-ref를 사용자 전용으로 유지한다.
- 다른 host·session 산출물은 read-only라고 명시한다.
- Bash heredoc 산출물, 축약 SHA, checkout path 복원과 전환+merge 복합 명령의 교정 방법을 포함한다.

### 14.4 문서 품질

README 상대 링크와 사용 가이드의 전략 문서 상대 링크를 확인했다. fence 개수는 짝수이며 whitespace 오류가 없다. code block 밖에서 HTML로 오인될 수 있는 angle placeholder는 제거하거나 inline code로 보정했다.

판정: 사용 가이드에 정책을 완화하거나 host 역할을 고정하는 차단 이슈는 없다.
