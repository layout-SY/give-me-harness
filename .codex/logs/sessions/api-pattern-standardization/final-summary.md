# 완료 결과

API 조사·개선 보고서, 전수 목록, 공통 스킬 참조와 이번 작업 포트폴리오를 작성했다. user-ui useApi를 최신 요청만 반영하고 최신 요청 종료 시 loading을 내리도록 변경했다. 전역 레거시 스택 지시를 제거했다.

## 산출물

- [조사 결과·문제·개선 근거](/Users/okand/SynologyDrive/asan-agent-policy/docs/api-pattern-audit-2026-09-17.md)
- [고유 60개 경로 / 변경본 포함 62행 전수 목록](/Users/okand/SynologyDrive/asan-agent-policy/docs/api-pattern-inventory-2026-09-17.md)
- [활성 세션 포트폴리오 조사](/Users/okand/SynologyDrive/asan-agent-policy/docs/session-portfolio-audit-2026-09-17.md)
- [이번 작업 포트폴리오](portfolio-log.md)

## 검증

useApi 새 요구의 변경 전 실패 5개를 확인했다. 수정 후 hook·직접 소비처 36개, user-ui lint/build, 중앙 344개 테스트와 audit가 통과했다. user-ui 전체 테스트는 758개 중 38개 실패하여 남은 문제로 명시했다. 세부 범위는 review-log.md에 있다.

## 세션 조사 결론

실제 소비자 세션은 user-ui 2개/admin-ui 4개다. 6개 모두 plan/final-summary가 있지만 portfolio는 0개다. 각 주입 정책이 optional로 규정하므로 무조건 정책 위반이라고 볼 수 없다. 이번 명시적 요청에는 포트폴리오를 필수로 적용했다. 다른 세션의 문서를 수정하거나 항상 필수인 정책으로 바꾸지는 않았다.

## 미완료·인계

실 서버 확인과 모든 API 문제 수정, 다른 세션의 포트폴리오 생산·새 bundle 재시작은 이번에 완료한 것으로 주장하지 않는다. 코드상 캐시 경합·DAO config·응답 검증 등 후속 우선순위는 조사 보고서에 있다. 현재 세션 및 기존 실행 세션은 handoff 후 새 inject 세션에서 새 스킬을 적용해야 한다. 후속 사용자 요청에 따른 작업 단위 커밋은 아래에 기록한다. merge는 수행하지 않았다.

## 후속 요청: 작업 단위 커밋

사용자의 “작업 단위 커밋” 요청에 따라 중앙 공통 스킬과 user-ui 구현을 별도 커밋했다.

- 중앙 `main`: `34f2dab` — `refactor: 공통 API 연결 스킬과 요청 수명 규칙 정리` (6개 파일).
- user-ui `sy-main`: `57c88ac` — `fix: useApi 동시 요청을 최신 호출 기준으로 처리` (구현·회귀 테스트 2개 파일).
- 조사 문서·검증 근거·이번 세션 산출물 7종은 별도의 문서 커밋으로 묶는다.

작업 시작 시 보관한 원본과 비교해 api-authoring의 기존 2·6·9번 지침 변경은 스테이징에서 제외했다. 기존 다른 세션의 소스·정책·로그 변경은 보존했다. 전역 `/Users/okand/.codex/AGENTS.md`는 Git 저장소 밖이어서 수정 상태만 유지한다. 구현은 검증 당시 내용과 동일하며 기존 테스트 결과·전체 suite 실패 제한을 유지한다.
