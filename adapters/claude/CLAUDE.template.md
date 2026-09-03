# Claude Code 호스트 계약

## 1. 공통 정책 진입점

- 사용자 지시 다음으로 `.agent-policy/common/AGENT_POLICY.md`의 호스트 중립 계약을 따른다.
- 역할 선택과 상세 책임은 `.agent-policy/common/skills/policy/task-role-routing/SKILL.md`와 그 `references/`에서 읽는다.
- branch·worktree 생명주기는 `.agent-policy/common/skills/policy/git-branch-strategy/SKILL.md`, 산출물은 `.agent-policy/common/skills/policy/documentation/SKILL.md`를 따른다.
- Claude Code는 실행 호스트이며 UI, Logic, 오케스트레이션 또는 Git 통합 권한을 자동으로 소유하지 않는다.
- 이 문서는 Claude Code의 도구, hook, native agent, 템플릿과 산출물 위치만 추가 정의한다. 공통 역할 책임을 재정의하지 않는다.

inject system prompt에 `--role`이 있으면 해당 값은 이번 세션에서 이미 확인된 역할이다. 같은 역할 범위에서는 다시 역할을 묻지 않는다. 다른 역할이 필요하면 범위를 확장하지 않고 새 role 세션을 요청한다. role 경계는 system prompt 계약이며 별도 감시 hook을 전제로 하지 않는다.

## 2. 작성 언어

- 사용자 응답, 계획과 모든 문서 산출물은 한국어로 작성한다.
- 하위 에이전트 지시와 결과에도 같은 원칙을 적용한다.
- 코드 식별자, 명령어, API 필드명과 라이브러리 고유명은 필요한 경우 원문을 유지한다.

## 3. Claude Code 도구 규칙

- 세션 산출물의 최초 쓰기는 Bash heredoc·리다이렉션이 아니라 `Write` 도구로 수행한다. 이후 수정도 가능한 한 `Edit` 또는 `Write`로 경로를 구조적으로 전달한다.
- 읽기 전용 shell의 `2>&1`, `2>/dev/null`은 산출물 생성으로 취급하지 않는다. 일반 파일로 향하는 redirect는 실제 쓰기이므로 관리 파일·산출물 정책을 적용한다.
- 사용자 권한 UI가 필요한 명령은 중앙 `PreToolUse` hook의 `ask` 결정을 따른다. 차단을 우회하거나 같은 명령을 의미 없이 반복하지 않는다.
- `git checkout -- <path>` 대신 `git restore ... -- <path>`를 사용한다.
- branch 전환과 merge를 하나의 복합 shell 명령으로 결합하지 않는다.
- 정책 스냅샷의 branch workflow가 출력한 전체 SHA와 승인 요청 식별자를 그대로 사용한다.

## 4. 관리 정책 파일

`CLAUDE.md`, `.agent-policy/**`, manifest가 관리하는 `.claude/**`, 하네스·스킬·hook과 runtime 정책은 소비자 프로젝트에서 직접 수정하지 않는다.

정책 변경이 필요하면 중앙 원본 경로, 이유, 예상 diff와 sync·세션 재시작 필요 여부를 사용자에게 보고한다. 별도 sync 승인 전에는 소비자 사본을 우회 수정하지 않는다.

## 5. Claude 산출물과 handoff

- Claude Code 세션 산출물의 정본은 `.claude/logs/sessions/{YYYY-MM-DD-task-slug}/`다.
- 산출물 스키마는 `.claude/templates/`, 부분 역할 인계는 `.claude/templates/handoff.template.md`를 사용한다.
- 전체 작업 책임자는 공통 계약의 필수 산출물 8종을 작성하고, 부분 기여자는 `handoff.md`를 작성한다.
- handoff의 `next_role`은 다음 역할의 제안이며 자동 권한이 아니다.
- 같은 worktree의 Git 통합 담당자가 따로 있으면 branch, index, commit과 merge를 조작하지 않는다. Claude Code가 담당자로 확인된 경우에만 해당 Git 작업을 수행한다.

## 6. Claude native agent와 검증

- `.claude/agents/**`와 `.claude/skills/**`는 공통 역할을 실행하는 Claude native 형식이다. 역할·workflow·산출물 의미는 `.agent-policy/common/**`에서만 정의한다.
- 하위 에이전트는 inject role 또는 사용자에게 확인된 역할과 pipeline 계약 안에서만 사용한다.
- Planner와 Evaluator의 넓은 읽기 권한은 구현 파일 수정 권한을 만들지 않는다.
- Watcher는 현재 변경을 직접 읽고 판정하며 별도 리뷰 에이전트를 중첩 실행하지 않는다.
- 필요한 검증은 기존 테스트, `{{BUILD_COMMAND}}`, `{{LINT_COMMAND}}` 범위에서 수행한다.
- 이미지 캡처, GIF, 화면 비교와 시각 QA는 사용자가 요청하지 않는 한 실행하지 않는다.
