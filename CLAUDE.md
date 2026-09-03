# asan-agent-policy — Claude Code 운영 계약

이 저장소는 `asan-metaverse-user-ui`와 `asan-metaverse-admin-ui`의 AI 정책 중앙 원본이다. Claude Code는 실행 호스트일 뿐 특정 작업 역할을 기본 소유하지 않는다. 공통 역할과 구현 책임의 정본은 `policy/common/`, 기계적 차단은 `policy/guards/`, Claude 형식은 `adapters/claude/`에 둔다.

## 역할과 승인

- 사용자 요청과 handoff에서 필요한 역할을 판단한다. inject system prompt에 `--role`이 있으면 해당 값은 이미 확인된 세션 역할이다.
- role이 없는 세션에서는 역할, 수정 범위, 필요한 정책·스킬, Git 통합 담당자와 검증 계획을 제안하고 승인을 기다린다.
- 조사 결과와 예상 diff를 제시한 뒤 명시적인 승인 전에는 중앙 원본을 수정하지 않는다.
- 역할이나 scope가 바뀌면 다시 보고한다. 특정 역할을 Claude Code의 고정 책임으로 문서화하지 않는다.

## 중앙 저장소 작업 흐름

1. `policy/`, `adapters/`, `projects/`, `lib/`, `tests/`의 영향을 조사한다.
2. 기존 공통 문서와 renderer를 재사용하고 호스트별 중복 정본을 만들지 않는다.
3. 승인 후 중앙 원본과 테스트만 수정한다.
4. `python3 -m unittest discover -s tests -v`와 `bin/agent-policy audit`를 실행한다.
5. `bin/agent-policy diff --project all`의 소비자 예상 변경을 사용자에게 제시한다.
6. 소비자 배포는 별도 승인을 받은 뒤 `bin/agent-policy sync --project all`로만 수행한다.
7. 배포 후 실행 중이던 소비자 세션은 handoff하고 새 세션으로 시작한다.

## 소유권과 안전

- 공통 정책: `policy/common/`
- guard와 drift 검사: `policy/guards/`
- 호스트 형식: `adapters/codex/`, `adapters/claude/`, `adapters/opencode/`
- 프로젝트 경로와 명령: `projects/*.json`
- 중앙 산출물 archive: `logs/projects/{project}/{host}/sessions/`
- 소비자 저장소의 생성 파일을 직접 수정하거나 manifest 밖 파일을 삭제하지 않는다.
- legacy 파일은 감사 SHA-256과 일치하고 `--retire-legacy`가 명시된 경우에만 퇴역한다.
- 모델 이름은 정책과 분리하고 `start --host`와 `--model`의 독립 인자로 유지한다.
- 활성 로그 원본은 소비자 worktree에 두고 중앙 로그는 추가·변경만 반영하는 Git 사본으로 관리한다.
- 중앙 로그를 자동 삭제하거나 Git add·commit하지 않는다. `logs/**`만 변경된 상태는 sync 청결 판정에서 제외한다.
- 이전 세대 정책 저장소와 백업은 정책 정본으로 읽거나 복사하지 않는다. `archive/**`로의 세대 보존은 사용자 승인이 있을 때 한 번 수행하는 예외이며, 보존된 내용은 렌더·sync·판정에 사용하지 않는다.

## Claude Code 도구

- 세션 산출물의 최초 쓰기는 Bash heredoc이나 redirect가 아니라 `Write`를 사용한다.
- `git checkout -- <path>` 대신 `git restore ... -- <path>`를 사용한다.
- branch 전환과 merge는 분리 실행한다.
- 사용자 승인 UI가 필요한 명령은 hook 결정을 따르고 차단을 우회하지 않는다.

## 커밋 메시지

- Conventional Commit type은 영어 소문자(`feat`, `fix`, `refactor`, `chore`, `docs`, `test`)를 사용한다.
- colon 뒤 요약과 필요한 본문은 한국어로 작성한다.
- 예: `feat: 중앙 에이전트 정책 프로젝트 구축`
