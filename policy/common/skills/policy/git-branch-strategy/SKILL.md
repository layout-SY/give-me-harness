---
name: policy-git-branch-strategy
description: 모든 세션의 프로젝트 Git 접근과 사용자 변경 승인, 기존 작업 보호를 관리한다.
---

# Git 운영

기준 branch는 `{{BASE_BRANCH}}`다. 모든 host·role·session은 해당 프로젝트의 모든 branch와 연결 worktree에 접근할 수 있다. 세션별 생성 권한, 계보·scope 계약, Git integrator, 독점 claim과 CLOSED 조건을 사용하지 않는다. 새 branch와 worktree는 작업 필요에 따라 선택한다.

## 조회와 변경

- 접근 공유는 현재 세션 프로젝트 안에서만 적용한다. 다른 프로젝트의 Git 조회·변경과 명령 실행은 금지하며 해당 프로젝트의 별도 세션을 사용한다. 실행 위치와 실제 Git 저장소는 사용자 승인보다 먼저 확인한다.
- 같은 Git common directory를 공유하는 연결 worktree는 허용한다. 다른 저장소를 만드는 clone/init, 프로젝트 외 global/system Git 설정, 다른 로컬 프로젝트를 가리키는 remote·파일 출력·worktree 대상은 현재 세션에서 사용하지 않는다.
- status, diff, log, 조회형 branch/config와 worktree list는 승인 없이 조회한다. 옵션이 파일이나 Git 상태를 바꾸면 변경 작업이다.
- 생성, 전환, stage, commit, merge, fetch, pull, rebase, stash, restore, branch/worktree 삭제, config 수정과 push는 사용자 승인 후 수행한다.
- reset --hard, clean, update-ref, force push 등도 승인 가능한 작업이다. 유실 가능한 변경·commit과 원격 영향을 먼저 설명한다.
- 변경 승인에는 작업 위치, 명령, 대상 branch·HEAD 또는 파일, 목적과 영향을 제시한다. 사용자가 구체적으로 요청한 동일 작업을 중복 승인받지 않는다.
- `git add -- <명시 경로> && git commit -m <메시지>`처럼 관련 작업을 묶어 한 번에 승인받을 수 있다. 승인 후 위치·명령·대상 상태가 달라지면 다시 확인한다.
- Claude는 native 권한 요청을 사용한다. Codex·OpenCode는 공통 guard에 대기 중인 작업을 `진행` 또는 `명령 실행 승인`으로 승인한다. SHA 입력을 요구하지 않는다.
- 일반 lint·test·build는 승인된 작업의 검증으로 실행한다. Git에 구현 탐색·필수 문서 검사를 추가하지 않는다.

## 기존 작업 보호

작업 전에 실제 worktree·branch·HEAD와 dirty/staged 변경을 확인한다. 다른 작업의 변경을 임의로 commit·stash·복원하지 않는다. stage 경로를 명시하고 commit 전에 staged diff를 확인한다. 같은 worktree의 Git 변경은 순차 실행하고 native Git lock을 임의로 제거하지 않는다. 병렬 구현에는 별도 worktree를 권장한다.

다른 host의 설정·세션 로그와 다른 세션의 산출물은 읽기 전용이다. 이미 커밋된 기록은 승인된 branch 전환·병합 과정에서 그대로 전달할 수 있다. 산출물 내용을 대신 수정·삭제하거나 새 commit에 임의로 포함하지 않는다. `.git` 내부 파일을 직접 편집하지 않는다.

## 병합과 완료

실제 변경과 검증 결과, source·target, merge 방식을 보고하고 사용자 승인 후 일반 `git merge`를 사용한다. ff-only가 가능한지 먼저 확인하며 실패했다고 임의로 방식·대상을 바꾸지 않는다. source 또는 target의 작업 세션·host·role이 달라도 병합할 수 있다. Git이 충돌하면 상태를 보존하고 해결 범위를 확인한다.

사후 검증 결과와 미완료 항목을 기록한다. 기존 오류도 통과로 기록하지 않으며, 오류가 남은 상태의 병합 여부는 사용자가 판단한다. 완료 상태는 기록이고 접근 권한이나 다음 작업의 조건이 아니다. 작업 완료와 branch/worktree 삭제를 분리하고, 삭제는 정확한 대상과 보존할 변경을 확인한 별도 승인 범위로 수행한다.

## 세션 이동과 이전 계약

`--worktree`는 시작 위치, `--branch`는 그 시점의 branch 확인값, `--task`는 작업 설명이다. 실행 중에는 `workdir` 또는 `git -C`로 다른 연결 worktree를 사용할 수 있다. host sandbox가 별도로 요구하는 파일 쓰기 승인은 필요한 경로만 받는다.

V1/V2/V3 metadata·Git claim·finish 예약은 과거 실행 이력으로 보존하고 새 세션의 권한으로 읽거나 갱신하지 않는다. 새 V4 bundle에서는 `branch_workflow.py proposal/create/finish/verify/close`를 사용하지 않는다. 중앙의 이전 실행 복구 코드는 기존 V3 계약 처리용으로만 유지한다.

정책 적용은 현재 작업을 handoff한 뒤 새 inject assignment로 시작한다. Git 소유권 인계·해제는 필요하지 않다. 이전 세션을 `--resume-assignment`로 재개하면 원래 bundle이 유지되므로 최신 정책 적용이 아니다. 과거 세션과 새 세션이 같은 worktree에서 동시에 Git 변경을 실행하지 않도록 인계한다.
