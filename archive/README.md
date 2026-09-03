# 정책 세대 아카이브

이 디렉터리는 현재 중앙 정책(V3)에 앞선 세대의 파일을 **있는 그대로 보존한 기록**이다.

## 정본이 아니다

- 렌더, `sync`, `audit`, guard 판정의 대상이 아니다. `bin/agent-policy`는 이 경로를 읽지 않는다.
- 여기 있는 문구, 역할 배정, 호스트 고정 표현은 현재 운영 계약과 충돌한다. 참조하지 않는다.
- 현재 계약의 정본은 `policy/common/`, `policy/guards/`, `adapters/`다.
- 파일 수정, 정리, 재포맷을 하지 않는다. 기록으로서의 가치는 원형 유지에 있다.

## 세대 구분

| 세대 | 내용 | 원본 위치 |
| --- | --- | --- |
| V1 | `asan-prompt-core` 배포 이전, `admin-ui`에만 존재하던 수작업 세대 | `archive/v1-admin-ui-pre-core/` |
| V2 | `asan-prompt-core`가 `bin/sync.py deploy`로 관리하던 세대 | `archive/v2-prompt-core/` |
| V3 | 현재 중앙 저장소 | 저장소 루트 (아카이브 아님) |

## V1 판별 근거

`admin-ui`의 정책 파일 중 다음 두 조건을 모두 만족하는 122개를 V1으로 분류했다.

1. `asan-prompt-core`의 배포 헤더 주석이 없다.
2. `user-ui`에 같은 경로가 없거나 내용이 다르다. 두 소비자에 바이트 동일하게 존재하는 파일은 V2 배포 세대로 보았다.

특징은 다음과 같다.

- 프로젝트명이 현재와 다른 `synthoria-admin-ui`로 기록되어 있다.
- `.agents/skills/reference/**`와 `.claude/skills/reference/**`가 43쌍 중 7쌍만 일치한다. 손으로 두 번 복제된 흔적이다.
- `user-ui`에는 이 세대가 존재하지 않는다.

`MANIFEST.sha256`은 복사 시점의 무결성 기록이다.

## 제외한 파일

- `admin-ui`의 `.claude/settings.local.json`: 사용자 전역 Git ignore가 `**/.claude/settings.local.json`을 대상으로 하고 있어 아카이브에 포함하지 않았다. 개인 권한 설정이며 정책 세대 판별에 필요하지 않다.
- `__pycache__/**`와 `.DS_Store`: 생성물이다.

## V2 판별 근거

두 소비자에 배포된 정책 파일 중 97개가 `asan-prompt-core` 배포 헤더를 갖고 있고 그중 95개가
바이트 동일하다. 배포 헤더가 없는 `templates/`, `memory/` 계열도 두 소비자에 바이트 동일하게
존재해 같은 세대로 분류했다. 즉 소비자에 있던 대부분은 이 세대의 배포 산출물이다.

`archive/v2-prompt-core/`의 구성은 다음과 같다.

- `deployed/user-ui/`, `deployed/admin-ui/`: 삭제 직전 소비자 정책 디렉터리 전량 스냅샷.
  세션 산출물 로그를 포함한다. `collect-logs`는 정해진 8종과 `handoff.md`, `unknown/`만
  수집하므로 그 밖의 이름을 가진 기록 9건은 이 스냅샷에만 남는다.
- `source-repo/`: 원본 저장소 작업 트리. 생성물인 `build/`, `state/`와 `.git/`은 제외한다.

`deployed/admin-ui/` 안에는 V1으로 분류한 파일도 그대로 들어 있다. `deployed/`는 삭제 시점의
있는 그대로의 스냅샷이고 `v1-admin-ui-pre-core/`는 세대 분류 추출본이다. 중복은 의도한 것이다.

원본 저장소는 커밋이 하나도 없는 상태였다. Git 이력으로 남은 세대 기록이 존재하지 않으므로
작업 트리 스냅샷이 유일한 보존 수단이다.

## 강제 포함한 파일

`deployed/*/.opencode/.gitignore`는 자기 자신과 `package.json`, `package-lock.json`을 무시하도록
작성되어 있어 복사 후에도 Git에서 제외됐다. 스냅샷 충실도를 위해 `git add -f`로 포함했다.
