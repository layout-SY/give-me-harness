# 이력서·포트폴리오 기록

## 사례 1 — 멀티 호스트 에이전트 훅 교착과 무한 재개 제거

- 작업 유형: AI 하네스
- 관련 도메인/서비스: 중앙 에이전트 정책, Codex·Claude·OpenCode lifecycle hooks
- 문제 출처: 사용자 피드백 | 테스트·런타임 실패

### 문제 상황

- 사용자가 제시한 요구·문제·변경 이유: 읽기 전용 handoff 조사에서도 구현 승인과 Git 명령 승인을 요구했고, 종료 시 필수 산출물 8종 요구가 반복됐다.
- 테스트·런타임에서 관찰한 오류: invalid SessionStart JSON, branch 승인 식별자 불일치, 산출물 Write 차단, Stop hook의 반복 continuation.
- 필요한 기술·구조·패턴이 없을 때 발생할 문제: 종료할 수 없는 세션, 정책 우회 유도, 호스트별 판정 drift.

### 고민과 선택

- 사용자 제안: parent session의 자손 branch 권한을 인정하고 실제 오류 흐름을 수정한다.
- 에이전트 제안: 일반 종료와 완료 검증을 분리하고 Git 조회 분류를 공통화한다.
- 검토한 대안: Stop 재진입 횟수 제한, Codex 전용 예외, 모든 Git 명령 승인 유지.
- 최종 선택: Stop은 로그 수집만, 완료 검증은 명시적 lifecycle만, 조회형 Git은 공통 parser로 허용.
- 선택 이유와 제외한 방식의 이유: 원인을 제거하면서 변경형 Git과 task 계약의 안전 경계를 유지한다.

### 적용

- 변경 경로: 공통 prompt·guard, host adapter, renderer, 테스트, 운영 문서.
- 구현·수정·리팩터링 내용: native hook JSON, lifecycle 분리, Git classifier 단일화, agent schema 검증.
- 핵심 동작: 일반 조사와 종료는 막지 않고 finish/verify/close/preserve에서만 필수 산출물을 강제한다.

### 사용 기술과 구체적 목적

| 기술·구조·패턴 | 해결하려는 구체적 문제 | 적용 위치와 방식 |
| --- | --- | --- |
| Lifecycle state separation | Stop 자동 continuation 무한루프 | Stop과 완료 workflow 분리 |
| Fail-closed command parser | 조회 허용 중 변경 명령 우회 방지 | `branch_guard.py` 공통 분류 |
| Native JSON contract | SessionStart invalid output | Codex 전용 context serializer |
| Regression tests | 실제 오류 재발 방지 | guard/rendering 테스트에 재현 사례 고정 |

### 결과

- 적용 전: 읽기→쓰기→종료 gate가 상호 차단되어 사용자가 세션을 중단해야 했다.
- 적용 후: 읽기 전용 조사는 즉시 허용되고 산출물은 현재 세션에 쓸 수 있으며 일반 종료가 자동 재개되지 않는다.
- 검증 결과: unittest 111/111, 중앙 및 두 프로젝트 audit PASS.
- 사용자 후속 피드백: 구현 시작 승인.
- 추가 요청 및 남은 제한: main 병합, 별도 소비자 sync 승인과 신규 세션 smoke test.

```mermaid
flowchart LR
  Before[조회·문서·종료 gate 교착] --> Change[Lifecycle 분리와 공통 Git 분류]
  Change --> After[조사 허용·완료 시점 검증·정상 종료]
```

### 이력서·포트폴리오 문구

- 이력서 bullet: Codex·Claude·OpenCode 공통 정책 런타임의 lifecycle과 Git 명령 분류를 재설계해 종료 무한루프와 승인 교착을 제거하고 111개 회귀 테스트로 검증.
- 포트폴리오 서술: 실제 세션 로그에서 Stop hook의 자동 continuation과 다중 gate 교착을 식별하고, 공통 guard 재사용과 명시적 완료 상태 기계로 분리해 안전성과 작업 가능성을 동시에 회복했다.
