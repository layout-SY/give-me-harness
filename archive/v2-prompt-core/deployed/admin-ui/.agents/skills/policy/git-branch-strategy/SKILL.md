---
name: policy-git-branch-strategy
description: 저장소 변경 작업을 시작하거나 이어가거나 병합할 때 브랜치 계보, 별도 사용자 승인, 작업 범위, compact 복구 및 안전한 정리를 관리한다.
---

<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/common/skills/policy/git-branch-strategy/SKILL.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# Git 브랜치 전략

기준 브랜치는 `sy-main`다. 모든 사용자 요청에서 이 스킬을 먼저 읽되, 읽기 전용 조사·설명만 수행하면 브랜치를 만들지 않는다. 저장소를 변경할 때는 구현 승인과 별도의 브랜치 생성 승인을 받은 뒤 첫 변경 전에 새 작업 브랜치를 만든다.

## 분기 판단

1. `git status --short --branch`, 현재 브랜치와 기준 브랜치 대비 변경 경로를 확인한다.
2. 새 작업이 이전 미병합 브랜치의 커밋에 의존하거나 변경 예정 파일·폴더가 그 브랜치의 변경 경로와 겹치면 해당 브랜치에서 자식 브랜치를 분기한다.
3. 관련이 없으면 `sy-main`에서 분기한다.
4. 브랜치명은 작업을 요약한 ASCII kebab-case인 `task/<summary>` 형식을 사용한다.
5. 분기 기준 브랜치와 직접 merge 대상은 같아야 한다. 상위 계보의 각 작업 브랜치도 목적과 직접 merge 대상을 보고한다.
6. dirty worktree, 미해결 충돌 또는 다른 세션의 동일 worktree 사용 가능성이 있으면 commit, stash, reset, checkout을 임의 수행하지 않고 사용자에게 보고한다.

## 브랜치 생성 승인

구현 승인은 브랜치 생성 승인을 대신하지 않는다. 다음 형식으로 정확한 분기 계약을 제시하고 독립된 긍정 응답을 기다린다. 이름, 목적, 부모, merge 대상, 범위 또는 부모 HEAD가 달라지면 다시 승인받는다.

승인 요청은 다음 도구의 `proposal` 명령으로 생성한다. 관련 작업이면 `--parent`에 이전 작업 브랜치, 독립 작업이면 `sy-main`를 준다. 경로가 여러 개면 `--scope`를 반복한다.

```sh
python3 .agents/skills/policy/git-branch-strategy/scripts/branch_workflow.py proposal --branch task/<summary> --purpose "<작업 목적>" --parent <parent> --scope <path> --reason "<분기 판단 근거>"
```

```text
[브랜치 생성 승인 요청]
- 작업 목적: <요약>
- 분기 기준: <parent>
- 분기 기준 HEAD: <commit>
- 새 브랜치: task/<summary>
- 직접 merge 대상: <parent>
- 승인 요청 식별자: branch:<새 브랜치>|parent:<분기 기준>@<분기 기준 HEAD>|merge:<직접 merge 대상>
- 예정 작업 경로:
  - <path>
- 상위 브랜치 계보:
  - <parent>: <작업 목적>, 추후 <merge-target>으로 merge
- 분기 판단 근거: <의존 커밋 또는 변경 경로 중첩 여부>
- 현재 상태: <현재 브랜치와 dirty 여부>

이 계약으로 브랜치를 생성해도 될까요?
```

승인 후에는 승인 요청에 표시된 값 그대로 `create` 명령을 실행한다. 이 명령은 dirty 상태와 부모 HEAD·proposal ID를 다시 확인한 후 브랜치와 Git config를 함께 생성한다.

```sh
python3 .agents/skills/policy/git-branch-strategy/scripts/branch_workflow.py create --branch task/<summary> --purpose "<작업 목적>" --parent <parent> --parent-head <승인 시점 부모 HEAD> --proposal "<승인 요청 식별자>" --scope <path>
```

다음 Git config는 도구가 기록한다. `scope`는 승인된 경로마다 하나씩 추가된다. 이 값은 hook과 compact 복구가 사용하는 브랜치 정적 메타데이터이며 승인 자체를 대체하지 않는다.

```sh
git config branch.<branch>.asan-purpose "<작업 목적>"
git config branch.<branch>.asan-parent "<분기 기준>"
git config branch.<branch>.asan-parent-head "<승인 시점 부모 HEAD>"
git config branch.<branch>.asan-merge-target "<직접 merge 대상>"
git config branch.<branch>.asan-proposal "branch:<branch>|parent:<분기 기준>@<승인 시점 부모 HEAD>|merge:<직접 merge 대상>"
git config --add branch.<branch>.asan-scope "<승인 경로>"
```

브랜치 생성 직후 현재 브랜치와 기록된 계약을 다시 출력한다. 예상과 다르면 수정하지 말고 중단한다. 작업 중에도 매 변경 전 현재 브랜치가 승인된 브랜치인지 확인하며 승인 범위 밖 경로가 필요하면 범위를 임의 확장하지 않고 다시 승인받는다.

## 브랜치당 작업 완료와 merge

기본값은 브랜치당 한 작업을 끝내고 바로 merge 여부를 묻는 것이다. 구현·문서화·검증을 마치면 다른 작업을 시작하기 전에 다음을 보고한다.

```text
[브랜치 병합 승인 요청]
- 완료한 작업: <요약>
- 병합할 브랜치: <source>
- 직접 merge 대상: <target>
- source/target HEAD:
- 상위 브랜치 계보:
- 변경 파일:
- commit 예정 내용과 메시지:
- 검증 결과:
- 충돌 사전 점검:
- 적용할 merge 방식:
- 병합 후 정리: 사후 검증 성공 시 source 로컬 브랜치를 git branch -d로 삭제
- 원격 작업: push 및 원격 브랜치 삭제 안 함

이 계약으로 commit, merge, 사후 검증과 로컬 브랜치 정리를 진행해도 될까요?
```

승인되면 승인된 경로만 stage·commit하고 기록된 target에 merge한다. 기존 저장소의 merge 관례를 우선하며 선택한 방식을 승인 요청에 명시한다. target HEAD나 diff가 승인 이후 달라지거나 충돌이 예상되면 merge하지 않고 다시 보고한다.

merge 후 target에서 검증을 다시 실행한다. source HEAD가 target에 포함되고 검증이 성공한 경우에만 `git branch -d <source>`로 로컬 브랜치를 정리한다. `git branch -D`, 자동 rebase, cherry-pick, push 및 원격 브랜치 삭제는 금지한다. 검증 실패 시 자동 rollback이나 삭제를 하지 않고 source를 보존한 채 보고한다.

자식 브랜치가 있으면 leaf부터 부모로 merge한다. `A -> B -> D`라면 `D -> B`를 승인·검증·정리한 뒤, B의 작업까지 완료되었을 때 별도 승인으로 `B -> A`를 수행한다. 미병합 자식이 있는 부모를 먼저 merge하거나 삭제하지 않는다. 사용자가 merge를 보류하면 현재 브랜치를 보존하고, 후속 범위가 실제로 연결될 때만 별도 승인 후 자식 브랜치를 만든다.

## Context compact와 재개

compact, resume 또는 handoff 직후에는 응답이나 도구 사용 전에 현재 Git 상태를 다시 읽고 다음을 명시한다.

- 현재 브랜치와 작업 목적
- 분기 기준 브랜치와 승인 시점 부모 HEAD
- 직접 merge 대상
- 승인된 작업 경로
- 기준 브랜치까지의 상위 계보와 각 브랜치 목적·merge 대상
- dirty 상태와 미병합 자식 브랜치
- 현재 작업이 구현 중인지 merge 검토가 필요한지
- 다음 안전 조치

hook이 주입한 `[BRANCH_CONTEXT]`와 실제 Git 상태가 다르면 실제 Git을 우선하되 작업을 중단하고 사용자에게 불일치를 보고한다.
