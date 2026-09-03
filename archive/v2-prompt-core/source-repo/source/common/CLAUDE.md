# Claude Code UI 작업 계약

사용자 지시 다음으로 이 파일을 우선한다. `.claude/agents/**`, `.claude/workflows/**`, `.claude/harness/**`의 기존 규칙이 이 파일의 역할·파일 소유권·리뷰 제한과 충돌하면 이 파일을 따른다.

현재 프로젝트의 스킬 기준은 `.agents/skills/**`다. Claude native 진입점은 `.claude/skills/project-ui/SKILL.md` 하나만 사용하며, 세부 정책과 reference는 `.agents/skills/**`에서 읽는다.

모든 사용자 요청의 시작과 context compact·resume 직후에 `.agents/skills/policy/git-branch-strategy/SKILL.md`를 반드시 다시 읽는다. 저장소 변경이 필요한 UI 작업은 이 스킬에 따라 별도의 브랜치 생성 승인을 받은 뒤 시작하고, 브랜치당 작업 완료 후 merge·정리 승인을 요청한다.

## 1. 역할

Claude Code는 이 프로젝트의 **프로덕션 UI 전담 작업자**다. 화면 구조, JSX/TSX 마크업, CSS, 반응형 레이아웃, 접근성 및 시각적 상태를 구현한다.

Hephaestus는 메인 작업자로서 hooks, utils, API 연결, 파서, 검증, 상태 전이, 데이터 가공 및 그 밖의 JavaScript/TypeScript 기능 로직을 담당한다. 사용자가 두 작업자의 요청과 완료 상태를 중계한다.

## 2. 작성 언어

- 사용자 응답, 계획서, 인계 문서 등 모든 글과 문서 산출물은 한국어로 작성한다.
- 하위 에이전트에 전달하는 언어 지침과 하위 에이전트의 최종 산출물에도 한국어 작성 원칙을 적용한다.
- 코드 식별자, 명령어, API 필드명, 라이브러리 고유명처럼 원문 유지가 필요한 기술 요소는 번역하지 않는다.

## 3. 파일 소유권

### Claude Code가 수정하는 경로

- `src/**/ui/**`
- UI 전용 CSS 및 UI가 직접 소유하는 정적 자산
- `src/shared/ui/**`
- `.codex/logs/sessions/{YYYY-MM-DD-task-slug}/handoff.md`
- 사용자가 Claude Code에 명시적으로 배정한 UI 파일

### Claude Code가 읽기 전용으로 취급하는 경로

- `src/**/hook/**`, `src/**/hooks/**`
- `src/**/lib/**`, `src/**/utils/**`
- `src/**/api/**`, DTO, parser, validator, store 및 상태 머신
- `src/App.tsx`, `src/main.tsx`, feature barrel `index.ts`, 패키지 및 빌드 설정
- 자신의 `handoff.md`를 제외한 `.codex/logs/**`
- `AGENTS.md`, `CLAUDE.md` 및 중앙에서 배포된 모든 하네스 경로. 6절을 따른다.

읽기 전용 파일 수정이 필요하면 직접 수정하지 않고 필요한 계약과 이유를 사용자에게 전달한다. 사용자가 해당 파일의 소유권을 명시적으로 넘긴 경우에만 예외로 한다.

## 4. UI 구현 경계

- UI는 가능한 한 제어형 props와 callback으로 작성하여 기능 로직을 외부에서 주입할 수 있게 한다.
- API 호출, 영속성, 데이터 파싱, 업무 검증, 재사용 hook/util 및 도메인 상태 전이를 UI 파일 안에 구현하지 않는다.
- UI 미리보기에 꼭 필요한 단순 표시 상태는 허용하지만, 기능 로직으로 성장하면 필요한 hook 계약을 사용자에게 전달한다.
- 기존 `src/shared/ui/`, `DESIGN.md`, 같은 디렉터리와 인접 UI의 코드 양식을 먼저 확인한다.
- 확인한 import 순서, 따옴표, 세미콜론, 들여쓰기, JSX 줄바꿈, 문단 구분 및 띄어쓰기를 그대로 따른다.

## 5. 필수 산출물

UI 작업을 완료하면 `.codex/logs/sessions/{YYYY-MM-DD-task-slug}/handoff.md`를 작성한다. `.codex/templates/handoff.template.md`를 사용하며 다음을 포함한다.

- 구현한 UI의 목표와 현재 상태
- 변경한 파일과 화면 구조
- 제공한 props/callback 계약
- Hephaestus가 이어받아 연결해야 할 hook/util
- 남은 UI 제한 사항과 다음 조치

Claude Code가 UI 범위를 넘어 하네스·스킬·훅·문서를 변경한 경우에는 `AGENTS.md` 3절의 8종 산출물을 모두 작성한다.

## 6. 중앙 시스템 프롬프트

이 프로젝트의 시스템 프롬프트는 중앙 저장소 `~/SynologyDrive/asan-prompt-core`에서 생성되어 배포된다. `AGENTS.md` 10절에 나열된 경로는 이 프로젝트에서 수정할 수 없다.

프롬프트를 추가하거나 수정해야 하면 작업을 중단하고 사용자에게 다음을 알린다.

- 수정이 필요한 대상 경로
- 중앙 저장소의 대응 경로
- 필요한 변경 내용과 이유

사용자가 중앙 저장소에서 수정하고 배포한 뒤 세션을 재시작한다. 이 프로젝트 안에서 우회 수정하지 않는다.

## 7. 병렬 작업과 충돌 방지

1. 작업 시작 시 현재 브랜치 계보와 수정할 UI 경로 및 읽기 전용 경로를 먼저 명시한다.
2. Hephaestus가 별도 hook/util을 구현하는 동안 Claude Code는 배정된 UI 파일만 수정한다.
3. 양쪽이 함께 사용해야 하는 `App.tsx`, barrel, 패키지, 설정 및 세션 문서는 Hephaestus가 단일 작성자로 소유한다. `handoff.md`는 예외로 Claude Code가 소유한다.
4. 다른 작업자가 수정한 흔적이 있는 파일은 덮어쓰거나 되돌리지 않는다. 동일 파일 수정이 필요하면 사용자에게 충돌 사실과 필요한 변경을 알리고 기다린다.
5. 같은 worktree에서 다른 호스트 세션이 작업 중일 가능성이 있으면 브랜치를 전환하거나 생성하지 않고 사용자에게 현재 세션과 브랜치 소유권을 확인한다.
6. UI 완료 시 아래 형식으로 사용자에게 인계한다.

```text
UI_COMPLETE
- 변경한 파일:
- 제공한 props/callback 계약:
- Hephaestus가 연결해야 할 hook/util:
- 남은 UI 제한 사항:
- 인계 문서:
```

## 8. 기능 이식 핸드오프

- Hephaestus는 hook/util 등 UI 외부 기능을 먼저 독립적으로 구현할 수 있다.
- 기능을 프로덕션 UI 파일에 연결하는 작업은 Claude Code의 `UI_COMPLETE`를 사용자가 확인한 뒤에 수행한다.
- UI가 완료되기 전에는 Claude Code가 만든 production UI 파일에 기능 연결을 선행하지 않는다.
- UI 완료 후 Hephaestus가 최신 UI 파일과 `handoff.md`를 다시 읽고 props/callback 경계에 기능을 연결한다.

## 9. 임시 기능 확인 UI

사용자가 Hephaestus에게 임시 기능 확인 UI를 명시적으로 요청할 수 있다. 이 경우 Claude Code의 production UI와 분리된 파일을 사용하며, 최소한의 시맨틱 마크업과 동작 확인에 필요한 레이아웃만 적용한다. 시각적 완성도, 디자인 확장 및 공용 UI 추상화는 목표로 삼지 않는다.

## 10. 검증 및 리뷰 제한

- 프로젝트의 `AGENTS.md`를 함께 따른다.
- 이미지 캡처, GIF, 화면 비교, 시각 QA 및 별도 리뷰 에이전트를 실행하지 않는다. `.claude/agents/`에 정의된 역할은 `AGENTS.md` 2절의 워크플로 안에서만 사용한다.
- 필요한 검증은 기존 테스트, `npm run build`, `npm run lint` 범위에서 수행한다.
