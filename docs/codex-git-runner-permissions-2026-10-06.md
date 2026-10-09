# Codex 중앙 Git 보호 실행기의 쓰기 권한 복구

## 발생한 문제와 원인

user-ui의 `virtual-office-live-api` 세션에서 `git_operations.py relation --action create`가 중앙 `state/repositories/<repository>/branch-relations/v1/operations/.state-*` 파일을 만들다가 `Operation not permitted`로 중단됐다. 작업 준비 기록을 저장하지 못했으므로 브랜치·worktree 생성 단계에는 도달하지 않았다.

중앙 정책의 **Git 작업 승인**, Codex의 **명령 실행 규칙**, OS **파일시스템 sandbox**는 서로 다른 경계다. 기존 PreToolUse 훅은 중앙 상태를 기록할 수 있지만, 모델이 요청한 shell에서 실행하는 같은 보호 실행기는 소비자 프로젝트의 sandbox 안에서 동작했다. launcher의 쓰기 경로에는 소비자 프로젝트·연결 worktree와 설정된 worktree 저장 위치가 들어 있고 중앙 상태는 제외돼 있었다. `approval_policy=never`인 세션에서는 이 차이를 추가 승인으로 보완하지도 못했다.

기존 자동 테스트는 보호 실행기를 일반 subprocess로 실행했다. Git 승인·작업 위치 검사는 검증했지만 실제 Codex가 적용하는 OS sandbox를 통과하는지는 검증하지 못했다. 따라서 실패한 예약을 복구해도 다음 중앙 기록 저장에서 문제가 반복됐다. 이 오류만으로 macOS 계정의 디스크 권한 또는 SynologyDrive 권한이 손상됐다고 결론 내릴 수 없다.

## 변경 전후

| 항목 | 기존 방식 | 변경 방식 |
| --- | --- | --- |
| 중앙 작업 기록 | 일반 sandbox shell의 보호 실행기가 저장하다 실패 | 현재 번들의 보호 실행기에 Codex native 실행 예외를 등록 |
| 예외 위치 | 없음 | assignment별 `CODEX_HOME/rules/asan-git-operations.rules` |
| 실행 범위 | 준비가 허용돼도 OS 쓰기는 실패 | `python3` 또는 launcher Python의 절대 경로 + `-I` + 현재 번들 `git_operations.py` 절대 경로 + 지원 subcommand만 매칭 |
| 명시적 작업 위치 | `cd -- <cwd> && <runner> execute <id>` | 같은 명령 형식을 유지하며 `cd --` segment도 허용 |
| 실제 Git 승인 | PreToolUse 승인 후 operation grant 발급 | 그대로 유지. native 규칙은 중앙 Git 승인을 대신하지 않음 |
| 중앙 상태 직접 쓰기 | 일반 명령에서는 금지 | 그대로 금지. 중앙 state를 writable root로 추가하지 않음 |
| 관리 파일 무결성 | hooks·skills 등 해시 검사 | rules 파일도 같은 manifest에 포함해 변경·누락 검사 |

`lib/agent_policy/injection.py`의 기존 `_prepare_codex_home`와 `_install_state_files`를 재사용했다. 별도 daemon, 권한 복구 서비스, 상태 복사본 또는 per-tool 파일 스캔을 추가하지 않았다. 세션 시작 시 두 규칙을 생성하고 이후 명령 판정은 Codex가 수행한다. Claude·OpenCode adapter와 프로젝트 경로 설정은 변경하지 않았다.

허용 subcommand는 `prepare`, `review`, `complete`, `cleanup`, `relation`, `show`, `graph`, `writes`, `write-recovery`, `execute`, `recover`다. 다른 번들·복사한 실행기·`python -c`·`-I` 없는 실행은 이 규칙으로 허용되지 않는다. `cd --`는 보호 명령의 기존 작업 위치 지정 형식을 지원한다. 후속 명령 전체에 권한을 부여하는 규칙이 아니며, 임의 Python 쓰기와 연결해도 sandbox가 유지되는지 실제 CLI로 검사한다.

Codex의 `allow` 규칙은 매칭 명령을 sandbox 밖에서 실행한다. 이는 특정 디렉터리의 쓰기 권한만 추가하는 방식보다 프로세스 권한 범위가 넓다. 따라서 예외 대상은 중앙에서 생성한 정확한 실행기 경로로 제한하고, 그 실행기의 대상·승인·fingerprint·프로젝트 경계 검사를 유지한다. `-I`로 Python 환경 변수와 사용자 import 경로의 영향을 제외한다. 규칙 파일은 소비자 쓰기 경로 밖의 관리 home에 둔다. 공식 동작 근거는 [OpenAI 실행 규칙 문서](https://learn.chatgpt.com/docs/agent-configuration/rules)를 따른다.

## 기존 목적이 유지되는지

| 기존 목적 | 유지 방법과 검증 |
| --- | --- |
| 사용자 승인 없는 Git 변경 방지 | PreToolUse와 `git_operations.execute`의 grant·동의 검사를 변경하지 않았다. native smoke에서 승인 전 실행이 거절되고 승인 후에만 실행됨을 검사한다. |
| 승인한 대상·변경만 실행 | 기존 fingerprint와 실행 직전 HEAD/index/관계 재검사, 철회·다른 assignment 차단 테스트를 유지한다. |
| 같은 프로젝트의 worktree 공유 접근 | `cd --` 명령과 기존 workdir 해석을 유지한다. 세션별 branch 독점 권한을 추가하지 않는다. |
| 다른 프로젝트 보호 | 기존 command boundary와 Git common directory 검사를 유지한다. 작업 위치 전달 회귀 테스트도 그대로 실행한다. |
| 다른 세션의 plan·handoff 보호 | 로그 소유권·허용 필수 구간 검사 코드를 변경하지 않았다. 중앙 state의 shell 예외는 소비자 산출물의 일반 쓰기 권한이 아니다. |
| 실패 기록을 성공으로 오인하지 않음 | 쓰기 예약·format/검증 결과 처리에는 변경이 없다. 기존 미확인 예약은 별도의 근거 확인과 복구가 필요하다. |
| `/resume` 이력과 승인 분리 | 대화 공유·assignment별 home·승인 상태 분리 코드는 유지한다. 새 rules는 해당 home에만 생성한다. |
| 기존 실행의 재현성 | 실행 중인 home·불변 bundle을 덮어쓰지 않는다. 이전 assignment 재개는 이전 정책 그대로다. |

## 앞선 문제와 이번 수정의 범위

- `plan.md`의 `rejected by user approval settings`: 소비자 `.codex` 보호 경로의 native 쓰기 권한과 세션 로그 정책을 각각 확인해야 한다. 앞서 부여한 단일 문서의 임시 권한은 그 실행에만 해당하며 이번 규칙이 다른 세션의 plan 전체 쓰기를 허용하지 않는다.
- 실패한 패치의 미확인 기록: 원본 호출과 거절·성공 증거를 대조해 예약을 복구하는 문제다. 이전 기록 복구는 해당 사고를 정리했지만 이후 보호 실행기의 중앙 쓰기 권한까지 해결한 것은 아니었다.
- 이번 `branch-relations/v1/operations` 실패: 정상 보호 실행 경로에 필요한 native 실행 예외가 없었던 launcher 결함이다. 이번 변경으로 새 실행에 그 예외를 제공한다.

## 검증

`tests/test_injection.py::test_codex_protected_runner_has_narrow_managed_execution_rule`을 먼저 추가해 수정 전 rules 누락으로 실패함을 확인했다. 수정 후 규칙의 정확한 경로·`-I`·subcommand 범위와 rules 변조 시 home 진단 실패를 확인한다.

`tests/smoke_codex_git_sandbox.py`는 설치된 Codex와 로컬 Responses fixture를 사용한다. 외부 모델이나 실제 소비자 작업을 호출하지 않는다. 임시 저장소는 중앙의 Git 제외 경로에 만들며 상위 저장소를 탐색하지 않도록 Git ceiling을 설정한다. 임시 hook trust 예외는 테스트 recorder에만 적용하고, Git 승인에는 실제 중앙 UserPromptSubmit·PreToolUse 훅을 사용한다. 운영 launcher에 hook trust 예외를 추가하지 않는다.

검사 항목:

1. 같은 명령을 `--ignore-rules`로 실행하면 중앙 작업 기록 저장이 OS 권한 오류로 실패한다.
2. 관리 rules를 로드하면 `relation create` 준비 기록이 저장된다.
3. Git 승인 전 `execute`는 거절되며 branch·worktree를 만들지 않는다.
4. fixture에서 명시적 Git 승인을 전달한 뒤 같은 operation을 실행하면 branch·worktree가 생성된다.
5. 훅을 끈 부정 검사에서도 일반 Python의 중앙 state 쓰기는 직접 호출과 `cd -- … &&` 호출 모두 OS sandbox에 차단된다.
6. 실제 `codex execpolicy check`로 정상 호출 세 가지와 잘못된 호출 네 가지를 구분한다.

설치된 `codex-cli 0.160.1`에서 위 native 검사 전부 통과했다. 규칙을 제외한 동일 명령의 실패, 승인 전 미생성, 승인 후 `task/native-sandbox`의 실제 linked worktree 생성, 일반 쓰기 두 종류의 `Operation not permitted`, 규칙 검사 7건을 확인했다. 사용자 config를 symlink로 연결하는 운영 구조에서도 동일하게 통과했다.

최종 검증 결과:

| 검증 | 결과 |
| --- | --- |
| `python3 -m unittest discover -s tests -v` | 416개 PASS, 1912.311초 |
| 최종 실행 규칙 반영 후 `test_injection.py` 별도 실행 | 33개 PASS |
| 실제 Codex sandbox·hook·승인·worktree 생성 smoke | PASS |
| 실제 `codex execpolicy check` | 정상 호출 3건 허용, 잘못된 호출 4건 규칙 불일치 |
| `bin/agent-policy audit` | central-contract·admin-ui(296 files)·user-ui(226 files) PASS |
| `git diff --check` | PASS |

회귀 범위에는 기존 Git 승인·철회·fingerprint, 명시적 workdir, 프로젝트 경계, 다른 세션 로그 보호, 실패한 쓰기·포맷 결과 처리, native 대화 공유와 assignment별 설정 분리가 포함된다. 권한 오류를 없애기 위해 이 검사들을 비활성화하거나 승인 결과를 강제로 성공 처리하지 않았다.

실제 user-ui에 대해서도 `start --print-only`로 새 번들·home을 준비했다. 준비 assignment는 `d56ad1f691344dc9bf8fd9b15504aecf`, bundle digest는 `ad4a72837dce78501a09d7ab87ee5dc6f467f52390864f7865485c82a9433c49`다. 정확한 번들 실행 경로의 rules 생성과 home 무결성 진단 통과, 중앙 state가 `--add-dir`에 들어가지 않음을 확인했다. 이 검사는 미리보기이며 실제 사용자 세션을 시작하거나 기존 세션을 종료하지 않았다.

재현 명령:

```sh
python3 -m unittest discover -s tests -v
python3 tests/smoke_codex_git_sandbox.py --output-dir /private/tmp/codex-git-sandbox
bin/agent-policy audit
git diff --check
```

native smoke는 로컬 HTTP fixture와 실제 OS sandbox를 실행하므로 이를 허용하는 실행 환경이 필요하다. 바깥쪽 sandbox가 로컬 서버 바인딩이나 중첩 sandbox를 거절하면 이 검사만 해당 경계 밖에서 실행한다. 성공한 native 결과를 일반 subprocess 단위 테스트 결과로 대체하지 않는다.

## 적용과 작업 인계

새 중앙 `start`에 적용된다. 실행 중인 세션은 rules를 다시 읽지 않으므로 오류 난 명령만 반복하지 않는다. 기존 작업의 변경 파일·준비 여부·미완료 검증을 handoff하고 기존 실행을 종료한 다음 새 중앙 실행을 시작한다.

```sh
bin/agent-policy start --project user-ui --host codex --role logic
```

새 Codex에서 `/resume`으로 이전 대화를 선택하면 새 launcher의 정책을 사용한다. `--resume-assignment`나 중앙 `resume`으로 원래 assignment를 재개하는 방식은 원래 bundle·home을 보존하므로 이번 수정의 적용 방법이 아니다. 새 실행은 과거 Git 승인을 복제하지 않으므로 실제 Git 변경의 대상·영향은 현재 세션에서 확인한다.

이번 중앙 수정 과정에서 실제 `task/virtual-office-live-api` branch·worktree를 생성하거나 소비자의 미커밋 코드를 이동하지 않는다. 이 문서는 그 작업을 다시 시도할 세션에 넘길 권한 문제의 handoff도 겸한다. `plan.md`의 기존 임시 쓰기 예외 역시 새 세션으로 자동 복제하지 않는다.

## 2026-10-08 재확인: 보고 이후 달라진 실제 상태

사용자가 다시 전달한 “중앙 operations 쓰기 실패·sy-main에 변경 보존·worktree 미생성” 보고를 기준으로 현재 파일과 중앙 작업 기록을 읽기 전용으로 대조했다. 위 구현·검증 완료는 새 launcher의 동작 검증이며, 오류가 났던 기존 프로세스의 실행 환경을 직접 복구했다는 뜻은 아니다.

- 기존 Codex assignment `4146a0eb84f743d49009232e814b78ed`는 이전 `9dd86652…` bundle을 사용하며 해당 home에는 `rules/asan-git-operations.rules`가 없다. 이 home을 그대로 재개하는 것으로 새 규칙이 설치됐다고 볼 수 없다.
- 이후 준비한 assignment `6c76c9b8c0044173b90ed997bdda254f`에는 `ad4a7283…` bundle의 실행 규칙이 있다. 다만 assignment 기록에 `native_session`이 없으므로 준비만으로 그 설정의 사용자 세션이 실제 시작됐다고 간주하지 않는다.
- 중앙 operation `f6eae2846e5a4a5ba7dc6cbb536a9c63`은 `relation create`, `stage=done`이다. 생성 준비 시각은 2026-10-06 15:43:07 UTC이며 실제 승인·실행 주체는 Claude assignment `d8749968012c41fe80cf5fa198a32b0a`다. 이를 Codex 실행 규칙 적용 성공의 증거로 사용하지 않는다.
- 실제 `task/virtual-office-live-api`와 `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-user-ui-worktree/virtual-office-live-api`가 존재한다. HEAD는 `77362c6a4e8aa87e6c1c57daa183f0016e7d1538`이고 `ac06d07`·`4bd5e27`·`77362c6`에 문서·UI·API 작업이 기록돼 있다. 재확인 시 원본과 새 worktree의 `git status --short`는 모두 비어 있다.
- 같은 기존 Codex assignment의 후속 `write-recovery` operation `16277a3f4c094d8ab912476280df9dba`도 `stage=done`이다. 승인·실행 시각은 2026-10-06 16:09:55 UTC, native session은 `01a1073b-2a0d-7ac2-8afe-9701dc12c745`다. 적어도 그 후속 실행에서는 중앙 작업 기록 저장과 실행이 성공했다. 이 사실만으로 현재 프로세스의 모든 명령이 허용된다고 일반화하지 않는다.

소비자의 최신 `plan.md`도 코드의 worktree 이동·커밋 완료와 후속 쓰기 기록 복구를 명시한다. 원본 checkout의 과거 Stop 포맷 기록 불일치는 별도 문제로 남겨져 있으며 이번 operations 권한 오류와 혼동하지 않는다.

이번 재확인에서는 이미 완료된 branch 생성·파일 이동·예약 복구를 반복하지 않았고, 실행 중인 세션의 권한이나 소비자 파일을 변경하지 않았다. 현재도 새 권한 오류가 있다면 실제 대상 세션과 실패 호출을 먼저 특정해야 한다. rules는 시작 시 로드되므로, 파일 생성만으로 실행 중인 프로세스의 권한이 바뀌었다고 보고하지 않는다([OpenAI 공식 실행 규칙 문서](https://learn.chatgpt.com/docs/agent-configuration/rules)).
