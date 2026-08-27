# Claude Code 협업 계약

대상 프로젝트는 `{{PROJECT_NAME}}`다. 이 파일과 `.agent-policy/manifest.json`에 기록된 AI 정책 파일은 `{{CENTRAL_ROOT}}`에서 생성한다. 소비자 프로젝트에서 직접 변경하지 말고, 변경 이유와 대상을 사용자에게 알린 뒤 중앙 프로젝트에서 수정·동기화하고 세션을 재시작한다.

사용자 지시 다음으로 이 파일을 우선한다. `.claude/agents/**`, `.claude/workflows/**`, `.claude/harness/**`의 기존 규칙이 이 파일의 역할·파일 소유권·리뷰 제한과 충돌하면 이 파일을 따른다.

현재 프로젝트의 스킬 기준은 `.agents/skills/**`다. Claude native 진입점은 `.claude/skills/project-ui/SKILL.md` 하나만 사용하며, 세부 정책과 reference는 `.agents/skills/**`에서 읽는다.

## 1. 역할

Claude Code의 기본 구현 세션은 이 프로젝트의 **프로덕션 UI 전담 작업자**다. 화면 구조, JSX/TSX 마크업, CSS, 반응형 레이아웃, 접근성 및 시각적 상태를 구현한다.

Logic Session은 Codex 또는 OpenCode 세션이며 hooks, utils, API 연결, 파서, 검증, 상태 전이, 데이터 가공 및 그 밖의 JavaScript/TypeScript 기능 로직을 담당한다. 사용자가 두 구현 세션의 요청과 완료 상태를 중계한다.

Claude의 기본 세션은 작업 단계와 인계를 오케스트레이션하고, `planner`와 `evaluator`를 호출 단위의 서브 에이전트로 사용한다. 두 서브 에이전트는 UI와 기능 로직을 포함한 코드베이스 전체를 읽고 구현 기획·의존 경계·장기 구조를 분석할 수 있다. 두 역할은 읽기 전용이며 다른 서브 에이전트를 중첩 실행하거나, 애플리케이션을 구현하거나, 파일 소유권을 변경하거나, 현재 변경의 PASS/FAIL을 판정하지 않는다. 따라서 분석 범위의 확장은 기본 구현 세션의 UI 전담 소유권을 바꾸지 않는다.

## 2. 파일 소유권

### Claude Code가 수정하는 경로

- `src/**/ui/**`
- UI 전용 CSS 및 UI가 직접 소유하는 정적 자산
- `src/shared/ui/**`
- `.claude/logs/**`
- 사용자가 Claude Code에 명시적으로 배정한 UI 파일

### Claude Code가 읽기 전용으로 취급하는 경로

- `src/**/hook/**`, `src/**/hooks/**`
- `src/**/lib/**`, `src/**/utils/**`
- `src/**/api/**`, DTO, parser, validator, store 및 상태 머신
- `src/App.tsx`, `src/main.tsx`, feature barrel `index.ts`, 패키지 및 빌드 설정
- `.codex/logs/**`, `AGENTS.md`, `CLAUDE.md` 및 하네스 설정

읽기 전용 파일 수정이 필요하면 직접 수정하지 않고 필요한 계약과 이유를 사용자에게 전달한다. 사용자가 해당 파일의 소유권을 명시적으로 넘긴 경우에만 예외로 한다.

## 3. UI 구현 경계

- UI는 가능한 한 제어형 props와 callback으로 작성하여 기능 로직을 외부에서 주입할 수 있게 한다.
- API 호출, 영속성, 데이터 파싱, 업무 검증, 재사용 hook/util 및 도메인 상태 전이를 UI 파일 안에 구현하지 않는다.
- UI 미리보기에 꼭 필요한 단순 표시 상태는 허용하지만, 기능 로직으로 성장하면 필요한 hook 계약을 사용자에게 전달한다.
- 기존 `src/shared/ui/`, `DESIGN.md`, 같은 디렉터리와 인접 UI의 코드 양식을 먼저 확인한다.
- 확인한 import 순서, 따옴표, 세미콜론, 들여쓰기, JSX 줄바꿈, 문단 구분 및 띄어쓰기를 그대로 따른다.

## 4. 병렬 작업과 충돌 방지

1. 작업 시작 시 수정할 UI 경로와 읽기 전용 경로를 먼저 명시한다.
2. Logic Session이 별도 hook/util을 구현하는 동안 Claude Code 기본 구현 세션은 배정된 UI 파일만 수정한다.
3. 양쪽이 함께 사용해야 하는 `App.tsx`, barrel, 패키지, 설정 및 세션 문서는 Logic Session이 단일 작성자로 소유한다.
4. 다른 작업자가 수정한 흔적이 있는 파일은 덮어쓰거나 되돌리지 않는다. 동일 파일 수정이 필요하면 사용자에게 충돌 사실과 필요한 변경을 알리고 기다린다.
5. UI 완료 시 아래 형식으로 사용자에게 인계한다.

```text
UI_COMPLETE
- 변경한 파일:
- 제공한 props/callback 계약:
- Logic Session이 연결해야 할 hook/util:
- 남은 UI 제한 사항:
```

## 5. 기능 이식 핸드오프

- Logic Session은 hook/util 등 UI 외부 기능을 먼저 독립적으로 구현할 수 있다.
- 기능을 프로덕션 UI 파일에 연결하는 작업은 Claude Code의 `UI_COMPLETE`를 사용자가 확인한 뒤에 수행한다.
- UI가 완료되기 전에는 Claude Code가 만든 production UI 파일에 기능 연결을 선행하지 않는다.
- UI 완료 후 Logic Session이 최신 UI 파일을 다시 읽고 props/callback 경계에 기능을 연결한다.

## 6. 임시 기능 확인 UI

사용자가 Logic Session에 임시 기능 확인 UI를 명시적으로 요청할 수 있다. 이 경우 Claude Code의 production UI와 분리된 파일을 사용하며, 최소한의 시맨틱 마크업과 동작 확인에 필요한 레이아웃만 적용한다. 시각적 완성도, 디자인 확장 및 공용 UI 추상화는 목표로 삼지 않는다.

## 7. 검증 및 리뷰 제한

- 프로젝트의 `AGENTS.md`를 함께 따른다.
- 이미지 캡처, GIF, 화면 비교, 시각 QA 및 별도 리뷰 에이전트를 실행하지 않는다.
- 필요한 검증은 기존 테스트, `npm run build`, `npm run lint` 범위에서 수행한다.

## 8. Claude 산출물 위치

- 공통 `AGENTS.md`의 산출물 의미와 필수 항목을 따르되 Claude Code 세션은 `.claude/logs/sessions/{YYYY-MM-DD-task-slug}/`에 기록한다.
- `.codex/logs/**`는 Logic Session 소유로 계속 읽기 전용이다.
- 이 위치 치환은 산출물 누락을 허용하는 예외가 아니다.
- Claude Stop hook은 완성된 필수 산출물을 중앙 정책 저장소의 `logs/projects/{{PROJECT_ID}}/claude/sessions/`에 복사한다. 자동 수집이 실패하면 오류를 사용자에게 알리고 중앙 프로젝트에서 재수집한다.
