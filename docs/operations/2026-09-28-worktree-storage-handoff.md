# 워크트리 저장 위치 정책 인계

- 요청: 임시 디렉토리의 작업 공간 유실을 예방하고 프로젝트 이름별 영속 폴더와 저장 위치 규칙 문서를 도입한다.
- 역할: 중앙 정책·실행 도구 유지보수. 프로젝트 이름별 구조와 문서 범위를 사용자 `Proceed`로 승인받았다.
- 중앙 작업 위치: `/Users/okand/SynologyDrive/asan-agent-policy`, branch `main`, 기준 HEAD `b4d89b396c285d038cf20dd1f5ce7a11846e0663`.
- 규칙 정본: [워크트리 저장 위치와 보존 규칙](../../policy/common/skills/policy/git-branch-strategy/references/worktree-storage.md).
- 설정: `projects/user-ui.json`, `projects/admin-ui.json`의 `worktree_root`. 프로젝트별 저장 폴더는 실제 승인된 첫 worktree 생성 시 만들어진다.

## 구현 범위

프로젝트 설정·렌더링, 공통 경로 검사, 관계 생성과 일반 Git 생성 경로, 공통 정책·Git 운영 스킬·README, 회귀 테스트를 수정했다. 기존 미커밋 변경을 보존했으며 소비자의 source·Git 등록 정보·세션 기록을 수정하지 않았다. commit·merge·worktree 이전·삭제는 수행하지 않았다.

`relation --action create`는 경로 생략 시 branch 이름으로 작업 폴더를 계산하고 승인 전에 절대 경로를 표시한다. 임시 디렉토리·심볼릭 링크 우회·프로젝트 저장 폴더 이탈·기존 또는 등록된 경로와의 충돌을 차단하며 실행 직전 다시 확인한다. 기존 위치에서의 작업과 세션 재개는 계속 허용한다.

## 기존 작업 공간 조사

2026-09-28 읽기 전용 재조회 결과다. 실행 직전에 다시 확인해야 하며, 아래 표는 이전·복구 승인이 아니다.

| 프로젝트 / 현재 위치 | 확인 상태 | 제안 목적지 / 다음 작업 |
| --- | --- | --- |
| user-ui / `~/SynologyDrive/asan-worktrees/reservation-media-check` | Git 연결 정상, `fix/reservation-media-check`, HEAD `a1b113d47c6b3da2cd3e6ae73cf317e51e07ce53`, 일반 status clean | `~/SynologyDrive/asan-worktrees/asan-metaverse-user-ui-worktree/reservation-media-check`; ignored 자료·로그·실행 중 작업을 추가 확인한 뒤 이전 계획 |
| user-ui / `~/SynologyDrive/asan-worktrees/vo-participant-status` | Git 연결 정상, `task/vo-participant-status`, HEAD `3e30393d2c9feaa12b4b5987a936863602967a5a`, 수정 1개·untracked 3개 | `~/SynologyDrive/asan-worktrees/asan-metaverse-user-ui-worktree/vo-participant-status`; 미커밋 변경과 로그 보존 후 이전 계획 |
| admin-ui / `/private/tmp/asan-metaverse-admin-ui-event-reward-ui` | 경로 없음 | branch·commit·중앙 로그·백업을 확인하는 복구 작업 |
| admin-ui / `/private/tmp/asan-metaverse-admin-ui-inquiry-types-api` | `.git` 없음. 의존성·빌드 결과 외 일반 파일은 재조회에서 발견하지 못함 | 남은 자료와 원본 저장소 이력을 대조하는 복구 작업 |
| admin-ui / `/private/tmp/asan-metaverse-admin-ui-item-ui` | `.git` 없음. 의존성 외 일반 파일은 재조회에서 발견하지 못함 | 남은 자료와 원본 저장소 이력을 대조하는 복구 작업 |

첫 조사에는 admin-ui의 세 임시 경로가 `prunable`로 등록돼 있었으나 이후 조회에는 기본 worktree만 등록돼 있었다. 이 작업에서 해당 등록을 제거하지 않았으며 상태 변경 원인은 확인하지 않았다.

`vo-participant-status`에서 확인한 미커밋 항목:

- 수정: `src/features/meeting-reservation/index.ts`
- untracked: `src/features/meeting-reservation/ui/entry/ParticipantStatusPage.test.tsx`
- untracked: `src/features/meeting-reservation/ui/entry/ParticipantStatusPage.tsx`
- untracked: `src/features/meeting-reservation/ui/entry/participant-status.css`

일반 `git status`의 clean만으로 ignored 자료나 모든 로그가 보존됐다고 판단하지 않는다. 기존 작업의 직접 부모·미처리 자식·실행 중 프로세스는 이번 조회로 확정하지 않았다.

## 소비자 적용

기존 inject bundle은 변경하지 않는다. 실행 중인 소비자 작업은 해당 세션이 자신의 실제 branch·HEAD·worktree·미커밋 변경·남은 작업을 handoff한 뒤 중앙 launcher의 새 `start`로 시작해야 새 규칙을 사용한다. 기존 assignment를 `resume`하면 원래 정책이 유지된다.

이 중앙 작업에서는 재시작할 소비자 세션·host·role을 선택하거나 새 소비자 host 프로세스를 실행하지 않았다. 기존 정상 worktree를 그대로 지정한 새 시작도 가능하다. 저장 위치 규칙은 새 생성에 적용하므로 정책 적용을 위해 기존 작업 공간을 먼저 이동할 필요는 없다.

```text
bin/agent-policy start --project <user-ui|admin-ui> --host <현재 host> --role <작업 역할> --worktree <확인한 기존 worktree>
```

기존 작업 공간 이전은 파일 상태와 중단 가능한 세션을 확인한 구체적 Git 작업으로 별도 준비한다. 현재 보호 실행기는 일반 `worktree move`·`repair`·`prune`를 차단한다. 이 제한을 우회하거나 소비자의 `.git` 파일을 직접 고치지 않는다.

## 검증 결과

| 검사 | 결과 |
| --- | --- |
| 수정 전 임시 경로 회귀 검사 | 3개 실패 확인: 관계 생성 준비, 일반 Git 준비, 관계 생성 실행 |
| 경로 변경 후 재준비 회귀 검사 | 이전 승인 대기 기록을 재사용하는 실패 확인 후 수정 |
| `python3 -m unittest discover -s tests -v` | 359개 통과, 1763.721초 |
| `PYTHONPATH=tests python3 -m unittest test_worktree_storage test_relation_operations test_shared_git_access -v` | 최종 보완 후 관련 83개 통과, 383.186초 |
| `bin/agent-policy audit` | central-contract PASS, admin-ui 279 bundle files PASS, user-ui 209 bundle files PASS |
| `git diff --check`, Python 구문, 문서 참조 링크 | 통과 |

전체 검사가 실행 중일 때 발견한 경로 재준비 문제를 추가 회귀 테스트로 고정했다. 이후 관련 세 테스트 모듈을 재실행했으므로 83개에는 전체 검사와 중복되는 검사와 새 회귀 검사 1개가 포함된다.

스킬 전용 `quick_validate.py`는 환경에 PyYAML이 없어 실행하지 못했다. 스킬 frontmatter는 변경하지 않았으며 중앙 계약 감사·렌더링 검사·실제 참조 링크 검사로 문서 연결을 확인했다. 실제 소비자 worktree 이전이나 새 host 프로세스 실행의 성공을 이 테스트 결과로 간주하지 않는다.
