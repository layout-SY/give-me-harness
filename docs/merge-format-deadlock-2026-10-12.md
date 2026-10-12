# 충돌 병합 중 포맷 교착 수정

## 발생한 문제

2026-10-10 user-ui의 `orchest` 세션("시민토론-실API-전환")에서 `sy-main`에 `origin/dev`를 병합하다 시민참여 파일이 충돌했다. 세션이 충돌 파일을 수정해 해결한 뒤 다음이 모두 막혔다.

- `npm run lint`·`test`·`build`: 실행 전 자동 포맷이 "이미 stage된 파일은 자동 포맷하지 않습니다"로 실패
- `git add`·`git commit`: "Prettier 적용이 확인되지 않은 파일이 있습니다"
- Stop 훅: 응답이 끝날 때마다 같은 포맷 경고 반복

세션은 우회하지 않고 멈췄고, 사용자가 검증 명령과 병합 commit(`007fb81`)을 직접 실행했다. commit 뒤에는 포맷이 정상 동작해 별도 commit(`d5507aa`)으로 들어갔다.

## 원인

두 규칙이 서로를 막았다.

- 검증·stage·commit은 수정한 파일이 포맷됐다는 기록을 요구한다.
- 포맷 도구는 index에 올라 있는 파일을 거부한다. 포맷이 작업 폴더만 바꿔 index와 내용이 달라지는 것을 막기 위해서다.

평소에는 "포맷 → stage → commit" 순서로 풀리지만, 충돌 병합에서는 파일이 수정하기 전부터 index에 있어 이 순서를 지킬 수 없다. 오케스트레이션과 무관하게 모든 role에서 생기는 교착이다.

## 수정 (사용자 선택: 병합 중에는 포맷을 commit 뒤로 미룸)

`MERGE_HEAD`가 있는 worktree에서는 다음과 같이 동작한다.

| 지점 | 동작 |
| --- | --- |
| 검증 명령 전 자동 포맷 | 실행하지 않고 검증을 진행한다 |
| `git add`·`git commit`·`git merge` 전 포맷 확인 | 병합 중인 worktree의 파일은 요구하지 않는다 |
| Stop 훅 | 병합 중인 worktree는 포맷하지 않고 경고도 내지 않는다 |
| 포맷 직접 실행 | 파일을 바꾸지 않고 "병합 commit 뒤로 미룬다"고 알린다 |

수정한 파일은 포맷 대기 상태로 남는다. 병합 commit 뒤에는 평소처럼 포맷이 요구되고 적용되며, 포맷으로 바뀐 내용은 별도 commit이 된다. 병합 commit은 검증한 내용 그대로 기록된다.

위치는 `policy/guards/formatting.py`(`merging`, `check`, `require_before_validation`, `apply`, 직접 실행)와 `policy/guards/managed_policy_guard.py`(Stop)다. 공통 시스템 프롬프트의 포맷 문단에 같은 규칙을 추가했다.

## 범위와 한계

- 병합(`MERGE_HEAD`)에만 적용한다. rebase·cherry-pick 중의 충돌은 다루지 않았다. 정책이 이 둘을 완료 경로로 쓰지 않기 때문이다.
- 병합 중이 아닐 때 stage된 파일을 포맷하지 않는 기존 동작은 그대로다.
- 모든 role의 세션에 적용된다.
- `orchest` 세션에서는 병합 commit과 뒤따르는 포맷 commit 각각에 Watcher PASS가 필요하다.

## 검증

`tests/test_formatting.py`의 `test_conflicted_merge_defers_formatting_until_the_merge_commit`이 실제 충돌 병합을 만들어 재현한다. 수정 전에는 검증 명령 단계에서 "이미 stage된 파일은 자동 포맷하지 않습니다"로 실패했고 수정 후 통과한다. 병합 commit 뒤에 포맷이 다시 요구되고 적용되는 것까지 확인한다.
