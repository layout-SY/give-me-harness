# 세션 재개와 원본 보존

## 프로젝트 이력 선택

중앙 저장소에서 실행한다. 목록 조회와 재개 미리보기는 assignment나 대화 파일을 생성하지 않는다.

```sh
bin/agent-policy sessions --project user-ui --host codex
bin/agent-policy resume --project user-ui --host codex
bin/agent-policy resume --project user-ui --host codex --assignment <assignment-id> --print-only
```

대화 변경 시각을 기준으로 정렬하며 역할·과거 branch 상태는 참고 정보다. 원래 native ID·정책 bundle·Codex home을 함께 선택한다. 내장 `/resume`은 해당 home 안에서 동작한다. 서로 다른 역할의 home 전체나 hooks·승인 상태를 공유하지 않는다. 비대화형 실행은 `--assignment`를 지정한다. 기존 `start --resume-assignment`도 같은 검증을 사용한다.

`bundle 정상`만으로 재개 가능하다고 판정하지 않는다. 프로젝트·worktree·native ID·대화 메타데이터·정책 원본·home의 관리 파일·인계 상태를 함께 확인하고 실행 직전에 다시 검사한다. 현재 중앙 정책의 변경 여부는 비교 정보로 표시한다. 현재 소스 audit가 실패해도 원래 bundle 자체를 정상 검증할 수 있는 기존 재개는 허용한다. 소비자 정책 사본 충돌 검사는 유지한다.

## 작업 위치 변경

```sh
bin/agent-policy resume --project user-ui --host codex --assignment <assignment-id> --worktree /absolute/existing/worktree
```

신규 V4 bundle의 프로젝트 기준은 Git의 primary worktree다. 실제 작업 cwd는 별개이므로 기능 worktree를 제거한 뒤에도 같은 저장소의 기존 경로를 선택해 재개할 수 있다. Codex에는 선택 경로를 `--cd`로 명시한다. 이력이나 대화를 branch 소유권으로 사용하지 않는다. 브랜치 관계·병합 순서·명령 승인은 기존 작업 정책을 따른다.

과거 bundle은 생성 당시 경로가 guard에 고정되어 있을 수 있다. 삭제된 옛 기준 경로 때문에 실행할 수 없으면 `policy_anchor_missing`으로 안내하며, 환경변수만 변경해서 정상 재개로 가장하지 않는다. 원래 경로/원본을 복구하거나 아래 기록 인계 절차를 사용한다. 현재 구조도 primary worktree 자체의 이동·삭제를 자동 복구하지는 않는다.

## native ID 미연결

ID가 비어 있으면 실행 전이라고 단정하지 않는다. home의 `sessions/`와 `archived_sessions/`에서 `session_meta`를 읽어 후보를 표시한다. 파일명만으로 연결하거나 다른 대화로 자동 대체하지 않는다.

```sh
bin/agent-policy session-link --project user-ui --assignment <assignment-id> --native-session <확인한-native-id>
```

선택한 ID가 해당 home에서 유일하고 최초 cwd도 assignment와 일치해야 한다. 원래 assignment를 백업한 뒤 연결한다. 인계된 기록이나 이미 ID가 연결된 기록은 변경하지 않는다. 연결은 재개를 보장하지 않으며 bundle·home·경로는 별도로 검증한다.

## 정책 보존과 복구

신규 기본 경로는 `state/bundles/{project}/{host}-{role}-{digest}/`다. 같은 저장소·host·role·정책은 primary worktree 기준으로 동일 bundle을 공유한다. 대화와 정책 원본은 worktree 완료·삭제 대상이 아니다. `state/`는 지속 데이터이며 build 캐시 정리 대상에 포함하지 않는다.

기존 `build/` 원본은 유효한 동안 보존한다. 아래 명령은 manifest에 있는 정책 파일만 복사하며 node_modules 등 재생성 가능한 실행 의존성은 백업하지 않는다. 동일 bundle·원래 경로의 백업은 한 번만 저장한다.

```sh
bin/agent-policy bundle-preserve --project user-ui --assignment <assignment-id>
bin/agent-policy bundle-repair --project user-ui --assignment <assignment-id>
```

`bundle-preserve`는 원본 manifest와 파일 해시를 검증하고 복구용 manifest 해시를 assignment에 기록한다. `bundle-repair`는 bundle 전체가 없는 경우 검증된 백업을 **원래 절대경로와 동일한 바이트**로 복원한다. 기존 경로를 덮어쓰거나 최신 정책으로 재생성하지 않는다. Python 생성 캐시만 오염된 기존 복구 방식도 유지한다. 다른 파일 누락·변경은 자동 덮어쓰지 않는다.

## 이미 누락된 기록

| 발견한 자료 | 조치 |
| --- | --- |
| 대화·정책·home 정상 | 원래 대화 재개 |
| 대화 있음, 정책 누락, 검증된 백업 있음 | bundle-repair 후 재개 조건 재검사 |
| 대화 있음, 원본 정책 복구 불가 | 대화 경로를 열람하고 기존 작업 기록과 함께 새 세션에 인계 |
| native ID만 있고 대화 없음 | 원래 home의 조사 결과를 표시; 확인한 백업 없이는 대화를 복원했다고 보고하지 않음 |
| 실행 위치만 없음 | 같은 저장소의 기존 worktree를 명시하여 재검사 |

새 정책으로 인계하려면 목록에 표시된 대화 원본과 기존 프로젝트 handoff를 검토한다. 인계 대상 저장소·branch·worktree·현재 HEAD, 원래 작업 목적, 미완료 변경, UI/Logic 역할별 다음 작업·검증 방법을 작성하고 다음처럼 새 실행을 선택한다.

```sh
bin/agent-policy start --project user-ui --host codex --role logic --worktree /absolute/existing/worktree
```

새 세션에 인계 문서 위치와 이전 대화 경로를 전달한다. 이는 원래 대화의 동일 정책 재개와 구분하며 기존 native 이력·assignment·승인을 덮어쓰거나 다른 세션으로 복제하지 않는다. 단순 commit/merge만 수행하는 요청은 별도 필수 산출물을 생성하지 않는 기존 예외를 유지한다.

## 검증과 적용 범위

회귀 검증은 누락 bundle·대화·경로, native 미연결, home 변경, 정책 백업 복구, 읽기 전용 목록, 역할별 home 선택, 작업 worktree 삭제 후 실제 guard 실행을 포함한다. 새 bundle의 경로 분리는 새 start부터 적용되며 과거 정책 파일은 수정하지 않는다.
