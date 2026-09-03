# asan-agent-policy 운영 지침

이 저장소는 `asan-metaverse-user-ui`와 `asan-metaverse-admin-ui`의 AI 정책 원본이다. 소비자 저장소의 생성 파일을 직접 수정하지 않고 여기에서 원본을 변경한다.

호스트는 실행 환경이고 역할은 작업 책임이다. 특정 호스트에 UI, Logic 또는 오케스트레이션 역할을 고정하지 않는다. 새 요청에서 사용자 입력과 적용 가능한 handoff를 근거로 역할을 제안하고 확인받은 뒤 작업한다.

## 작업 흐름

1. `policy/`, `adapters/`, `projects/`의 영향을 조사한다.
2. 계획과 예상 diff를 제시하고 명시적인 승인을 받는다.
3. 중앙 원본과 테스트만 수정한다.
4. `python3 -m unittest discover -s tests -v`와 `bin/agent-policy audit`를 실행한다.
5. `bin/agent-policy diff --project all`을 사용자에게 제시한다.
6. 소비자 프로젝트 배포는 별도 승인을 받은 뒤 `bin/agent-policy sync --project all`로만 수행한다.
7. 실행 중이던 소비자 세션을 handoff하고 새 세션을 시작한다.

## 소유권

- 공통 정책: `policy/common/`
- 기계적 차단과 drift 검사: `policy/guards/`
- 호스트 형식: `adapters/codex/`, `adapters/claude/`, `adapters/opencode/`
- 프로젝트 경로와 명령: `projects/*.json`
- 필수 세션 산출물 아카이브: `logs/projects/{project}/{host}/sessions/`
- 소비자별 기능 정책은 V1 범위에 없으며 임의 overlay를 만들지 않는다.

## 안전 규칙

- `asan-prompt-core`, 그 백업, `asan-harness`를 원본으로 읽거나 복사하지 않는다.
- manifest에 기록되지 않은 소비자 파일을 삭제하지 않는다.
- legacy 파일은 감사 시 고정한 SHA-256과 일치하고 `--retire-legacy`가 명시된 경우에만 퇴역한다.
- 모델 이름은 정책과 분리한다. 호스트와 모델은 `start`의 독립 인자다.
- 활성 작업의 로그 원본은 소비자 프로젝트에 두고 중앙 로그는 추가·변경만 반영하는 Git 사본으로 관리한다.
- 중앙 로그를 자동 삭제하거나 Git add·commit하지 않는다. `logs/**`만 변경된 상태는 정책 source digest와 sync 청결 판정에서 제외한다.

## 커밋 메시지

- Conventional Commit type은 영어 소문자(`feat`, `fix`, `refactor`, `chore`, `docs`, `test`)로 작성한다.
- colon 뒤의 요약과 필요한 본문은 한글로 작성한다.
- 예: `feat: 중앙 에이전트 정책 프로젝트 구축`
