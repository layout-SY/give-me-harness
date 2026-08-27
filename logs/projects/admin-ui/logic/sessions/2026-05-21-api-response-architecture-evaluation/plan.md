# 계획 로그

## 단계
- 에이전트: planner
- 상태: approved

## YAML 결과
```yaml
summary: API 응답 envelope 의존을 도메인 API에서 제거하고 discussion 도메인부터 `Promise<T> + throw` 장기 구조로 전환한다.
decision: plan_ready
work_type: refactor
scope:
  in:
    - src/apis/common/api-result
    - src/apis/api-client.ts
    - src/apis/services/dao/discussion/discussion.api.ts
    - src/pages/dao/discuss-posts-management/**
  out:
    - 전체 API 도메인 일괄 전환
    - interceptor에서 Dialog 직접 표시
    - UI 레이아웃/퍼블리싱 변경
    - unrelated 기존 경로 깨짐 수정
sections:
  - 응답 구조 평가 및 경계 결정
  - typed apiClient 추가
  - ServerResponse unwrap + CustomException throw 경계 추가
  - discussion API 반환 계약 전환
  - discussion hook/page 호출부 result.success 분기 제거
  - lint/type 영향 검증
required_agents:
  - planner
  - refactorer
  - watcher
  - evaluator
required_skills:
  - policy-abstraction-strategy
  - policy-refactoring
  - policy-coding-convention
  - hook-use-api
  - recipe-data-dto
  - policy-documentation
approval_request: 사용자가 "장기 구조 방식으로 리팩토링 진행" 및 "unknown 타입 없이 진행"을 명시해 승인한 것으로 처리한다.
reasons:
  - ServerResponse는 백엔드 공통 envelope이므로 도메인 API가 직접 알 필요가 낮다.
  - useApi.execute가 이미 try/catch 기반이므로 ApiResult 값 모델보다 throw 모델이 hook 제어와 잘 맞는다.
  - 전체 전환은 위험하므로 discussion 도메인부터 국소 적용한다.
artifacts:
  - plan.md
  - exploration.md
next_action: refactorer_execute
log:
  - 승인 전에는 평가/계획만 진행했고, 사용자 승인 후 코드 리팩터링을 진행했다.
status: ready_for_approval
```

## 범위 정의
- 현재 변경은 API 응답 구조의 장기 방향을 `discussion` 도메인에 먼저 적용하는 구조 리팩터다.
- 기능 추가가 아니라 반환 계약과 실패 처리 경계를 정리하는 작업이므로 `refactor`로 분류한다.
- `ApiResult<T>` 전체 제거는 후속 백로그로 남긴다.

## 의존 방향
- 허용:
  - `domain api -> apiClient`
  - `apiClient -> api-result common`
  - `hook/page -> useApi.execute -> domain api`
- 금지:
  - `domain api -> ServerResponse` 직접 의존
  - `domain api -> toApiResult` 직접 의존
  - `axios interceptor -> UI Dialog` 직접 의존

## 에이전트 실행 순서
1. evaluator: 구조 리스크와 장기 방향 진단
2. planner: 적용 범위와 에이전트 순서 결정
3. refactorer: discussion 범위 구조 리팩터 적용
4. watcher: 체크리스트 기반 pass/fail 판정
5. evaluator: 결론/백로그 문서화
6. planner/orchestrator: final-summary 작성
