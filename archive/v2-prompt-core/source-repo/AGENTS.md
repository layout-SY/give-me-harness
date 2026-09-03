# AGENTS.md

## 역할

- 이 저장소는 `asan-metaverse-user-ui`와 `asan-metaverse-admin-ui`의 중앙 에이전트 정책 원본이다.
- 공통 정책은 `source/common/`, 호스트별 형식은 `source/hosts/`, 대상별 최소 사실은 `targets.json`에서 관리한다.
- 대상 프로젝트에 생성된 `AGENTS.md`, `.agents/`, `.codex/`, `.claude/`, `.opencode/` 파일을 직접 수정하지 않는다.

## 변경 절차

1. 변경하려는 정책이 두 프로젝트에서 같은 의미와 생명주기를 갖는지 확인한다.
2. 실제 원본과 인접 파일을 읽고 `source/` 아래 대응 파일만 수정한다.
3. `python3 -m unittest discover -s tests`를 실행한다.
4. `python3 bin/sync.py deploy --target all --dry-run`으로 두 프로젝트의 diff를 확인한다.
5. 사용자가 승인한 범위이면 `python3 bin/sync.py deploy --target all`로 배포한다.
6. `python3 bin/sync.py check --target all`이 정합인지 확인한다.
7. 실행 중이던 대상 프로젝트 세션을 handoff하고 새 세션을 시작한다.

## 최소화 원칙

- SQLite, 세션 registry, evidence 저장소, release channel 및 mutation state machine을 추가하지 않는다.
- 프로젝트별 overlay는 사용자가 별도로 요청하기 전까지 구현하지 않는다.
- 로그 문서를 런타임 판단의 원본으로 사용하지 않는다. 현재 파일과 Git 이력이 정책과 변경 기록의 기준이다.
- 공통 동작과 호스트 어댑터를 분리하며, 호스트 전용 형식을 공통 정책에 섞지 않는다.

## 명령어

- 테스트: `python3 -m unittest discover -s tests`
- 상태: `python3 bin/sync.py status`
- 검사: `python3 bin/sync.py check --target all`
- dry-run: `python3 bin/sync.py deploy --target all --dry-run`
- 배포: `python3 bin/sync.py deploy --target all`
- 시작: `python3 bin/sync.py start --target <user-ui|admin-ui> --host <codex|claude|opencode>`

## 승인

- 사용자 승인 전에는 중앙 원본이나 대상 프로젝트를 수정하지 않는다.
- 소비 프로젝트에서 정책 수정 요청이 발생하면 중앙 저장소로 이동해야 한다는 안내만 제공한다.

