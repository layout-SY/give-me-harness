# asan-agent-policy 운영 지침

이 저장소는 `asan-metaverse-user-ui`와 `asan-metaverse-admin-ui`의 AI 정책 원본이다. 소비자 저장소의 생성 파일을 직접 수정하지 않고 여기에서 원본을 변경한다.

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
- 소비자별 기능 정책은 V1 범위에 없으며 임의 overlay를 만들지 않는다.

## 안전 규칙

- `asan-prompt-core`, 그 백업, `asan-harness`를 원본으로 읽거나 복사하지 않는다.
- manifest에 기록되지 않은 소비자 파일을 삭제하지 않는다.
- legacy 파일은 감사 시 고정한 SHA-256과 일치하고 `--retire-legacy`가 명시된 경우에만 퇴역한다.
- 모델 이름은 정책과 분리한다. 호스트와 모델은 `start`의 독립 인자다.

## 커밋 메시지

- Conventional Commit type은 영어 소문자(`feat`, `fix`, `refactor`, `chore`, `docs`, `test`)로 작성한다.
- colon 뒤의 요약과 필요한 본문은 한글로 작성한다.
- 예: `feat: 중앙 에이전트 정책 프로젝트 구축`
