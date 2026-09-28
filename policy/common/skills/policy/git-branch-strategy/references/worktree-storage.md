# 워크트리 저장 위치와 보존 규칙

새 linked worktree를 생성하거나 기존 작업 공간을 이전할 때 읽는다. 설정 정본은 중앙 `projects/*.json`의 `worktree_root`이며, 현재 프로젝트 `{{PROJECT_NAME}}`의 저장 위치는 `{{WORKTREE_ROOT}}`다.

## 디렉토리 구조

```text
~/SynologyDrive/asan-worktrees/
├── asan-metaverse-user-ui-worktree/
│   ├── reservation-media-check/
│   └── vo-participant-status/
└── asan-metaverse-admin-ui-worktree/
    ├── inquiry-types-api/
    └── item-ui/
```

프로젝트 폴더는 전체 저장소 이름에 `-worktree`를 붙인다. 그 바로 아래에 작업별 폴더를 두며 프로젝트 ID·호스트·역할·세션별 중간 폴더는 만들지 않는다. 위 작업명은 구조 예시이며 실제 생성·이전 완료를 뜻하지 않는다.

각 작업 폴더는 같은 원본 Git 저장소에 연결된 worktree다. 별도 clone이나 폴더 복사로 만들지 않는다. 호스트·세션이 바뀌어도 같은 작업 공간을 이어 사용할 수 있다.

## 생성과 이름 충돌

- 현재 bundle의 `git_operations.py relation --action create --name <branch> --parent <직접 부모> --fork <부모 HEAD> --purpose <목적>`으로 준비한다. `--worktree`를 생략하면 설정된 프로젝트 폴더 아래의 경로를 계산해 승인 보고에 표시한다. 준비 단계에서는 디렉토리를 생성하지 않는다.
- 기본 작업명은 branch의 `task/`, `feature/`, `feat/`, `fix/`, `hotfix/`, `chore/`, `refactor/`, `docs/`, `test/` 접두어를 제거하고, 남은 `/` 등 구분자를 `-`로 바꾸어 소문자로 만든다. 예: `task/reservation/media` → `reservation-media`. 문자·숫자·`._-`는 유지하며 앞뒤 `._-`는 제거한다.
- 이름이 모호하거나 충돌하면 `--worktree "{{WORKTREE_ROOT}}/<구체적인 작업명>"`으로 명시한다. 폴더·심볼릭 링크가 이미 있거나 Git에 해당 경로가 등록돼 있으면 덮어쓰기·자동 번호 변경·강제 재사용을 하지 않는다. branch 이름을 바꿔도 기존 폴더를 자동으로 옮기지 않는다.
- 일반 `git worktree add`도 같은 위치 규칙을 따른다. 절대·상대 경로와 `git -C`의 실제 실행 위치를 해석하고, 준비 시점과 실행 직전에 검사한다. 새 경로는 프로젝트 저장 폴더 바로 아래여야 하며 다른 저장소나 기존 worktree와 겹칠 수 없다.
- `/tmp`, `/private/tmp`, `/var/tmp`, macOS의 `/var/folders` 계열, `TMPDIR`·`TMP`·`TEMP` 및 시스템 임시 디렉토리 아래에는 작업용 worktree를 생성하지 않는다. 심볼릭 링크의 실제 목적지도 검사한다. host sandbox의 쓰기 권한 때문에 임시 경로로 대체하지 말고 필요한 프로젝트 저장 경로의 권한을 요청한다.

## 보존과 정리

미완료 작업은 기간·접근 시각·세션 종료를 기준으로 자동 삭제하지 않는다. Git worktree 목록에서 `prunable`로 표시돼도 작업 완료나 파일 보존을 의미하지 않는다.

정리는 기존 Git 운영의 완료 검토·승인·검증·로그 보존 절차를 따른다. 미커밋 파일, untracked·ignored 파일과 모든 host의 세션 로그를 확인한다. `.env.local` 등 미보존 자료가 있으면 정리를 보류한다. 상위 프로젝트 폴더나 다른 작업 폴더까지 함께 지우지 않는다. 중앙 로그는 자동 삭제·stage·commit하지 않는다.

## 기존 워크트리의 이전·복구

위치 규칙은 새 생성에 적용한다. 기존 경로의 조회·편집·세션 재개를 막거나 시작 시 자동 이동하지 않는다.

1. 기본 저장소에서 `git worktree list --porcelain`을 읽고 각 경로의 실제 파일·`.git` 연결·branch·HEAD를 대조한다. 정상 공간, 일부 파일만 남은 공간, 사라진 공간을 구분한다.
2. 살아 있는 공간은 staged·unstaged·untracked·ignored 자료와 세션 로그를 확인한다. 해당 세션을 handoff하고 관련 편집·명령을 멈춘 뒤 원본·목적지·보존 범위를 명시한 이전 계획을 준비한다.
3. Git 연결 정보를 함께 갱신하는 이전을 사용한다. Finder 이동이나 파일 복사만으로 완료 처리하지 않는다. 현재 보호 실행기는 일반 `worktree move`·`repair`·`prune`를 허용하지 않으므로, 이 문서가 이동 권한이나 우회 승인을 부여하지 않는다. 구체적인 Git 이전·복구는 별도로 승인한 운영 절차로 수행한다.
4. 일부만 남았거나 사라진 공간은 남은 파일·branch·commit·중앙 로그·백업의 존재부터 확인한다. Git에 없는 미커밋 파일은 branch 재생성만으로 복구되지 않는다. 복구 상태를 확인하기 전에 `prune`, force 삭제 또는 같은 경로 재사용을 하지 않는다.
5. 이전 후 Git 연결·HEAD·파일 보존과 산출물 위치를 검증한다. 과거 중앙 로그는 이력으로 유지하고 새 handoff에 실제 목적지를 기록한다. 새 정책 적용은 중앙 launcher의 `start --project {{PROJECT_ID}} --host <host> --role <role> --worktree <확인한 새 경로>`로 한다. 기존 bundle의 `resume`은 새 위치 규칙 적용을 뜻하지 않는다.

저장 루트의 변경은 중앙 프로젝트 설정과 정책 검증을 거친다. 호스트별 복제 규칙이나 소비자 정책 사본을 추가하지 않는다.
