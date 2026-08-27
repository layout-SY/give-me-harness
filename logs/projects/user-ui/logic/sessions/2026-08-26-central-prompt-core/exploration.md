# 탐색

## 요청

user-ui와 admin-ui가 각자 보유한 시스템 프롬프트(AGENTS.md, CLAUDE.md, 스킬, 훅, 에이전트)의 드리프트를 없애기 위해, 별도 위치에 중앙 프롬프트 프로젝트를 만들고 두 프로젝트로 배포한다. user-ui의 현재 프롬프트를 기준 원본으로 삼고, 기준으로 삼기 전에 내부 불일치를 교정한다.

## 대상 관련 사실

### 프롬프트 자산 규모 (user-ui)

| 대상 | 파일 | 줄 수 |
| --- | --- | --- |
| `AGENTS.md` | 1 | 97 |
| `CLAUDE.md` | 1 | 72 |
| `.agents/skills/**` | 28 | 396 |
| `.claude/agents/**` | 6 | 424 |
| `.claude/harness`, `.claude/workflows` | 10 | 229 |
| `.codex/agents`, `.codex/harness`, `.codex/workflows` | 18 | 79 |
| `.codex/templates`, `.claude/templates` | 30 | 684 |
| `multi-agent-spec` (양쪽) | 14 | 44 |
| `.codex/hooks/**` (Python) | 8 | 1364 |

Markdown/TOML 합계는 약 1,600줄이다. 별도 런타임 없이 파일 복사와 해시 비교로 관리 가능한 규모다.

### 기존 중앙화 시도

`~/SynologyDrive/asan-harness`에 Python 런타임(233 트래킹 파일, 230 테스트, v0.1.3)이 존재한다. 다음 이유로 재사용하지 않는다.

- `governance_sources.py`가 프롬프트 본문이 아니라 소스 ID와 앵커(`"AGENTS.md#6"`)만 보유한다. 중앙에 실제 텍스트가 없다.
- `governance_render.py:40`의 `_root()`가 생성하는 `AGENTS.md`는 10줄 메타데이터 스텁이며, `render_command`는 이를 `os.replace`로 덮어쓴다. 현 상태로 실행하면 지침이 소실된다.
- `.agents/skills/**/SKILL.md` 본문을 생성하는 코드가 없다. 드리프트 최대 표면이 커버 밖이다.
- `launch` 계열이 요구하는 actual-host mutation certification을 설치된 세 호스트 중 어느 것도 통과하지 못해 활성화가 봉쇄되어 있다.

설계 아이디어(정렬 JSON 직렬화, drift 검사, 프로파일 필드)만 차용하고 코드는 새로 작성한다.

### 호스트별 프롬프트 적재 경로

`.agents/skills/`는 codex, claude, opencode가 모두 동일 경로를 읽는다. 전체 자산 중 396줄이 무변환 복사 대상이다. 실제 변환이 필요한 대상은 역할 정의 형식(`.toml` 대 frontmatter `.md`)과 훅 등록 방식뿐이다.

## 불러온 스킬

- `.agents/skills/SKILL.md`
- `.agents/skills/policy/SKILL.md`
- `.agents/skills/policy/harness/SKILL.md`
- `.agents/skills/policy/documentation/SKILL.md`
- `.agents/skills/policy/codex-native-quality/SKILL.md`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| 해당 없음 | 미사용 | 애플리케이션 UI 변경이 없는 하네스 전용 작업이다 |

## 제약 조건 및 미확인 사항

- 사용자가 이번 작업에 한해 `AGENTS.md`, `CLAUDE.md`, `.agents/**`, `.codex/**`, `.claude/**`의 소유권을 Claude Code에 이전했다.
- 프로젝트 고유 오버레이(user의 Agora RTC, admin의 TanStack Query)는 이번 범위에서 제외하고 이후 기능으로 추가한다.
- `.agents/skills/**`의 얇은 본문(8줄 스킬 8개) 보강은 외부 프롬프트 참고가 필요하여 이번 범위에서 제외한다.

## 결론

user-ui 프롬프트를 교정한 뒤 중앙으로 이관하고, 파일 복사와 해시 비교만 수행하는 200줄 규모의 동기화 도구와 편집 차단 훅을 구현한다.
