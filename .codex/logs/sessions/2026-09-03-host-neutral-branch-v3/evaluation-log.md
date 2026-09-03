# 평가 로그

## 1. 현재 판정과의 경계

현재 중앙 변경의 정확성·완료 여부는 `review-log.md`에서 PASS로 판정했다. 이 문서는 현재 diff를 다시 승인하지 않고, 구조 변경이 장기 운영에 미치는 영향, 남아 있는 기술 부채, 선택하지 않은 대안과 후속 backlog를 평가한다.

## 2. 진단 요약

이번 문제의 표면적인 증상은 branch create 실패, SHA 불일치, dirty worktree 차단과 Git 명령 오판이었다. 그러나 공통 원인은 다음 세 경계가 명확하지 않았다는 데 있다.

1. **host와 role 경계**: 실행 프로그램 이름이 작업 책임을 암시했다.
2. **branch와 session 경계**: 장기 task 계약과 현재 작업자의 산출물 책임이 하나의 metadata에 섞였다.
3. **공통 정책과 host hook 경계**: 같은 안전 규칙을 공통 guard와 Codex legacy hook이 서로 다른 상태로 실행했다.

V3는 이 경계를 분리함으로써 개별 예외를 계속 추가하는 방식 대신 정책의 의존 방향을 재설계했다.

## 3. 장기 관찰 사항

### 3.1 host와 역할의 분리

장점:

- Claude, Codex, OpenCode를 교체하거나 역할을 역전해도 공통 역할 문서를 수정할 필요가 없다.
- 한 host가 전체 구현을 맡는 경우 `generate`, 기획만 맡는 경우 `orchest`처럼 시작 시 context를 명시할 수 있다.
- model 선택은 host와 role과 독립적으로 유지돼 모델 교체가 정책 권한 변경으로 이어지지 않는다.

비용:

- 운영자가 start 시 올바른 role을 선택해야 한다.
- 한 세션에서 role을 바꾸려면 새 session을 시작하거나 역할 재확인이 필요하다.
- role별 파일 의미는 현재 prompt 계약이므로 agent가 이를 어겼을 때 runtime이 모든 경우를 추론하지는 못한다.

평가:

현재 사용 패턴과 미래 확장성을 고려하면 비용보다 장점이 크다. 다만 role 목록을 지나치게 세분화하면 start 인자와 문서 선택 복잡도가 커지므로 실제 업무 유형이 축적되기 전에는 현 5개 profile을 유지하는 것이 좋다.

### 3.2 공통 정본과 host adapter

장점:

- 역할·workflow·산출물 의미가 한 source에서 렌더돼 drift가 줄어든다.
- host adapter가 없어도 common bundle만 있으면 정책 의미를 이해할 수 있다.
- 새 host를 추가할 때 native event와 파일 위치만 연결하면 된다.

비용:

- 공통 문서 한 변경이 모든 host에 영향을 준다.
- host 고유 기능을 common 의미로 잘못 끌어올리면 추상화가 오염될 수 있다.
- template을 여러 native 경로로 렌더하므로 소비자 managed 파일 수가 크게 증가한다.

평가:

공통 정본에는 “무엇을 지켜야 하는가”만, adapter에는 “그 host에서 어떻게 실행하는가”만 두는 의존 규칙을 audit로 지속해야 한다. host-specific event 이름이나 tool payload를 common contract에 직접 넣지 않는 것이 중요하다.

### 3.3 공통 guard 단일화

장점:

- 동일 세션의 승인·skill·탐색·산출물 상태가 한 곳에서 판정된다.
- Codex만 강했던 readiness gate를 Claude와 OpenCode에도 동일하게 적용한다.
- 중복 hook의 상충 deny가 사라진다.

비용:

- `managed_policy_guard.py`의 책임과 코드 크기가 커졌다.
- 한 구현의 버그가 세 host에 동시에 영향을 줄 수 있다.
- host event payload 차이를 normalization 계층이 계속 흡수해야 한다.

평가:

단일 정책 판정점은 맞지만 장기적으로는 한 파일 안에서 artifact, branch delegation, readiness, command approval 모듈을 내부적으로 더 분리할 여지가 있다. 다만 지금 즉시 파일을 여러 개로 쪼개면 inject runtime 로딩·무결성 surface가 다시 늘어난다. 먼저 실제 유지보수 빈도와 결함 위치를 관찰한 뒤 분리하는 편이 낫다.

### 3.4 immutable proposal

장점:

- 사용자에게 보여준 계약과 실제 실행 인자가 동일하다.
- purpose, role, scope, reason, worktree 같은 의미 필드가 승인 뒤 바뀌면 digest가 달라진다.
- 긴 인자를 create/finish에서 다시 입력하지 않아 오타와 축약 SHA 문제가 줄어든다.

비용:

- proposal과 승인 prompt가 분리되어 상호작용 단계가 늘어난다.
- Git common directory에 proposal record가 누적된다.
- 사용자가 SHA만 보고 내용 확인을 생략하면 암호학적 동일성은 있어도 의미적 동의가 약해질 수 있다.

평가:

proposal 출력은 SHA뿐 아니라 핵심 필드를 사람이 읽을 수 있게 계속 표시해야 한다. 향후 proposal 목록/만료 조회 CLI가 필요할 수 있지만 자동 삭제는 감사 가능성을 해치므로 신중해야 한다.

### 3.5 worktree 격리

장점:

- 기준 폴더의 dirty 파일과 index를 건드리지 않는다.
- 여러 독립 task의 stage/commit 범위를 물리적으로 분리한다.
- 다른 세션 소유 파일을 임의 stash/commit할 필요가 없다.

비용:

- 폴더와 local branch가 누적될 수 있다.
- 사용자가 어느 worktree에서 어떤 session을 시작했는지 추적해야 한다.
- parent의 미커밋 변경은 child에 자동 포함되지 않아 의존 관계를 명시해야 한다.

평가:

모든 작업에 worktree를 강제하지 않고 ACTIVE/PRESERVED 병행, dirty 기준 폴더, 실제 병렬 수정 때만 사용하도록 한 현재 전략이 균형적이다. 자동 garbage collection보다 읽기 전용 status/list 명령을 먼저 추가하는 것이 안전하다.

### 3.6 owner/contributor assignment

장점:

- 한 branch에서 여러 host가 순차적으로 역할을 나눠도 branch metadata를 다시 만들 필요가 없다.
- contributor의 부분 handoff와 owner의 최종 8종 책임을 구분한다.
- Git integrator를 한 명으로 제한해 index와 commit 충돌을 줄인다.

비용:

- owner assignment가 장기간 부재하면 contributor 작업이 merge되지 않고 PRESERVED로 남는다.
- handoff 품질이 낮으면 owner가 다시 탐색해야 한다.
- 같은 사람이 여러 role을 수행할 때 책임 구분이 형식적으로 느껴질 수 있다.

평가:

handoff를 “완료의 대체물”로 보지 않는 것이 중요하다. owner가 전체 source와 검증을 다시 확인한다는 원칙을 유지하되, 동일 작업자가 전체를 수행하면 8종을 역할별로 중복 작성하지 않는 현재 규칙이 합리적이다.

## 4. 기술 부채와 위험

### 4.1 role boundary의 비기계적 성격

현재 role은 system prompt와 선택 문서로 강제한다. 이는 사용자의 의도와 일치하지만, agent가 UI role에서 API 파일을 수정하려 할 때 branch scope가 넓다면 role 의미만으로는 차단되지 않을 수 있다.

권고:

- 당장 경로 heuristic hook을 추가하지 않는다.
- 실제 침범 사례와 오탐 후보를 `unknown/` 또는 evaluation log에 수집한다.
- 충분한 사례가 생기면 role별 semantic scope를 프로젝트 설정으로 둘지 평가한다.

### 4.2 대형 common guard

현재 common guard는 managed source, branch, artifact, readiness, Stop, operation approval을 조율한다. 단일 실행점은 필요하지만 함수 수가 늘어 향후 변경 영향 분석이 어려울 수 있다.

권고:

- 외부 runtime 파일 수를 바로 늘리기보다 내부 pure function 경계를 유지한다.
- 각 정책 영역별 test class 또는 fixture를 분리한다.
- 실제 결함 밀도가 높아질 때만 bundled module 구조를 검토한다.

### 4.3 host API 변화

OpenCode의 `chat.message`, `tool.execute.before/after`, session ID shape와 Codex/Claude hook schema는 외부 제품 변화에 민감하다.

권고:

- renderer unit test 외 실제 host `--print-only`/smoke test를 배포 절차에 포함한다.
- session ID가 없는 경우 fail-open하지 않고 선언된 session directory를 요구하는 현재 원칙을 유지한다.
- event API 변경은 adapter에만 국한하고 common state schema는 유지한다.

### 4.4 consumer legacy 퇴역

현재 diff에는 프로젝트마다 legacy 11개가 남고 기존 Codex test hook 하나는 audit hash mismatch로 표시됐다. 중앙 source에서 legacy 등록은 제거했어도 소비자 파일은 별도 retire 없이는 남는다.

권고:

- sync와 retire를 같은 명령으로 묶지 말고 각각 diff와 hash를 확인한다.
- mismatch 파일은 자동 삭제하지 않는다.
- 새 공통 hook이 실제 host에서 동작하는 smoke test 후 legacy 퇴역을 승인한다.

### 4.5 proposal/state 누적

Git common directory에 proposal, branch state와 session binding이 쌓일 수 있다. 자동 삭제는 audit trail을 잃게 할 수 있다.

권고:

- 먼저 상태 목록과 CLOSED/PRESERVED 필터를 제공한다.
- 보존 기간과 삭제 권한을 사용자가 정하기 전에는 자동 cleanup하지 않는다.
- cleanup은 branch finish proposal에 명시된 worktree/branch에만 한정한다.

## 5. 선택하지 않은 대안

### host별 완전 독립 문서 복제

- 장점: 각 host bundle만 읽어도 모든 문장이 로컬에 존재한다.
- 단점: 같은 역할 의미가 세 곳에서 drift하고, 어느 파일이 정본인지 다시 모호해진다.
- 결론: common 자체를 bundle에 포함하면 복제 없이 독립성을 달성할 수 있어 제외했다.

### legacy hook을 compatibility mode로 유지

- 장점: 기존 동작이 갑자기 사라지는 위험이 낮아 보인다.
- 단점: matching hook 중복 deny와 서로 다른 state가 바로 현재 장애 원인이다.
- 결론: 기능 대응 테스트 후 단일화가 더 안전하다.

### dirty worktree 자동 stash

- 장점: 같은 폴더에서 빠르게 branch를 바꿀 수 있다.
- 단점: stash 소유자·복원 시점이 불명확하고 다른 세션 변경을 감춘다.
- 결론: 자동화하지 않고 isolated worktree를 사용한다.

### 모든 Git 변경을 사용자에게 맡김

- 장점: agent의 Git 실수 surface가 최소화된다.
- 단점: 정상 stage/commit/ff-only lifecycle까지 수동화돼 반복성과 검증 가능성이 떨어진다.
- 결론: 승인된 integrator와 workflow는 허용하되, push/hard reset 등 복구·외부 영향이 큰 명령만 사용자 전용으로 둔다.

### 모든 cross-host artifact 접근 차단

- 장점: 소유권 모델이 단순하다.
- 단점: handoff와 이전 검토 문서를 읽을 수 없어 협업이 불가능하다.
- 결론: 읽기와 쓰기 권한을 분리한다.

## 6. 프로세스 개선 제안

### 즉시 적용

1. 중앙 변경을 먼저 commit해 배포 기준 SHA를 고정한다.
2. sync 전 `audit`와 `diff --project all` 결과를 다시 제시한다.
3. 별도 승인 후 한 소비자에서 role별 inject smoke를 우선 실행한다.
4. 실행 중 세션은 handoff한 뒤 재시작한다.
5. legacy retire는 새 runtime 확인 후 별도 수행한다.

### 단기 backlog

1. `branch_workflow.py list/status` 형태의 읽기 전용 task/worktree 조회 검토
2. 실제 host process를 사용한 UserPrompt/PostTool/Stop payload contract test
3. proposal 사람이 읽기 쉬운 요약과 canonical JSON diff 표시 개선
4. PRESERVED task 장기 방치 알림 정책 검토

### 조건부 backlog

1. role 침범 실제 사례가 반복될 때 semantic scope guard 검토
2. common guard 변경 충돌이 늘 때 bundled internal module 분리 검토
3. 새 host 도입 시 adapter conformance test kit 작성
4. 산출물 품질 편차가 클 때 Markdown 구조 validator 강화

## 7. 권고 우선순위

| 우선순위 | 권고 | 채택하지 않을 때 남는 문제 | 채택 시 추가 복잡성 |
| --- | --- | --- | --- |
| P0 | 중앙 commit 후 별도 승인된 sync | 배포 기준이 유동적이고 consumer와 source 대응이 불명확 | 승인 단계 1회 추가 |
| P0 | 새 공통 hook smoke 후 legacy retire | 중복 hook이 consumer에 남을 수 있음 | 단계적 배포 시간 |
| P1 | worktree/task 읽기 전용 status | PRESERVED/CLOSED 폴더 누적 파악 어려움 | CLI·테스트 추가 |
| P1 | host event payload smoke | 외부 API 변화가 unit test를 통과할 수 있음 | host별 실행 환경 필요 |
| P2 | role 침범 사례 수집 | 향후 guard 설계 근거 부족 | 로그 분류·검토 비용 |
| P3 | common guard 내부 모듈화 평가 | 장기 유지보수 인지 비용 증가 | runtime bundle 구조 복잡성 |

## 8. 아키텍처 원칙

다음 의존 방향을 이후 변경에서도 유지해야 한다.

```text
사용자 요청·handoff
  -> role profile
    -> 공통 의미·runtime registry
      -> renderer/inject
        -> host adapter
          -> 세션 assignment와 tool event
```

역방향 의존은 금지한다.

- common 문서가 `.codex`, `.claude`, `.opencode` 역할 정의를 참조하지 않는다.
- host adapter가 공통 역할 의미를 재정의하지 않는다.
- model 이름이 role이나 permission을 바꾸지 않는다.
- contributor handoff가 owner 완료 판정을 대신하지 않는다.
- command approval이 never-agent 명령을 해제하지 않는다.

## 9. 최종 평가

이번 변경은 여러 개의 개별 guard 예외를 추가한 것이 아니라, 역할·세션·branch·host의 책임을 분리해 기존 장애가 반복되던 구조를 바꿨다. 자동 테스트와 source audit가 핵심 invariant를 고정하고 있어 중앙 원본으로서는 장기 운영 가능한 상태다. 가장 큰 잔여 위험은 코드 자체보다 배포 순서다. 중앙 commit, 승인된 sync, host smoke, legacy retire, 세션 재시작 순서를 지키는 것이 다음 단계의 핵심이다.
