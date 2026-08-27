# 이력서·포트폴리오 기록

## 사례 1 — 멀티 호스트 중앙 정책의 역할·명령 승인 계약 확장

- 작업 유형: AI 하네스
- 관련 도메인/서비스: `asan-metaverse-user-ui`, `asan-metaverse-admin-ui`, Codex, Claude Code, OpenCode
- 문제 출처: 사용자 요구 | 기획 변경 | 구현 위험 | 검토 결과

### 문제 상황

- 사용자가 제시한 요구·문제·변경 이유: 특정 호스트 작업자 이름을 중앙 역할로 일반화하고, Claude가 향후 UI 외 구현까지 기획·평가하며, 네 세션에서 Git·빌드·개발 서버 실행을 사용자가 통제할 수 있어야 했다.
- 테스트·런타임에서 관찰한 오류: 첫 `py_compile`은 중앙 저장소의 `__pycache__` 쓰기가 sandbox에서 거부됐고, OpenCode debug는 사용자 홈 로그 쓰기가 필요해 제한 환경에서 실패했다. `-B` AST/단위 테스트와 승인된 실제 OpenCode smoke로 검증 경로를 조정했다.
- 필요한 기술·구조·패턴이 없을 때 발생할 문제: 호스트명 고정으로 OpenCode 역할이 불명확해지고, Planner 분석 권한이 구현 권한으로 오인되며, 동시 세션의 Git/build/dev 실행이 사용자 판단 없이 충돌할 수 있다.

### 고민과 선택

- 사용자 제안: Codex/OpenCode 로직 세션과 Claude UI 세션을 두 프로젝트에서 병렬 운용하고, 향후 Claude Planner/Evaluator가 전체 구현 기획·평가를 맡으며 보호 명령은 사용자가 직접 판단한다.
- 에이전트 제안: `Logic Session` 역할, 분석/쓰기 소유권 분리, 호스트별 native 기능 우선, Codex만 exact one-shot 승인 상태를 사용한다.
- 검토한 대안: 모든 호스트에 동일한 로그 기반 승인 상태를 복제하는 방식, 모든 shell 명령을 차단하는 방식, Planner에 중첩 서브 에이전트 실행 권한을 주는 방식.
- 최종 선택: Claude/OpenCode는 native ask, Codex는 동일 명령 해시 1회 승인, Claude 기본 세션은 오케스트레이션하고 Planner/Evaluator는 호출 단위 읽기 전용 역할을 맡는다.
- 선택 이유와 제외한 방식의 이유: native 권한 UI가 호스트 세션과 직접 결합되어 가장 단순하며, Codex `ask`는 현재 미지원이다. 모든 shell 차단은 정상 탐색·lint/test를 과도하게 방해하고, 중첩 Planner는 현재 도구·수명주기 계약과 모순된다.

### 적용

- 변경 경로: 중앙 `policy/common`, `policy/guards`, `adapters/claude`, `adapters/opencode`, `lib/agent_policy`, `tests`, `README.md`.
- 구현·수정·리팩터링 내용: Hephaestus 제거, Logic Session 도입, Claude Planner/Evaluator 전역 읽기·비구현 계약, 보호 명령 분류, Codex 승인 상태, OpenCode 권한 config renderer와 smoke 추가.
- 핵심 동작: 보호 명령을 정확히 표시하고 사용자 승인 전 차단하며 Codex 승인은 동일 세션·동일 명령 한 번에만 소비한다.

### 사용 기술과 구체적 목적

| 기술·구조·패턴 | 해결하려는 구체적 문제 | 적용 위치와 방식 |
| --- | --- | --- |
| 역할 기반 소유권 | 분석 범위 확장이 파일 충돌로 이어지는 문제 | Logic Session, Claude 기본 세션, Planner/Evaluator 계약 분리 |
| Codex lifecycle hooks | native ask 부재에서 사용자 승인 왕복 필요 | UserPromptSubmit + PreToolUse, session ID와 SHA-256 one-shot 상태 |
| Claude PreToolUse ask | 명령 실행 직전 사용자 판단 | 중앙 guard가 공식 ask JSON 반환 |
| OpenCode V1 permissions | OpenCode TUI의 세션 네이티브 승인 | `opencode.json`의 명령 패턴별 `permission.bash: ask` |
| 결정적 renderer·manifest | 두 프로젝트 정책 drift 방지 | config와 guard를 128개 managed output에 포함 |
| unittest·실설치 smoke | 호스트 문서와 런타임 차이 검증 | 26 tests와 OpenCode 1.18.19 effective config 확인 |

### 결과

- 적용 전: 특정 작업자 명칭, UI 전용 Planner 계약, 불가능한 중첩 Explore/상주 요구, 보호 명령의 세 호스트 공통 통제 부재.
- 적용 후: 호스트 중립 로직 역할, Claude 전역 기획·평가와 UI 쓰기 경계 분리, 세 호스트별 실행 전 승인, 세션 격리 테스트가 중앙 원본 커밋 `3a291fc`에 반영됐다.
- 검증 결과: 단위 테스트 26개 PASS, 두 프로젝트 각 128 managed files audit PASS, OpenCode plugin·권한 effective config smoke PASS.
- 사용자 후속 피드백: 없음.
- 추가 요청 및 남은 제한: 소비 프로젝트 sync와 legacy 해시 불일치 처리는 별도 승인 대기, OpenCode V2 미지원.

```mermaid
flowchart LR
  Before[호스트 고정 역할과 무통제 보호 명령] --> Change[역할 분리와 호스트별 승인 게이트]
  Change --> After[네 세션 병렬 운용 가능한 중앙 계약]
```

### 이력서·포트폴리오 문구

- 이력서 bullet: Codex·Claude Code·OpenCode 중앙 정책을 역할 기반으로 재설계하고, 세션 격리형 one-shot 승인과 native permission adapter를 구현해 26개 회귀 테스트 및 실설치 smoke로 검증.
- 포트폴리오 서술: 두 프런트엔드 프로젝트의 AI 세션을 병렬 운용할 때 호스트 고정 명칭과 실행 권한 차이로 정책이 흔들리는 문제를 분석했다. 분석 역할과 파일 쓰기 소유권을 분리하고 Logic Session·Claude Planner/Evaluator 계약을 정의했으며, 각 호스트의 실제 훅 지원 수준에 맞춘 Git/build/dev 승인 게이트를 구현했다. 결정적 렌더링과 세션 격리 테스트, OpenCode effective config smoke로 중앙 원본의 일관성을 검증했다.
