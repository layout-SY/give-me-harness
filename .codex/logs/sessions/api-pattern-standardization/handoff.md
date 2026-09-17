# API 패턴 정리 인계

## 완료 상태

중앙 API 스킬 4개를 수정하고 공통 references 2개를 추가했다. user-ui useApi와 회귀 테스트를 수정했으며 global AGENTS.md의 레거시 스택 안내를 제거했다. 상세 조사·전수 목록·세션 산출물 조사와 portfolio를 작성했다. 검증은 final-summary/review-log를 따른다.

## 후속 담당자가 먼저 읽을 자료

1. docs/api-pattern-audit-2026-09-17.md: 도메인별 패턴, API-01~13 문제·근거·우선순위.
2. docs/api-pattern-inventory-2026-09-17.md와 operations JSON: 조사 당시 HEAD·file hash·연결 상태.
3. docs/session-portfolio-audit-2026-09-17.md: 실제 활성 6개 assignment와 산출물 상태.
4. policy/common/skills/recipe/api-authoring/SKILL.md 및 필요한 references.

## 재시작과 소유권

기존 소비자 assignment의 고정 bundle은 자동 업데이트되지 않는다. 각 세션 owner가 본인의 worktree·변경·검증·남은 작업을 handoff하고 중앙 launcher로 새 inject 세션을 시작해야 한다. `--resume-assignment`는 이전 bundle을 유지한다. `bin/agent-policy start --project <project> --host <host> --mode inject --role <role> --responsibility owner --worktree <current-worktree>` 형태에 현재 모델 인자를 보존하고 `--print-only`로 먼저 확인한다.

이번 작업에서 기존 세션을 강제 종료하거나 타인의 세션에 메시지를 보내지 않았다. 현재 열려 있는 세션의 작업을 복제하는 새 세션도 기동하지 않았다. 다음 실행은 그 세션 owner가 인계를 수락한 뒤 수행한다. 이 문서는 새 bundle 적용 완료를 뜻하지 않는다.

## 보존해야 할 변경

중앙 repo에는 이번 작업 이전부터 여러 policy/runtime/test 변경이 있다. consumer user-ui에는 회의 진입·미디어 변경, admin에는 다른 API 도메인의 동시 변경·commit이 있다. 이전 status를 기준으로 일괄 restore/reset하지 않는다. 이번 consumer 수정 경로는 shared/lib/hooks/use-api.tsx와 use-api.test.tsx뿐이다.

## 남은 위험·검증

user-ui 전체 suite 38개 실패를 별도 조사한다. CP cache race, user mutation parser, DAO POST config, event fallback 개선의 기준본 통합 여부는 각 담당자에게 인계할 검토 항목이다. 활성 6개 세션의 portfolio는 조사 당시 모두 없었으므로 각 owner가 실제 근거로 작성해야 한다. 실 backend 정상 동작과 성능 향상 수치는 확인하지 않았다.

## 후속 요청: 작업 단위 커밋

사용자의 “작업 단위 커밋” 요청에 따라 중앙 공통 스킬과 user-ui 구현을 별도 커밋했다.

- 중앙 `main`: `34f2dab` — `refactor: 공통 API 연결 스킬과 요청 수명 규칙 정리` (6개 파일).
- user-ui `sy-main`: `57c88ac` — `fix: useApi 동시 요청을 최신 호출 기준으로 처리` (구현·회귀 테스트 2개 파일).
- 조사 문서·검증 근거·이번 세션 산출물 7종은 별도의 문서 커밋으로 묶는다.

작업 시작 시 보관한 원본과 비교해 api-authoring의 기존 2·6·9번 지침 변경은 스테이징에서 제외했다. 기존 다른 세션의 소스·정책·로그 변경은 보존했다. 전역 `/Users/okand/.codex/AGENTS.md`는 Git 저장소 밖이어서 수정 상태만 유지한다. 구현은 검증 당시 내용과 동일하며 기존 테스트 결과·전체 suite 실패 제한을 유지한다.
