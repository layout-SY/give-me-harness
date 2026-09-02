# 탐색

## 요청

- 중앙 정책의 고유 작업자 명칭을 호스트 중립적으로 수정한다.
- Claude Planner/Evaluator가 향후 UI 외 구현의 기획·평가까지 담당할 수 있는지 검토하고 충돌 없는 역할 계약으로 반영한다.
- OpenCode 중앙화 운영 방식을 조사하고 세 호스트의 Git·빌드·개발 서버 실행 전 사용자 승인 게이트를 설계한다.

## 대상 관련 사실

- 중앙 저장소 HEAD는 조사 시작 시 `1fc8070 feat: 중앙 에이전트 정책 프로젝트 구축`이며 작업 트리는 깨끗했다.
- 공통 `AGENTS.template.md`와 Claude 템플릿·generator·planner에 `Hephaestus` 명칭이 남아 있었다.
- Claude planner와 evaluator는 이미 `Read`, `Grep`, `Glob`, `Bash`만 사용하여 애플리케이션 코드를 직접 수정할 수 없는 구조다.
- 기존 Claude Planner는 `Agent` 도구가 없는데도 Explore 서브 에이전트 2~3개를 실행하고 파이프라인 종료까지 상주하도록 요구했다. 호출 단위 서브 에이전트라는 실제 계약과 모순됐다.
- Codex 0.147.0 공식 매뉴얼에서 `PreToolUse`의 `permissionDecision: ask`는 파싱되지만 아직 지원되지 않고 도구 실행이 계속될 수 있으므로 승인 게이트로 사용할 수 없다.
- Claude Code 2.1.246 공식 훅 계약은 `PreToolUse`의 `ask`와 `UserPromptSubmit`을 지원한다.
- 설치된 OpenCode는 1.18.19이고 플러그인 패키지는 1.18.18이다. V1 프로젝트 권한의 `permission.bash`는 명령 패턴별 `ask`를 지원하며 한 번/항상/거절 선택을 제공한다.
- OpenCode V2 공식 문서는 `permission`/`bash` 대신 `permissions`/`shell`을 사용하므로 현재 설치본과 동일 파일에서 두 스키마를 혼용하면 안 된다.

## 불러온 스킬

- `policy-harness`: 승인, 관련 스킬, 역할 분리, Watcher/Evaluator 경계를 확인했다.
- `policy-documentation`: 한국어 Todo와 8종 세션 산출물 요구를 적용했다.
- `policy-abstraction-strategy`: 새 역할 추상화가 두 로직 호스트와 향후 Claude 분석 역할에서 실제로 재사용되는지 검토했다.
- `policy-review-checklist`: 승인·정확성·재사용·검증 근거 점검 기준으로 사용한다.
- `policy-portfolio`: 검증 후 현재 대화와 실행 근거만 포트폴리오 문서에 추합한다.
- `openai-docs`: 현재 Codex 훅 매뉴얼을 로컬 캐시로 확인했다.

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| `src/shared/ui/**` 전체 | 재사용하지 않음 | 이번 변경은 중앙 CLI·훅·Markdown 역할 계약이며 production UI를 생성하거나 수정하지 않는다. |

## 제약 조건 및 미확인 사항

- 소비 프로젝트에는 아직 중앙 V1이 동기화되지 않았으므로 중앙 변경 검증 후에도 실제 세션 동작은 별도 sync 승인 전까지 바뀌지 않는다.
- OpenCode V2로 업그레이드할 때 권한 설정 변환과 smoke test가 필요하다.
- OpenCode의 `always` 승인은 사용자의 명시적 선택이므로 정책이 강제로 `once`만 남길 수는 없다. 지시문에서 기본 선택을 `once`로 제한한다.

## 결론

- 발견한 기존 공통 guard와 호스트 adapter를 확장한다. 별도 승인 시스템을 중복 생성하지 않는다.
- Claude의 분석 역할과 구현 역할을 분리하면 Planner/Evaluator의 전역 분석 확장은 현재 병렬 파일 소유권과 모순되지 않는다.
- 기본 Claude 세션이 오케스트레이션하고 Planner/Evaluator가 중첩 위임 없이 호출 단위 결과를 반환하도록 수정하면 서브 에이전트 수명주기 모순도 제거된다.
- 세션별 동시성은 Codex 승인 상태를 `저장소 + 호스트 + session_id`로 격리하고 Claude/OpenCode 네이티브 세션 승인을 사용하면 지원할 수 있다.
