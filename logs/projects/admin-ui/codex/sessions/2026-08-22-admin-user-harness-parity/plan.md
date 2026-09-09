# Admin/User 하네스 동일화 계획

## 목표

admin-ui의 prompt·Python governance harness를 user-ui와 동일한 구조와 실행 계약으로 통일하고, admin-ui에서 반복된 UI/CSS 소유권 침범과 브라우저·Watcher·이미지 QA를 Python Hook으로 차단한다.

## 범위

### 1. Prompt harness 동일화

- `AGENTS.md`를 user-ui의 간결한 운영 구조에 맞춘다.
- Hephaestus는 기능 로직과 테스트만 소유하고 production UI·CSS를 수정하지 않도록 명시한다.
- QA는 테스트 코드 작성·실행만 허용하고 browser automation, screenshot, image capture, visual QA, Watcher·별도 review agent 실행을 금지한다.
- `.codex/agents/`, `.codex/harness/`, `.codex/multi-agent-spec*`, `.codex/workflows/`, `.codex/templates/`, `.harness/roles/orchestration.md`의 구조와 상태 용어를 user-ui 기준으로 통일한다.
- admin 도메인 skill과 reusable asset 목록은 덮어쓰지 않는다.

### 2. Python governance harness 이식

- 먼저 user-ui의 governance 테스트 fixture와 테스트를 admin-ui에 이식해 기존 Hook에서 실패하는 red 상태를 확인한다.
- `hook_common.py`를 identity-bound v2 state, secure atomic write, canonical path, protected path 계약으로 교체한다.
- `track-user-prompt.py`를 exact approval match 방식으로 교체한다.
- `track-posttooluse.py`를 skill·shared UI/reference/reusable asset evidence 방식으로 교체한다.
- `enforce-pretooluse.py`를 read-only allowlist와 unclassified default-deny 방식으로 교체한다.
- `require-documentation-stop.py`를 bound session과 8개 산출물 검증 방식으로 교체한다.
- `.codex/hooks.json`에 entry + common SHA-256 bootstrap을 등록한다.

### 3. Admin 전용 hard deny

- CSS·style 파일과 production UI 경로 mutation은 승인 후에도 차단한다.
- Playwright, browser, screenshot, image capture, visual QA 도구 호출은 승인 후에도 차단한다.
- `task` 입력의 Watcher·review agent 실행은 승인 후에도 차단한다.
- Bash의 browser·capture 명령도 차단한다.
- 각 금지 규칙은 허용 조건과 다른 값을 사용하는 독립 회귀 테스트로 고정한다.

### 4. 테스트 명령 통합

- admin-ui에 Vitest 기반 application test command와 Python governance test command를 하나의 `npm test`로 연결한다.
- `package.json`, `package-lock.json`, `vitest.config.ts`만 test infrastructure 범위에서 수정한다.
- feature QA는 browser 대신 최소 test code로 검증하도록 prompt와 Hook 문서를 일치시킨다.

### 5. 이전 위반 산출물 정리

- 이 세션에서 생성한 root QA screenshot·browser 임시 산출물만 소유권을 확인한 뒤 제거한다.
- shared worktree의 사용자·다른 agent 변경과 기존 session 이력은 제거하지 않는다.

## TDD 순서

1. user-ui governance test suite와 admin 전용 금지 테스트를 추가한다.
2. 현 admin Hook에서 의도한 failure를 확인한다.
3. user-ui Hook core와 prompt 계약을 이식한다.
4. admin 전용 hard deny를 최소 코드로 추가한다.
5. Python governance suite와 application test suite만 실행한다.
6. browser, Watcher, image capture는 실행하지 않는다.

## 검증

```bash
python3 -I .codex/hooks/test_governance_hooks.py
npm test
```

- Python Hook 동작은 subprocess 회귀 테스트로만 검증한다.
- application 동작은 Vitest 테스트 코드로만 검증한다.
- lint·build는 정적 확인이며 QA evidence로 계산하지 않는다.

## 변경하지 않는 것

- `src/**` production application code
- 모든 CSS·style 파일
- 브라우저·Playwright 설정을 이용한 QA
- Watcher·visual QA·review agent 실행
- 이미지·스크린샷 생성

## 상태

- `hold_for_approval`
- 명시적 `진행`, `진행해줘`, `Proceed` 전에는 하네스 production 파일을 수정하지 않는다.
