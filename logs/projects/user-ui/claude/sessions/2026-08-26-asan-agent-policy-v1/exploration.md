# 탐색

## 요청

`폐기된 외부 정책 저장소`가 아닌 새 중앙 정책 프로젝트를 만들고 user-ui를 기준으로 Codex·Claude Code·OpenCode 세션 정책을 동기화한다.

## 대상 관련 사실

- user-ui Git HEAD에는 `AGENTS.md`, `CLAUDE.md`, `.agents/`, `.codex/`, `.claude/`, `.harness/`가 추적되어 있다.
- user-ui 현재 작업 트리의 다수 AI 파일에는 `폐기된 외부 정책 저장소` 배포 주석이 존재한다.
- admin-ui Git HEAD에는 해당 AI 정책 경로가 추적되어 있지 않다.
- Codex 공식 문서는 `AGENTS.md`를 세션 시작 시 한 번 구성하고, 신뢰된 프로젝트의 `.codex/hooks.json`에서 `PreToolUse` 차단을 지원한다고 설명한다.

## 불러온 스킬

- `skill-index`
- `policy-index`
- `policy-harness`
- `policy-documentation`
- `policy-abstraction-strategy`
- `policy-review-checklist`
- `policy-portfolio`
- `openai-docs`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| user-ui `src/shared/ui/**` 73개 파일 | 구현 재사용 없음 | 이번 작업은 UI를 만들지 않는다. 탐색 우선 정책만 중앙화한다. |

## 제약 조건 및 미확인 사항

- 실제 대상 배포 전에는 두 프로젝트의 생성 예정 diff를 별도 승인받아야 한다.
- OpenCode 어댑터는 설치된 런타임과 공식 플러그인 계약으로 검증한다.
- 구현 중 별도 작업이 user-ui의 추적된 AI 정책 129개를 Git index에서 제거하고 `.gitignore`에 중앙 산출물 ignore 규칙을 추가한 상태를 관찰했다. 이 변경은 되돌리지 않았다.
- 최초 legacy 감사 뒤 두 프로젝트의 `.claude/hooks/harness_core.py`, `.codex/hooks/harness_core.py`, `.opencode/plugins/harness_core.py`가 같은 새 hash로 바뀌었다. 안전 퇴역 기준 hash와 달라 자동 삭제할 수 없다.

## 결론

Git HEAD 기반 공통 정책과 호스트별 얇은 어댑터를 분리하고, target manifest가 기록한 파일만 이후 교체·퇴역시키는 구조가 적합하다.

실제 첫 배포는 동시 변경된 legacy 파일을 폐기해도 된다는 사용자 확인과 `--retire-legacy` 승인이 추가로 필요하다.
