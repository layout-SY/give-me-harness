# 통합 worktree와 cleanup 대상 충돌 수정

## 재현과 원인

`task/reservation-restricted-popup`은 외부 worktree에서 `sy-main`으로 ff-only 병합한 뒤 lint·build 검증을 통과했다. finish SHA는 `1a44ba2fee957bd74c48eab48ec5d1be93b8ac56261cf247207b3364e0e77a81`, 검증된 HEAD는 `c79f3d8c74c0536fa2d3afb983fb2e121742f076`이다.

기존 finish proposal은 target이 다른 worktree에 checkout되어 있지 않으면 source worktree를 통합 위치로 선택하면서 같은 경로의 `cleanup: true`도 허용했다. finish가 해당 worktree를 target으로 전환한 뒤 close는 cleanup 대상이 source를 checkout하고 있어야 한다고 검사했다. 이 계약은 병합 후 충족할 수 없었다.

기존 테스트는 별도 통합 worktree에서 cleanup하는 경우와 하나의 worktree에서 cleanup 없이 종료하는 경우만 검사했다. 기본 worktree가 다른 작업으로 dirty이고 외부 worktree가 통합과 삭제를 겸하는 조합을 빠뜨렸다.

`MERGED_VERIFIED` 상태에서 cleanup 없는 finish proposal을 다시 만드는 우회도 작동하지 않는다. 새 proposal은 ACTIVE만 허용하며, 새 SHA는 기존 통합 예약과도 다르다. `integration-recover`는 실패한 병합을 원래 target으로 되돌리는 별도 기능이다.

## 변경

- 공통 `branch_workflow.py`: 통합과 cleanup 대상이 같은 계약은 proposal 단계와 새 병합 실행 전에 차단한다. 이미 실행한 병합 결과의 receipt 복구는 유지한다. 별도 target worktree를 준비하거나 cleanup 없이 제안하도록 안내한다.
- 중앙 `close-recover`: 같은 경로의 구형 cleanup 계약에서 검증이 완료된 경우만 지원한다. 원래 finish SHA, 현재 HEAD, source 계약, 검증 receipt, assignment, 통합 예약과 Git claim을 새 복구 SHA에 묶는다.
- 승인 적용: source metadata와 종료 기록을 CLOSED로 만들고 해당 통합 예약과 Git claim을 해제한다. 기존 finish 계약과 검증 근거를 유지하면서 receipt에 `cleanup_deferred`와 `close_recovery_sha256`을 남긴다. branch·worktree·로그를 보존한다.
- 재시도: 작업 journal을 먼저 기록한다. 자신의 부분 기록만 같은 SHA로 재개할 수 있으며, HEAD·소유권·검증 근거가 달라지면 중단한다. 완료 후 재호출은 이후 작업의 소유권을 해제하지 않는다.

host adapter와 프로젝트별 overlay에는 변경이 없다. 새 proposal 차단은 중앙 launcher로 시작한 새 inject 번들에서 적용된다. 중앙 복구 명령은 소비자의 기존 번들을 고치지 않고 사용할 수 있다.

## 회귀 검증

`tests/test_close_recovery.py`는 실제 임시 Git 저장소에서 과거 계약의 merge·verify·close 실패를 재현한다. 수정 전 최초 6개 테스트는 2개 실패와 4개 미구현 오류로 종료했고, 수정 후 모두 통과했다. 최종 9개 사례는 다음을 포함한다.

- 같은 경로의 proposal 및 과거 승인 계약의 신규 finish 차단
- 검증 완료 후 미리보기·잘못된 SHA 거부·정리 보류 종료·반복 호출
- source 또는 target HEAD, dirty 파일, 검증 기록, assignment·Git 소유권 변경 거부
- 원본 계약 변조와 다른 cleanup 배치 거부
- CLOSED 기록 뒤 중단 및 예약 해제 뒤 중단의 동일 SHA 재시도
- 다른 작업의 dirty 기본 worktree와 이후 소유권 보존

전체 검사 명령: `python3 -m unittest discover -s tests -v`, `bin/agent-policy audit`.

최종 검증: 전체 unittest 200개 통과, 중앙 계약·admin-ui·user-ui audit 모두 PASS, `git diff --check` 통과. 실행 로그는 `/private/tmp/asan-close-full-suite.log`, 수정 전 실패 로그는 `/private/tmp/asan-close-red.log`에 남겼다. 이번 작업만의 diff는 `/private/tmp/asan-close.diff`다.

## 실제 작업 복구 미리보기

미리보기 SHA: `2fcc68f13bcf28e1aef66634d53a18daa7fdd739facec1c0f7aa32df74926bb0`

계약 파일: `state/repositories/4513b4f40b840df844024984f40ab0b185b2f47439c6e7548d5c72fc4d83666b/recoveries/2fcc68f13bcf28e1aef66634d53a18daa7fdd739facec1c0f7aa32df74926bb0.json`

미리보기 시 실제 상태는 `sy-main` checkout, clean, `MERGED_VERIFIED`, receipt `verified`다. 적용하면 `task/reservation-restricted-popup`과 `/Users/okand/SynologyDrive/asan-worktrees/reservation-restricted-popup`을 보존하고 CLOSED 및 정리 보류만 기록한다. 병합과 npm 검증을 다시 실행하지 않는다.

아래 명령은 이 정리 보류 계약을 승인받은 뒤에만 실행한다. 원래 승인한 `cleanup: true`의 실행 내용을 바꾸므로 복구 SHA 승인을 별도로 받는다.

```sh
bin/agent-policy close-recover --project user-ui \
  --finish-file /Users/okand/SynologyDrive/asan-metaverse-user-ui/.git/asan-agent-policy/finish-proposals/1a44ba2fee957bd74c48eab48ec5d1be93b8ac56261cf247207b3364e0e77a81.json \
  --finish-sha256 1a44ba2fee957bd74c48eab48ec5d1be93b8ac56261cf247207b3364e0e77a81 \
  --approved-sha256 2fcc68f13bcf28e1aef66634d53a18daa7fdd739facec1c0f7aa32df74926bb0
```

실제 복구 적용과 실행 중인 소비자 세션 교체는 아직 수행하지 않았다.
