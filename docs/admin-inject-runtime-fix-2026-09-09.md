# admin-ui 통합 소유권과 inject 재개 장애 수정

## 확인한 원인

공지사항 작업은 merge 이후 `npm run lint`가 68 errors / 5 warnings로 실패했다. 따라서 close 호출만 누락된 성공 작업이 아니다. `task/connect-news-api`는 `READY_TO_MERGE`, 통합 receipt는 `merged`로 남았으며 assignment `adc9f97a68614efa9180b7a90cbf7681`의 Git claim과 sy-main 통합 예약도 유지됐다.

finish가 같은 worktree를 sy-main으로 전환한 뒤 자기 handoff·final-summary 수정까지 branch 불일치로 차단했다. 디스크 문서가 실제 실행 결과를 반영하지 못한 이유다. 원본 Codex 대화에서 병합 08:29:36, lint 실패 09:38:13, 산출물 수정 거부 09:40:04를 확인했다(KST).

후속 Claude UI 세션은 `cd` 다음 줄에 Python workflow를 실행했다. 훅은 이 복합 명령을 workflow로 분류하지 못해 task 생성 단계의 Git 소유권 검사가 빠졌다. 09:55:38 생성은 성공했지만 10:08:52 commit은 기존 Codex 소유권에 막혔다. 이후 사용자 직접 shell 입력으로 로그인 화면 commit·merge·build를 수행했다. 현재 실제 Git은 clean sy-main `5834f920fcceadbe79491791d5cf8a35ca7e2a98`지만 `task/sign-in-page` 정책 상태는 `ACTIVE`다.

Codex 대화 이력은 유실되지 않았다. assignment별 `CODEX_HOME`을 사용하므로 일반 Codex 또는 다른 inject assignment의 `/resume` 목록에서 보이지 않는다. 원본 native session은 `01a08187-6168-77b0-b09b-5d23e54d8fac`이며 아래 home에 JSONL 661행, 이력 index와 DB가 남아 있다.

```text
state/repositories/efc3a8561a1c88e862e3f5c61f955c00c442164e45dbe8ab31f06e61e7be50b8/assignments/adc9f97a68614efa9180b7a90cbf7681/codex-home
```

`--resume-assignment`의 bundle 검증 실패는 별도 결함이다. 원본 manifest의 모든 선언 파일은 일치했지만 workflow의 `importlib` 로딩이 다음 추가 파일을 생성했다. 동일 현상이 Claude UI 번들에도 있었다.

```text
policy/.agent-policy/runtime/__pycache__/branch_guard.cpython-314.pyc
policy/.agent-policy/runtime/__pycache__/runtime_state.cpython-314.pyc
```

캐시 생성 시각 08:24:54는 finish-proposal 실행과 일치했다. 임시 복사본 재현에서 기본 Python과 `-I`는 두 캐시를 생성해 검증에 실패했고, `-B -I`는 통과했다. 중앙 정책 변경이나 CODEX_HOME 손상이 재개 실패의 직접 원인은 아니다.

## 중앙 수정

- workflow의 runtime 로더를 소스 직접 로딩으로 바꿔 pyc를 읽거나 생성하지 않는다.
- bundle 진단은 누락·변경·추가 파일과 symlink를 구분한다. `bundle-repair`는 원본 파일이 모두 일치하고 추가 항목이 확인된 캐시뿐일 때 백업 후 정확한 파일만 격리한다.
- `sessions`는 assignment별 이력 위치, native ID, task 상태, 미확인 call, 통합 예약, bundle 상태와 원래 재개 명령을 조회한다. home·DB를 공유하거나 대화 내용을 출력하지 않는다.
- 복합 shell 안의 Python workflow를 명시적으로 거부하고 도구 workdir와 단일 명령 사용을 안내한다. create 본문도 Git claim과 미완료 통합 예약을 검사한다.
- 병합 후에도 원본 finish 계약·통합 receipt로 귀속이 확인되는 자기 세션 로그를 갱신할 수 있다. verify 실패는 receipt에 명령·HEAD·종료 코드·사유를 남기고 이전 검증 완료 상태를 해제한다. 재검증 실패 후 과거 성공 기록으로 close가 통과하던 추가 결함도 수정했다.
- `integration-preserve`는 검증 미완료 병합과 명시한 후속 수동 병합을 새 SHA 계약으로 보존한다. 실제 상태 변경 전에 HEAD, 소유권, 관련 task, 취소할 call과 해제할 예약을 검토한다. 적용은 `PRESERVED` 기록이며 검증 성공 또는 `CLOSED`로 취급하지 않는다.

이번 수정은 중앙 CLI·공통 workflow·guard·테스트다. host adapter 또는 프로젝트 overlay 추가는 없다. 앞선 TalkToFigma와 close-cleanup 수정은 유지했다.

## 실제 bundle 복구 결과

다음 두 assignment의 캐시를 각각 2개씩 백업·격리했다. 정책 파일·digest와 원본 대화 저장 위치는 유지했다.

| assignment | 원래 bundle | 결과 |
| --- | --- | --- |
| adc9f97a68614efa9180b7a90cbf7681 | codex-logic-80bc872b88c3c486 | valid |
| 598b9af704914ff5bf5233d58348c1f7 | claude-ui-536f0e4ca10cd868 | valid |

백업과 audit JSON은 위 repository state의 `bundle-repairs/` 아래에 있다. 원본 Codex와 Claude 재개 명령에 각각 `--print-only`를 붙인 검사는 모두 exit 0이었다. 실제 대화 프로세스는 실행하지 않았다.

```sh
bin/agent-policy sessions --project admin-ui --host codex
bin/agent-policy start --project admin-ui --host codex --role logic \
  --responsibility owner --resume-assignment adc9f97a68614efa9180b7a90cbf7681
```

원래 assignment resume은 구형 정책을 유지하므로 새 guard 수정까지 적용하는 동작은 아니다. 구형 workflow 실행 시 캐시가 다시 생길 수 있다. 기록 확인 후 실제 작업 재개에는 handoff와 새 중앙 inject 세션이 필요하다.

## admin-ui 실제 상태 복구 계약 — 적용 완료

원래 finish SHA:

```text
751ab6877d66dadd06ee7a326567aa3b5b4540f7ecebf43bccd8c822150ce4f1
```

복구 미리보기 SHA:

```text
e895183c167b7041d94997bbe5a34285bdf5df8a6caba26e0542a52d6a9cf264
```

계약 파일은 위 repository state의 `recoveries/e895183c167b7041d94997bbe5a34285bdf5df8a6caba26e0542a52d6a9cf264.json`이다. 2026-09-09 사용자의 이전 통합 소유권 해제 요청에 따라 이 계약을 적용했고 transaction journal은 `complete`다.

적용 내용:

1. 현재 sy-main HEAD `5834f920fcceadbe79491791d5cf8a35ca7e2a98` 및 모든 branch·worktree·파일을 보존한다.
2. `task/connect-news-api`와 `task/sign-in-page`를 `PRESERVED`로 기록한다. 원본 receipt와 검증 미완료 사실을 유지한다.
3. 원본 Codex 대화에서 실패가 확인된 pending patch 예약 2건만 취소한다.
4. 이전 Codex assignment의 해당 worktree Git claim과 sy-main 통합 예약을 해제한다.

취소 대상의 원본 대화 근거:

| call | 도구 결과 |
| --- | --- |
| exec-65b292de-76b0-4850-907b-5fcfcabfd364 | 00:06:48.634 KST, 동일 news.dto.ts에 중복 patch 작업을 적용하려다 실패 |
| exec-e8a3657a-a08b-4af4-b0ba-dfe42a7d2a08 | 00:58:41.373 KST, implementation-log.md의 기준 문맥을 찾지 못해 실패 |

아래 명령으로 적용했다. 실행 시 승인한 HEAD·metadata·소유권·pending 내용을 다시 확인했다.

```sh
bin/agent-policy integration-preserve --project admin-ui \
  --finish-file /Users/okand/SynologyDrive/asan-metaverse-admin-ui/.git/asan-agent-policy/finish-proposals/751ab6877d66dadd06ee7a326567aa3b5b4540f7ecebf43bccd8c822150ce4f1.json \
  --finish-sha256 751ab6877d66dadd06ee7a326567aa3b5b4540f7ecebf43bccd8c822150ce4f1 \
  --related-task task/sign-in-page \
  --cancel-call exec-65b292de-76b0-4850-907b-5fcfcabfd364 \
  --cancel-call exec-e8a3657a-a08b-4af4-b0ba-dfe42a7d2a08 \
  --reason '공지사항 사후 lint 실패와 로그인 화면 수동 병합을 보존하고 실패한 patch 예약 2건 및 worktree 통합 예약을 정리' \
  --approved-sha256 e895183c167b7041d94997bbe5a34285bdf5df8a6caba26e0542a52d6a9cf264
```

사후 확인에서 해당 worktree의 Git claim과 sy-main 통합 예약, 실패한 patch 예약 2건이 모두 제거됐고 두 task는 `PRESERVED`였다. sy-main HEAD와 두 task의 branch HEAD는 그대로이며 worktree는 clean이다. 원본 검증 기록을 보존했고 중앙 계약·admin-ui·user-ui audit도 모두 PASS였다.

이는 구형 `close-recover`의 검증 완료 cleanup 복구와 다른 계약이다. 보존 뒤 실제 검증 문제 해결과 정상 완료 workflow는 후속 작업으로 남는다. 앞서 준비한 user-ui close 복구도 이번에 적용하지 않았다.

### 이후 사용자 요청에 따른 수동 종료

2026-09-09 사용자가 두 task를 CLOSE로 변경하도록 직접 요청했다. 요청에 따라 `task/sign-in-page`와 `task/connect-news-api`의 metadata 및 종료 기록을 `CLOSED`로 전환했다. 이번 종료는 `closure_kind: user_requested`, `verification_status: incomplete`이며 기존 lint 실패와 검증 미완료 근거를 보존한다. 정상 검증 성공으로 기록하지 않았다.

종료 감사 SHA는 `51208fedc71e2b364d79b1d0a2f283461bab0d65a65f14e8117566ef1ca01204`이고 위 repository state의 `recoveries/<SHA>.json`에 적용 범위와 이전 receipt를 보관했다. transaction journal은 `complete`다. 두 task의 `.git/asan-agent-policy/closed/` 기록과 공지사항 통합 receipt에도 수동 종료 출처를 남겼다.

처음 확인한 sy-main checkout이 적용 전에 task/sign-in-page로 바뀌어 최초 적용은 쓰기 전에 중단됐다. 동일 HEAD·clean 상태와 새 claim·예약·미확인 도구가 없음을 재확인한 뒤 현재 checkout을 유지하는 감사 계약으로 적용했다. 최종 HEAD는 `5834f920fcceadbe79491791d5cf8a35ca7e2a98`이며 파일·branch HEAD·checkout을 변경하지 않았다. 사후 audit는 모두 PASS다.

이전 Git claim과 target 통합 예약은 앞선 보존 복구에서 이미 해제된 상태다. `CLOSED` metadata 자체가 예약을 자동 삭제하는 것은 아니다. 정상 `close`가 종료 기록, 해당 finish의 target 예약 제거, 동일 assignment의 source/통합 worktree claim 해제를 함께 수행한다.

소유권은 세 층으로 구분한다. task assignment는 branch와 scope에 대한 작업 권한이고, `git:<worktree 절대경로>` claim은 해당 폴더의 checkout·index·Git 변경을 한 assignment가 담당하도록 한다. 별도의 `integration-targets` 예약은 finish부터 verify·close까지 같은 target의 병합을 직렬화한다. 독립 task를 별도 worktree에서 구현하면 각 Git 작업 영역을 분리할 수 있다. 하나의 폴더에서 branch만 전환하면 Git 작업 영역을 공유하므로 같은 폴더에 대한 독점이 여전히 필요하다.

## 회귀 검증

수정 전에 실제 Git·bundle fixture로 실패를 확인한 뒤 중앙 원본을 수정했다.

- `tests/test_admin_runtime_fixes.py`: 두 host 원본 재개, 캐시 복구·변조 거부, 격리 이력 조회, 복합 workflow 차단, create 본문 소유권, 병합 후 자기 로그의 7개 테스트.
- `tests/test_integration_preserve.py`: 미리보기·보존·동일 SHA 재호출, HEAD/dirty/소유자 변경 거부, 부분 적용 복구, 후속 수동 task, 명시한 실패 call 취소의 5개 테스트.
- 기존 recovery 테스트: 검증 실패 receipt 기록 및 재검증 실패 후 close 차단을 확인하고, 하위 task 테스트를 실제 inject assignment 환경으로 정렬했다.

최종 `python3 -m unittest discover -s tests -v`는 213개 모두 통과했다(835.520초). 중앙 계약·admin-ui·user-ui의 `bin/agent-policy audit`는 모두 PASS이며 `git diff --check`도 통과했다. 회귀 사례 13개를 추가했고 기존 검증 실패·하위 task 테스트도 보강했다.

검증 기록:

- 수정 전 실패: `/private/tmp/asan-admin-fixes-red.log`, `/private/tmp/asan-integration-preserve-red.log`, `/private/tmp/asan-verification-record-red.log`, `/private/tmp/asan-reverification-red.log`
- 최종 전체 검사: `/private/tmp/asan-admin-fixes-verified-suite.log`
- 최종 audit: `/private/tmp/asan-admin-fixes-audit-final.log`
- 원본 세션 재개 사전 검사: `/private/tmp/asan-admin-resume-after-repair.log`, `/private/tmp/asan-admin-claude-resume-after-repair.log`
- 이번 작업만의 diff: `/private/tmp/asan-admin-runtime-fixes.diff` (작업 시작 시 복사본과 비교, 앞선 미커밋 변경 제외)

중앙 변경을 stage·commit·push하지 않았으며, 소비자 애플리케이션의 lint 실패를 수정하거나 검증 미완료 작업을 CLOSED로 변경하지 않았다.
