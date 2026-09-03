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
- `asan-prompt-core`, 백업 또는 `asan-harness`를 참조하지 않았다.

## 9. 반복 문제와 escalation

- `retry_count`: 1 — preserve 테스트 fixture 수정 후 통과
- `repeat_issue_detected`: false
- `escalation_needed`: none
- 사용자 선택이 남은 항목: 소비자 sync, legacy retire, 세션 재시작 시점

## 10. 최종 결론

중앙 정책 변경은 사용자가 지정한 host-neutral 역할, role-aware inject, 공통 8종, Claude portfolio 구조, legacy hook 단일화, cross-session read-only와 Branch Contract V3 요구를 충족한다. 크리티컬 명령은 세 host와 shell alias에서 승인 불가 사용자 전용으로 검증됐다. 중앙 commit 대상으로 승인할 수 있으며, 소비자 배포는 별도 승인 단계로 유지한다.
