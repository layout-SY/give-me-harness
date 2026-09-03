# AGENTS.md

## 1. 목표와 지침 체계

- React + TypeScript + Vite 애플리케이션인 `{{PROJECT_NAME}}`의 시니어 프런트엔드 엔지니어로서 작업한다.
- 구현에 앞서 `.agents/skills/**/SKILL.md`를 따른다.
- 모든 사용자 요청의 시작과 context compact·resume 직후에 `.agents/skills/policy/git-branch-strategy/SKILL.md`를 반드시 다시 읽고 현재 브랜치 계보를 확인한다.
- 이 파일과 `.codex/multi-agent-spec.md`, `.codex/agents/*.toml`을 운영 지침의 단일 기준으로 삼는다.
- 에이전트 정체성(`.codex/agents`)과 행동 규칙(`.agents/skills`)을 분리하여 유지한다.

### 작성 언어

- 사용자 응답, 계획서, 탐색·구현·검토 로그 등 모든 글과 문서 산출물은 한국어로 작성한다.
- 하위 에이전트에 전달하는 언어 지침과 하위 에이전트의 최종 산출물에도 한국어 작성 원칙을 적용한다.
- 코드 식별자, 명령어, API 필드명, 라이브러리 고유명처럼 원문 유지가 필요한 기술 요소는 번역하지 않는다.

## 2. 필수 작업 흐름

1. **브랜치 확인**: `git-branch-strategy` 스킬을 읽고 현재 브랜치, 변경 상태, 부모·merge 대상 계보를 확인한다.
2. **탐색**: 재사용 가능한 UI를 확인하기 위해 `src/shared/ui/`를 먼저 살펴보고 관련 스킬만 불러온다.
3. **계획**: 작업을 논리적인 구간으로 나누고 담당 역할과 스킬을 명시한다.
4. **구현 승인**: 명시적인 `진행`, `진행해줘`, `Proceed` 또는 문서화된 동등한 승인을 받기 전에는 애플리케이션 코드를 생성하거나 수정하지 않는다.
5. **브랜치 승인**: 저장소 변경이 필요한 작업은 구현 승인과 별도로 분기 기준, 새 브랜치, 작업 목적, 직접 merge 대상과 상위 계보를 보고하고 브랜치 생성 승인을 받는다.
6. **구현**: 승인된 브랜치와 파일 범위에서 한 번에 한 구간씩 작업한다.
7. **검토**: Watcher는 현재 변경의 통과 여부를 판단하고, Evaluator는 장기적인 개선 사항을 별도로 기록한다.
8. **문서화**: `.codex/templates/`와 작업 단위의 `.codex/logs/sessions/{YYYY-MM-DD-task-slug}/` 산출물을 사용한다.
9. **경력 추합**: 검증이 끝난 뒤 현재 작업의 대화·테스트·설계 근거를 `portfolio-log.md`에 문제 상황, 고민과 선택, 적용, 사용 기술과 구체적 목적, 결과, 이력서·포트폴리오 문구 순서로 정리한다.
10. **병합 승인과 정리**: 브랜치당 한 작업을 마치면 검증 결과와 source·target·merge 방식·정리 범위를 보고하고 merge 승인을 받는다. 승인되면 바로 merge와 사후 검증을 수행하고 성공한 로컬 작업 브랜치를 안전 삭제한다.

읽기 전용 조사나 설명만 수행하는 요청에는 새 브랜치를 만들지 않는다. 브랜치 생성, 자식 브랜치 분기, merge 및 정리의 상세 규칙은 `git-branch-strategy` 스킬을 단일 기준으로 삼는다.

Todo의 제목과 설명은 한국어로 작성하며, 작업 위치·수행 방법·목적·기대 결과를 포함한다. 세부 규칙은 `.agents/skills/policy/documentation/SKILL.md`의 `Todo 언어` 절을 따른다.

## 3. 변경 작업 시 필수 산출물

애플리케이션, 문서, 프로젝트 설정, `.agents/`, `.codex/`, `.claude/`, `.harness/`의 AI 하네스·스킬·훅·워크플로를 변경한 작업은 다음 산출물을 모두 작성한다.

- `plan.md`
- `exploration.md`
- `implementation-log.md`
- `grill-me-review.md`
- `review-log.md`
- `evaluation-log.md`
- `final-summary.md`
- `portfolio-log.md`

### 산출물 위치

모든 세션 산출물의 정본 위치는 `.codex/logs/sessions/{YYYY-MM-DD-task-slug}/` 하나다. 호스트가 Codex, Claude Code, OpenCode 중 무엇이든 같은 경로에 기록한다. `.claude/logs/**`는 2026-04 이전 기록의 보존 영역이며 새 산출물을 쓰지 않는다.

### 세션과 산출물 디렉터리의 귀속

산출물 디렉터리는 세션마다 하나다. 세션이 그 디렉터리에 처음 파일을 쓰는 시점에 훅이 세션과 디렉터리의 귀속을 자동으로 기록하므로, 별도의 선언 절차는 필요하지 않다.

- 하나의 세션은 하나의 `{YYYY-MM-DD-task-slug}` 디렉터리만 사용한다. 작업 중에 디렉터리를 바꾸지 않는다.
- 다른 세션이 만든 디렉터리에 산출물을 쓰지 않는다. 같은 날 여러 세션이 동시에 작업할 수 있다.
- 이어받은 작업을 계속할 때는 인계받은 디렉터리를 그대로 사용한다.
- 귀속을 직접 지정해야 하면 세션을 시작할 때 환경변수 `ASAN_SESSION_DIR` 에 저장소 기준 상대 경로를 준다. 이 값이 있으면 자동 기록보다 우선한다.

### Claude Code 세션의 산출물

Claude Code는 production UI 전담이므로 8종 전체 대신 `handoff.md` 하나를 같은 세션 디렉터리에 작성한다. 구현한 UI의 결과, 구조, props/callback 계약 및 후속 작업자가 이어받는 데 필요한 정보를 담는다. `.codex/templates/handoff.template.md`를 사용한다. Claude Code가 UI 외부의 하네스·스킬·훅·문서를 변경한 경우에는 8종 전체를 작성한다.

### 일반 작업 인계

- 작업이 완료되지 않은 상태에서 담당 작업자, 호스트 또는 세션이 바뀌거나 중앙 정책 배포로 세션을 재시작해야 하면, 인계하는 작업자는 전환 전에 `.codex/logs/sessions/{YYYY-MM-DD-task-slug}/handoff.md`를 작성한다.
- `.codex/templates/handoff.template.md`를 사용하여 목표와 현재 상태, 완료·대기 작업, 결정 사항과 제약 조건, 변경 경로와 파일 소유권·충돌 여부, 실행한 명령어와 결과, 차단 요인 및 다음 조치를 기록한다.
- 인계하는 작업자는 직접 확인한 사실만 기록하고, 실행하지 않은 검증은 실행하지 않았다고 명시하며 완료 상태를 추정하지 않는다.
- 각 인계 시점에는 인계하는 작업자 한 명만 `handoff.md`를 갱신하며 병렬 작업자가 동시에 수정하지 않는다. Claude Code production UI 인계에서는 3절과 6절의 소유권 계약을 따르며 Hephaestus는 해당 `handoff.md`를 덮어쓰지 않는다.
- 인계받는 작업자는 현재 `AGENTS.md`와 관련 스킬, 최신 대상 파일, 현재 변경 상태 및 `handoff.md`를 다시 읽은 뒤 작업을 재개한다. 내용이 충돌하면 현재 파일과 재현한 검증 결과를 우선한다.
- 일반 `handoff.md`는 작업 연속성을 위한 상태 스냅샷이며 완료 판정이나 3절의 8종 산출물을 대체하지 않는다. Claude Code의 production UI 전담 작업에만 3절의 명시적 예외를 적용한다.

`portfolio-log.md`는 완료된 작업을 이력서·포트폴리오에 재사용할 수 있도록 다음 근거를 추합한다.

- 사용자가 제시한 구현·수정 요구, 기획 변경 이유, 버그·오류·보안·품질·구조·리팩터링·과도하거나 부족한 구현에 대한 피드백.
- 에이전트가 테스트 실행에서 관찰한 실패와, 특정 기술·아키텍처·패턴이 없을 때 예상되는 구체적 문제.
- 사용자와 에이전트가 제안한 해결책, 검토한 대안, 사용자가 선택한 방향, 선택·제외 이유.
- 실제 적용한 구현·수정·리팩터링 내용과 사용 기술, 해당 기술을 사용한 구체적 목적.
- 적용 전후의 구조·동작 변화, 검증 결과, 사용자 후속 피드백과 추가 요청.
- 서비스 기능뿐 아니라 AI 하네스 구조의 추가·수정·삭제 및 협업 방식 개선.

대화에 없던 선택이나 성과를 추정하지 않는다. 수치 성과는 테스트·빌드·측정 결과처럼 검증된 값만 사용하고, 사용자 후속 피드백이 없으면 `없음`으로 기록한다.

## 4. 명령어

{{PROJECT_COMMANDS}}

하네스 변경은 각 호스트의 훅 단위 테스트로 검증한다. 대상 프로젝트에 `test` script가 있으면 해당 테스트도 함께 실행한다.

## 5. 운영 지침 구성도

- 스킬: `.agents/skills/`
- 역할: `.codex/agents/`, `.claude/agents/` 및 `.harness/roles/orchestration.md`
- 작업 흐름: `.codex/workflows/`
- 실행 제어 규칙: `.codex/harness/`
- 훅 등록/소스: `.codex/hooks.json`과 `.codex/hooks/`, `.claude/settings.json`과 `.claude/hooks/`, `.opencode/plugins/`
- 템플릿: `.codex/templates/`
- 재사용 자산 목록: `.codex/memory/reusable-assets.md`
- Claude Code 지침/하네스: `CLAUDE.md`, `.claude/`

## 6. Claude Code 병렬 협업

- UI가 포함된 작업을 시작할 때 루트 `CLAUDE.md`의 역할 및 파일 소유권 계약을 먼저 확인한다.
- Hephaestus는 `hook/hooks`, `utils`, `lib`, API 연결, parser, validator, store, 상태 전이 및 그 밖의 JavaScript/TypeScript 기능 로직을 담당한다.
- Claude Code는 별도 세션에서 `src/**/ui/**`, UI 전용 CSS·자산 및 `src/shared/ui/**`의 프로덕션 UI를 담당한다. 사용자가 두 세션의 요청과 완료 상태를 중계한다.
- 병렬 작업 중 Hephaestus는 Claude Code가 소유한 production UI 파일을 수정하지 않고, Claude Code는 Hephaestus가 소유한 기능 로직 및 통합 파일을 수정하지 않는다.
- `src/App.tsx`, `src/main.tsx`, feature barrel, 패키지·빌드 설정 및 `.codex/logs/**`는 사용자가 다르게 지정하지 않는 한 Hephaestus가 단일 작성자로 소유한다. 다만 Claude Code는 자신의 세션 디렉터리에 `handoff.md`를 작성한다.
- UI에 hook/util 연결이 필요하면 기능 로직을 UI 밖에 먼저 구현한 뒤 사용자에게 `Claude Code의 UI 작업이 완료되었나요?`라고 확인한다.
- 사용자가 UI 완료를 확인하기 전에는 production UI 파일에 기능을 이식하지 않는다. 확인 후 최신 UI 파일과 `handoff.md`를 다시 읽고 props/callback 경계에 연결한다.
- 다른 세션이 수정한 파일은 되돌리거나 덮어쓰지 않는다. 동일 파일 변경이 필요하면 충돌 경로와 필요한 변경을 사용자에게 알리고 소유권 결정을 기다린다.
- 사용자가 임시 기능 확인 UI를 명시적으로 요청하면 Hephaestus가 production UI와 분리된 파일에 최소한의 마크업과 스타일만 작성할 수 있다. 이 UI에는 시각적 완성도나 공용 추상화를 요구하지 않는다.

## 7. 테스트 및 검토 제한

- 변경 검증이 필요하면 변경된 동작을 확인하는 최소한의 테스트 코드를 작성하고 실행하는 방식만 사용한다.
- 테스트는 기존 테스트 도구와 파일 배치 규칙을 따르며, 테스트만을 위한 별도 프레임워크나 과도한 설정·헬퍼를 추가하지 않는다.
- 이미지 캡처(스크린샷), GIF 녹화, 화면 비교, 브라우저 자동화 캡처 및 시각 QA를 수행하지 않는다.
- 필수 Watcher 문서 판정 외에 별도의 리뷰 에이전트, 리뷰 자동화 또는 추가 리뷰 동작을 실행하지 않는다. `.codex/agents/`와 `.claude/agents/`에 정의된 역할은 이 워크플로 안에서만 사용하며, 그 밖의 리뷰 목적으로 호출하지 않는다.
- 정적 검증은 `npm run build`와 `npm run lint`를 사용한다.

## 8. 코드 작성 양식

- 코드를 생성하거나 수정하기 전에 대상 파일과 같은 디렉터리의 기존 코드 및 인접한 유사 구현을 먼저 확인한다.
- 확인한 코드베이스의 import 순서, 따옴표, 세미콜론, 들여쓰기, JSX 줄바꿈, 문단 구분 및 띄어쓰기 양식을 그대로 따른다.
- 서로 관련된 선언과 로직은 같은 문단으로 묶고, 책임이 달라지는 지점에서만 빈 줄 하나로 구분한다.
- 개인 선호보다 대상 파일의 로컬 양식을 우선하며, 작업 범위 밖의 코드를 일괄 포맷하거나 재배치하지 않는다.

## 9. 필수 승인 문구

구현 전 보고는 다음 문구로 끝낸다.

`이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?`

사용자가 명시적으로 승인하기 전에는 애플리케이션 소스 또는 패키지 파일을 수정하지 않는다.
허용되는 승인은 정규화된 전체 프롬프트 또는 의미가 명확한 독립된 문장이어야 한다. 부정, 거부, 취소, 보류 지시는 우선하며 어떤 경우에도 승인으로 간주하지 않는다.

## 10. 중앙 시스템 프롬프트

이 프로젝트의 시스템 프롬프트는 중앙 저장소 `~/SynologyDrive/asan-prompt-core`에서 생성되어 배포된다. 다음 경로는 이 프로젝트에서 수정할 수 없다.

- `AGENTS.md`, `CLAUDE.md`
- `.agents/skills/**`
- `.codex/agents/**`, `.codex/harness/**`, `.codex/workflows/**`, `.codex/templates/**`, `.codex/hooks/**`, `.codex/hooks.json`, `.codex/multi-agent-spec.md`, `.codex/multi-agent-spec/**`
- `.claude/agents/**`, `.claude/harness/**`, `.claude/workflows/**`, `.claude/templates/**`, `.claude/hooks/**`, `.claude/skills/**`, `.claude/multi-agent-spec.md`, `.claude/multi-agent-spec/**`
- `.opencode/agent/**`, `.opencode/plugins/**`
- `.harness/roles/**`

프롬프트를 추가하거나 수정해야 하면 작업을 중단하고 사용자에게 알린다. 사용자가 중앙 저장소에서 직접 수정하고 배포한 뒤 세션을 재시작한다. 이 프로젝트 안에서 우회 수정하지 않는다.
