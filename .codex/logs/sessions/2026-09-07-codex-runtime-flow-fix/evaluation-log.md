# 평가 로그

## 현재 판정과의 경계

여기서는 현재 변경의 PASS/FAIL을 다시 판정하지 않는다.

## 장기 관찰 사항

Lifecycle hook은 대화 제어와 완료 검증을 한 이벤트에 결합하면 호스트별 의미 차이 때문에 교착이 발생한다. SessionStart는 context 주입, Stop은 관찰·로그 수집, finish 계열은 완료 검증으로 역할을 분리하는 편이 안정적이다.

## 이 문제가 중요한 이유

에이전트가 오류를 설명하려고 종료할 때마다 같은 Stop hook이 자동 continuation을 만들면 사용자가 대화를 끝낼 수 없고, 문서를 쓰려 해도 별도 guard가 막는 상호 차단 상태가 된다.

## 재사용 가능 자산

- `branch_guard.git_command_mutates`
- `managed_policy_guard.emit_session_context`
- renderer의 host별 hook 등록 감사
- 명시적 branch workflow 완료 lifecycle

## 기술 부채

- shell parser가 지원하는 Git option 범위는 Git 버전 변화에 맞춰 지속 보강해야 한다.
- 전역 Codex 설정 drift와 프로젝트 관리 설정 drift를 한 audit 보고서에서 구분해 보여줄 수 있다.

## 추상화·아키텍처·의존성 방향

- hook event별 출력 encoder를 공통 typed 구조로 확장하면 잘못된 JSON 회귀를 더 줄일 수 있다.
- 승인·branch·artifact 계약은 독립 상태 기계로 유지하되 최종 lifecycle command에서 조합한다.

## 프로세스 개선 사항

- 사용자 보고 오류 문구를 그대로 회귀 테스트 이름과 assertion에 반영한다.
- sync 전에는 project별 요약 diff와 누적 migration diff를 분리해 제시한다.

## 권고 사항

- 실제 소비자 배포 후 신규 inject와 sync 세션 각각에서 짧은 smoke test를 수행한다.
- deprecated 경고가 남으면 사용자 전역 config를 읽기 전용으로 확인한 뒤 별도 수정 승인을 받는다.

## 개선 선택지와 권장 backlog

- 선택지 A: 현재 event별 encoder 유지 — 변경량이 작음.
- 선택지 B: hook output type/serializer 모듈화 — 이벤트가 더 늘 때 유리함.
- 권장: 현 시점에는 A를 유지하고 다음 hook event 추가 시 B를 backlog로 승격한다.

## 다음 제안 단계

main 병합 후 소비자별 diff를 승인받아 sync하고, 실행 중 세션은 handoff 후 새 launcher로 시작한다.
