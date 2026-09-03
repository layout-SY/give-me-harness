# Grill Me 검토

## 1. 검토 목적

이번 변경은 문서 구조, 권한, Git lifecycle과 세 host runtime을 동시에 바꾸므로 “구현이 동작하는가”만으로는 충분하지 않다. 이 문서는 설계가 특정 현재 관행이나 이미 선택한 구현을 정답으로 전제하지 않았는지, 더 단순한 대안이 있었는지, 안전 장치가 협업 자체를 과도하게 막지는 않는지를 중립 질문으로 압박 검토한다.

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부
- [x] “Claude=UI, Codex=Logic”이라는 현재 운영 관행을 전제로 하지 않음
- [x] 사용자 요구와 에이전트 제안을 구분함
- [x] 안전성을 이유로 모든 작업을 무조건 차단하는 결론을 피함
- [x] 자동화 편의를 이유로 복구 어려운 명령을 허용하지 않음
- [x] 현재 변경의 결함과 장기 개선 제안을 분리함
- [x] 측정하지 않은 성능·효율 향상을 수치로 주장하지 않음

## Neutral Question Flow

이 절은 두 번째 검토 단계인 중립 질문 흐름이다.

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 역할 모델 | 역할을 host에 고정하는 방식과 작업마다 선택하는 방식 중 무엇이 미래 변경에 더 잘 견디는가? | 작업마다 선택하는 방식 | 사용자는 향후 Claude가 Logic·오케스트레이션·전체 구현을 맡을 수 있다고 명시함 | host/model과 독립된 `--role` profile 사용 |
| 공통 진입 | host 문서를 각각 완전 복제하는 것과 중앙 common을 직접 참조하는 것 중 어느 쪽이 독립성과 일관성을 함께 만족하는가? | 중앙 common 직접 참조 | 다른 host adapter가 inject bundle에 없을 수 있고 복제는 drift를 만듦 | common 의미 정본 + self-contained host adapter |
| 문서 중복 | 일부 내용 중복을 모두 제거해야 하는가? | discovery에 필요한 최소 안내는 host에 중복 가능 | host 문서는 공통 경로를 찾아야 하지만 역할 의미 자체는 재정의하면 안 됨 | host 문서는 경로·도구 차이만 설명 |
| role 확인 | 매 요청마다 사용자에게 역할을 물어야 하는가? | inject role이 있으면 반복할 필요 없음 | 역할을 실행문에서 명시하자는 사용자 결정 | 같은 role 범위는 진행, 경계 변경 시 새 session |
| role 강제 | 지금 role 침범 hook을 만들어야 하는가? | 현재는 만들지 않음 | 사용자가 먼저 prompt 계약으로 운영하고 실제 사례 후 수정하길 원함 | telemetry·사례 축적 후 별도 결정 |
| 산출물 수 | 모든 owner 작업에 8종이 필요한가? | 현재 공통 계약상 필요 | 사용자가 OpenCode의 8종을 명시적으로 공통 기준으로 지정 | owner 8종, contributor handoff 분리 |
| portfolio | OpenCode 템플릿을 그대로 쓸 것인가, Claude 사례 구조를 쓸 것인가? | Claude 사례 구조 | 사용자 요구이며 문제·대안·기술 목적·결과를 더 재현 가능하게 기록 | 이름은 8종, 내용은 Claude prompt 구조 |
| legacy hook | 공통 guard를 먼저 실행하면 legacy를 남겨도 되는가? | 안 됨 | Codex는 matching hook을 모두 실행하고 deny 하나가 전체 차단 | 기능 흡수 후 legacy 파일·등록 제거 |
| hook 범위 | 공통 guard가 legacy의 모든 기능을 실제로 포함하는가? | 승인·skill·탐색·mutation·Stop 기능을 포함 | 함수·이벤트·테스트를 항목별 비교함 | 중앙 audit에서 기능 marker와 legacy 부재를 함께 검사 |
| dirty 상태 | 기준 worktree를 먼저 clean하게 만들어야 하는가? | 독립 작업이라면 불필요 | 타 세션 dirty의 commit/stash는 소유권 침범 | 승인 parent commit에서 isolated worktree 생성 |
| child 의존성 | parent에 미커밋 변경이 있어도 child worktree를 만들 수 있는가? | 만들 수는 있지만 필요한 변경이 빠지므로 허용하면 안 됨 | worktree는 branch ref의 commit에서 시작 | parent owner의 commit 또는 handoff 후 child 생성 |
| worktree 빈도 | 모든 작업마다 새 폴더와 새 세션이 필요한가? | 아님 | CLOSED+clean이면 같은 세션에서 다음 task 가능 | 미완료 병행·dirty·사용 중인 경우만 격리 |
| proposal 승인 | 구현 계획 승인과 branch SHA 승인을 한 번에 받을 수 있는가? | proposal 생성 전에는 정확한 SHA가 없어 분리해야 함 | digest는 canonical proposal output 후에만 존재 | proposal 출력 뒤 독립 prompt로 전체 SHA 승인 |
| SHA 종류 | Git parent SHA와 proposal SHA를 축약해도 되는가? | 안 됨 | parent 계보는 40자리 commit SHA, 계약 식별자는 64자리 SHA-256 | 둘 다 전체 길이만 허용 |
| Git push | 사용자가 “승인”하면 agent가 push해도 되는가? | 안 됨 | 원격 상태 변화이며 사용자가 양도 방식을 명시 | 정확한 명령·대상·영향을 사용자에게 설명하고 직접 실행 요청 |
| hard reset | agent가 정확한 경로를 알면 reset hard를 실행해도 되는가? | 안 됨 | worktree 전체 변경 손실 가능성 | 승인 경로 없이 사용자 전용 |
| parser 실패 | 명령을 해석하지 못하면 허용할 것인가? | 안 됨 | `git -C`가 실제 치명 명령을 숨긴 사례 | fail-closed하고 명시적 명령을 요구 |
| checkout path | `git checkout -- path`를 예외 허용할 것인가? | 의미가 중의적이므로 대체 명령 사용 | branch 전환 오탐 사례가 있고 restore가 의도를 명시 | `git restore ... -- path`만 사용 |
| compound command | branch 전환과 merge를 한 command로 실행할 것인가? | 안 됨 | hook은 실행 전 branch 기준으로 전체 문자열을 판정 | 전환과 merge 각각 독립 실행 |
| 다른 host 로그 | 다른 host/session의 산출물 접근을 모두 막을 것인가? | Read는 허용해야 함 | handoff 복원과 검토에 필요 | Read 허용, mutation·stage·commit 차단 |
| unknown 문서 | 이름을 모르는 파일을 거부할 것인가? | 보존하되 분리 | 진단 기록을 잃지 않으면서 필수 schema와 섞지 않아야 함 | current session의 `unknown/` 사용 |
| shell 산출물 | heredoc으로 빠르게 문서를 만들게 둘 것인가? | 안 됨 | 구조화 경로가 없어 session binding을 신뢰할 수 없음 | host Write/Edit/apply_patch 사용 |
| stderr redirect | 모든 redirect를 mutation으로 볼 것인가? | 안 됨 | `2>&1`, `/dev/null`은 일반적인 진단 패턴 | fd duplication·진단 경로와 실제 repo write를 구분 |
| 완료 책임 | contributor의 handoff가 branch 완료 증거인가? | 아님 | 부분 역할 결과만 보장하며 8종·통합 검증을 포함하지 않음 | owner만 finish/verify/close 수행 |
| merge 실패 | 자동 rollback/rebase로 원상복구할 것인가? | 안 됨 | 추가 계보 변경이 원인을 숨기고 데이터 손실 가능 | source/worktree 보존 후 상태 보고 |
| cleanup | merge 후 항상 worktree를 삭제할 것인가? | 안 됨 | 검증 실패 또는 사후 조사에 필요할 수 있음 | finish proposal에 cleanup이 승인된 경우만 close에서 수행 |
| 소비자 배포 | 중앙 테스트 PASS 직후 자동 sync할 것인가? | 안 됨 | 소비자 파일과 실행 세션에 외부 상태 변화 발생 | diff 제시 후 별도 승인 |

## 3. 핵심 가정 검증

### 가정 A — 공통 문서 한 벌이면 host 독립성이 떨어진다

검토 결과 이 가정은 성립하지 않는다. host 독립성이란 공통 의미를 복제한다는 뜻이 아니라, 해당 host bundle 안에서 공통 정본을 직접 읽을 수 있다는 뜻이다. inject가 `.agent-policy/common/**`를 host bundle에 포함하면 Claude는 Codex adapter가 없어도 독립적으로 동작한다.

### 가정 B — common guard와 legacy hook을 함께 두면 단계적으로 이전할 수 있다

검토 결과 위험하다. 같은 이벤트의 상태 저장 형식이나 승인 문구가 다르면 한쪽은 허용하고 다른 쪽은 거부한다. Codex hook 실행 모델상 하나의 deny가 최종 deny이므로 중복은 단순 비용이 아니라 가용성 결함이다. 기능 동등성을 테스트한 뒤 한 번에 등록을 단일화하는 것이 맞다.

### 가정 C — dirty 기준 폴더가 있으면 어떤 새 branch도 만들면 안 된다

검토 결과 “현재 폴더에서 새 branch를 만드는 것”과 “같은 repository의 clean worktree를 추가하는 것”을 구분해야 한다. 전자는 dirty를 끌고 가므로 막아야 하지만, 후자는 index와 working directory가 독립적이므로 승인된 parent commit 기반 독립 작업에 적합하다.

### 가정 D — 사용자의 일반 승인 문구는 모든 Git 동작을 허용한다

검토 결과 승인 범주를 분리해야 한다. 구현 계획 승인, 정확한 shell command 실행 승인, branch proposal SHA 승인, finish proposal SHA 승인, 사용자 전용 명령은 서로 다른 권한이다. 특히 push/hard reset은 어떤 agent approval marker에도 연결하지 않는다.

### 가정 E — 다른 host 문서를 못 쓰게 하면 협업도 막힌다

검토 결과 읽기와 쓰기를 분리하면 된다. handoff와 검토 근거는 read-only로 열어두고, 원본 작성자의 host+session만 내용을 바꿀 수 있게 하면 협업과 출처 보존을 동시에 만족한다.

## 4. 반대 시나리오 검토

### 시나리오 1 — Claude가 Logic owner로 시작

- start에서 `--host claude --role logic --responsibility owner`를 지정한다.
- common logic reference와 관련 skill이 bundle에 포함된다.
- 산출물은 `.claude/logs/sessions/...` 8종이다.
- Claude가 Git integrator로 branch 계약에 승인됐다면 index/commit/finish를 수행할 수 있다.
- “Claude=UI” 고정 규칙은 개입하지 않는다.

### 시나리오 2 — Codex가 UI contributor, OpenCode가 owner 통합

- Codex는 UI role과 scope에서 구현하고 자기 `.codex/.../handoff.md`를 작성한다.
- OpenCode는 해당 handoff를 읽을 수 있지만 수정할 수 없다.
- OpenCode owner는 최신 source와 handoff를 다시 확인해 통합하고 `.opencode/...` 8종을 작성한다.
- Git integrator 한 명만 stage/commit/finish를 수행한다.

### 시나리오 3 — sy-main 폴더가 다른 작업으로 dirty

- dirty 파일을 현재 agent가 commit/stash하지 않는다.
- 독립 task proposal에 외부 worktree를 포함한다.
- 승인된 sy-main full SHA에서 clean task branch를 만든다.
- sy-main dirty 작업과 task index는 서로 영향을 주지 않는다.

### 시나리오 4 — proposal 승인 뒤 scope 변경

- canonical JSON bytes가 달라져 SHA-256도 달라진다.
- 이전 승인 digest로 create하면 실패한다.
- 변경된 proposal을 다시 출력하고 사용자의 별도 승인을 받는다.

### 시나리오 5 — `git -C . push`를 command approval로 풀려는 시도

- branch guard가 실제 subcommand를 `push`로 분류한다.
- common guard는 operation approval 확인 전에 사용자 전용 denial을 반환한다.
- `명령 실행 승인`을 기록해도 같은 denial이 유지된다.

## 5. 과도한 복잡성 여부

### 필요한 복잡성

- branch task와 session assignment 분리: 다중 host/role 협업을 표현하려면 필요하다.
- canonical proposal 두 종류: create와 finish가 서로 다른 외부 상태 변경이라 필요하다.
- common event state: legacy 기능을 세 host에서 동일하게 강제하려면 필요하다.
- owner/contributor: handoff와 전체 완료 책임을 구분하려면 필요하다.

### 의도적으로 미룬 복잡성

- role별 파일 의미를 추론하는 새 hook
- 자동 worktree garbage collection
- 자동 rollback/rebase/conflict resolution
- consumer별 기능 policy overlay
- 새 외부 schema validator나 database

## 6. 실패 시 안전성

- Git/parser/runtime contract를 읽지 못하면 허용하지 않는다.
- proposal/finish proposal이 불일치하면 새 승인을 요구한다.
- merge 또는 verify가 실패하면 source branch와 worktree를 보존한다.
- cleanup은 승인 계약 없이는 실행하지 않는다.
- log collection 실패는 원본을 삭제하지 않고 오류만 보고한다.
- 중앙 sync는 자동 후속 단계가 아니다.

## 7. 최종 권고

현재 선택인 “공통 의미 정본 + role-aware inject + 얇은 host adapter + 단일 공통 guard + immutable proposal 기반 worktree lifecycle”을 유지한다. 배포 전에는 중앙 commit을 먼저 고정하고, 별도 승인된 sync 뒤 세 host role 조합에 대한 consumer smoke test를 수행하는 것이 가장 안전하다.

## 8. 결론

검토 결과 현재 설계는 사용자가 요구한 host 역할 가변성, 산출물 출처 보존, dirty 작업 격리와 위험 Git 명령 양도를 동시에 만족한다. 현재 변경을 막는 설계상 FAIL 항목은 없다. 소비자 배포와 legacy 퇴역은 중앙 구현의 완료 조건이 아니라 별도 운영 승인 항목으로 남긴다.
