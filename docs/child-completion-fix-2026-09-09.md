# 다른 assignment의 자식 branch를 부모에서 완료하는 정책 수정

## 문제와 재현

- admin-ui: `task/news-management-logic`(Codex) → `task/news-management-ui`(Claude).
- user-ui: `task/reservation-mock-logic`(Codex) → `task/reservation-detail-ui`(Claude).

기존 완료 절차는 source worktree에서만 proposal을 만들고 source의 Git integrator가 실행하도록 제한했다. 동시에 실제 병합 대상 worktree는 다른 부모 assignment가 소유했다. UI는 source 조건에, Logic은 target claim에 막혔다. 부모가 ACTIVE인 이번 사례는 과거 CLOSED 누락으로 남은 claim과 구별된다.

`test_parent_cannot_reuse_legacy_source_finish_approval`을 기존 원본에서 실행하여 다음 실패를 먼저 고정했다.

```text
finish proposal은 source worktree에서 실행해야 합니다: task/reservation-mock-logic
Ran 1 test in 11.968s
FAILED (failures=1)
```

실패 기록: `/private/tmp/asan-child-completion-before.log`.

## 구현

기존 `finish-proposal --source <직접 자식>` 명령을 부모 worktree에서 실행할 수 있게 했다. 현재 branch와 source가 다르면 직접 부모 관계와 양쪽의 유효한 V3 계약·assignment·Git claim을 검사한다. source에서 실행하는 기존 완료 계약은 유지한다.

부모 완료 계약의 `completion_authority`에는 다음을 canonical SHA-256에 포함한다.

- `mode: parent`.
- 부모 실행 assignment·host와 부모 V3 계약 SHA.
- 자식 assignment·host와 자식에게 귀속된 세션 산출물 디렉터리.

기존 계약 필드의 source·target 전체 HEAD, 실제 두 worktree, source V3 계약 SHA, 병합 방식과 정확한 사후 검증 argv도 계속 승인 대상이다. 이 새 계약에는 새 SHA 승인이 필요하며 이전 자식 담당자의 승인 기록을 복사하지 않는다.

`child_completion.py`를 hook과 workflow 본문에서 함께 사용한다. 부모 owner가 자식 산출물을 읽어 완료 근거를 검사하며 부모의 진행 중인 작업에 자식 산출물을 중복 작성하지 않는다. 부모의 구현·스킬·UI 탐색·계약 승인 gate는 그대로 적용한다. Codex와 Claude의 조합을 반대로 둔 경우도 테스트한다.

자식 HEAD·계약·소유권·귀속 변경, dirty worktree, 미병합 하위 branch, 양쪽 assignment의 결과 미확인 도구 예약을 차단한다. 마지막 예약 검사와 자식 READY_TO_MERGE 전환은 repository events lock 안에서 수행한다. 조회 캐시는 읽기 전용 검사 범위에서만 사용하고 Git 변경 직전 다시 검사한다.

`close`는 자식만 CLOSED로 기록하고 승인된 자식 claim만 해제한다. 부모는 ACTIVE와 자기 claim을 유지한다. 타 세션의 branch·worktree와 산출물은 보존하므로 이 경로의 `--cleanup`은 거부한다. CLOSED metadata 기록 후 중단된 close도 같은 계약으로 복구할 수 있게 closing 영수증을 먼저 기록한다.

추가로 자식 merge 직후 verify·close를 건너뛰고 같은 worktree에서 부모→sy-main finish를 시작할 수 있던 예약 검사의 누락을 재현했다. 기존 검사는 target branch별 예약만 대조했다. 이제 같은 worktree의 다른 완료 계약 예약도 hook과 본문 양쪽에서 차단한다. 자식 close가 끝나면 부모 완료를 진행할 수 있다. 수정 전 실패 기록은 `/private/tmp/asan-child-completion-reservation-before.log`에 있다.

## 검증

- 기본 회귀 13개: PASS, 273.483초. 두 보고 사례의 실제 hook → workflow → 결과 hook → close 재시도를 포함한다.
- 전체 `python3 -m unittest discover -s tests -v`: 229개 PASS, 1081.852초. 이 실행에는 최초 추가 회귀 16개가 포함되었다.
- 후속 자식 완료 회귀 17개: PASS, 371.150초. host 조합 반전, close 중단 복구, finish 검사 중 시작된 자식 쓰기 차단, 자식 close 전 부모의 다음 병합 차단을 포함한다.
- 이후 추가한 진행 중 부모 완료 계약의 handoff 차단: 1개 PASS, 24.173초. 이번 작업의 새 회귀는 총 18개다.
- 부모·자식 양쪽의 미확인 예약 검사 최종 재검증: 1개 PASS, 24.193초. 기존 assignment handoff 복구 호환 검사: 1개 PASS, 0.889초.
- `bin/agent-policy audit`: 중앙 계약, admin-ui 262개 bundle 파일, user-ui 192개 bundle 파일 PASS.
- `git diff --check`: PASS.

전체 검사 로그: `/private/tmp/asan-child-completion-full-suite.log`.

최종 회귀 로그: `/private/tmp/asan-child-completion-final-regressions.log`, `/private/tmp/asan-child-completion-handoff-after.log`, `/private/tmp/asan-child-completion-pending-regression.log`, `/private/tmp/asan-child-completion-legacy-handoff.log`.

## 실행 중인 세션에 적용

기존 inject bundle은 불변이므로 원본 수정으로 실행 중인 세션의 정책이 바뀌지 않는다. 새 bundle의 동일 host·role 부모 세션을 준비하고, 현재 부모 담당자의 handoff를 근거로 중앙 `assignment-handoff`의 검토·승인 절차를 거친다. 이후 새 부모 세션이 새 완료 계약을 제안한다. `--resume-assignment`는 기존 bundle 재개에 사용한다.

부모 완료 계약은 실행 assignment를 고정하므로 finish 이후에는 같은 assignment를 재개해 verify·close까지 수행한다. 중앙 `assignment-handoff`도 해당 계약의 예약이 남은 동안에는 소유권을 바꾸기 전에 차단한다. 그렇지 않으면 claim만 이전되고 승인된 실행 담당자는 바뀌지 않아 완료할 수 없게 된다. 이 누락도 `/private/tmp/asan-child-completion-handoff-before.log`에서 먼저 재현했다. 진행 중인 부모 완료 계약의 실행 권한을 다른 assignment로 이전하는 기능은 이번 범위에 포함하지 않는다. 세션 교체는 부모 완료 계약을 만들기 전에 수행해야 한다.

각 부모 worktree에서 새 bundle의 스크립트 절대 경로를 사용한다.

```sh
python3 <새-bundle의-branch_workflow.py> finish-proposal \
  --source task/news-management-logic \
  --merge-strategy ff-only \
  --verify-command "npm run lint" \
  --verify-command "npm run build"
```

user-ui에서는 source를 `task/reservation-mock-logic`으로 바꾼다. 생성된 계약의 전체 SHA를 승인받고 부모에서 각각 finish, verify, close를 실행한다. 부모→sy-main 완료는 그 다음 별도 계약이다.

실제 상태에 대한 읽기 전용 새 정책 검사에서는 양쪽 자식에 기존 결과 미확인 예약이 하나씩 확인되었다.

| 프로젝트 | 자식 assignment | 도구 call | 확인된 대상 |
| --- | --- | --- | --- |
| admin-ui | `14a3b5c529a94f6d8c36fb91cfee693d` | `exec-c580ea48-63c5-46d2-826a-e537d904fab6` | 자식 세션 `handoff.md` apply_patch |
| user-ui | `ed17a5549ae942c79f833b1ffadbe9de` | `exec-e6935f90-6f2a-4929-8c2d-5198b390b9d3` | 예약 mock `fixtures.ts`·`handlers.ts` apply_patch |

해당 call ID 문자열은 현재 native rollout에서 직접 대응되지 않았다. 작업 결과를 확인한 뒤 중앙 `assignment-recover --project <project> --assignment <id> --call-id <call> --outcome <confirmed|cancelled>`로 정확한 복구 계약을 검토·승인해야 한다. 이번 중앙 수정에서 이 예약을 임의로 삭제하거나 성공으로 처리하지 않았다.

admin Logic의 최신 handoff에는 `npm run build` 성공, 별도 `tsconfig.app.json` 타입 검사 14건 실패, 전체 lint 68 errors/5 warnings 실패가 기록되어 있다. 부모 소유권 문제를 해결해도 실패한 검증은 MERGED_VERIFIED 또는 CLOSED가 되지 않는다. 변경 범위 밖의 오류 처리와 검증 명령 계약은 별도 판단 대상이다.

이 정책 수정 시점에는 소비자 branch 병합과 실제 소유권 인계를 실행하지 않았다. 이후 별도의 사용자 직접 요청에 따라 두 자식→부모 병합을 중앙에서 처리했다. 현재 결과는 [중앙 직접 병합 기록](manual-child-merges-2026-09-09.md)을 따른다. user-ui 자식은 CLOSED, admin-ui 자식은 lint 실패로 READY_TO_MERGE이며 부모 소유권은 유지했다.
