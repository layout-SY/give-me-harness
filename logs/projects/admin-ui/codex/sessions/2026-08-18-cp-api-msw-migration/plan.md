# CP API 및 MSW 마이그레이션 계획

## 결론

- 기존 CP UI는 유지하고 fixture 직접 참조를 typed Axios API와 TanStack Query 서버 상태로 교체한다.
- 외부 응답은 `ApiResult`를 해제한 뒤 Zod parser를 통과시킨다.
- 개발 환경에서는 MSW가 실제 endpoint와 `ServerResponse` envelope를 재현한다.
- 한 번에 한 도메인 수직 슬라이스만 구현한다.

## 완료 섹션

- 개발 전용 MSW worker 부트스트랩과 health endpoint를 구성했다.

## 현재 섹션: CP Dashboard

1. `QueryClientProvider`와 공통 query 기본값을 구성한다.
2. Dashboard DTO·parser·ApiClient·AbortSignal·query key/hook을 구현한다.
3. Dashboard MSW handler를 추가하고 page의 fixture 직접 참조를 제거한다.
4. 최초 조회, 새로고침, refetch 실패 시 기존 캐시 유지 동작을 검증한다.
5. `recipe-api-authoring`, `policy-tanstack-query`와 세션 산출물을 갱신한다.

## 역할과 적용 SKILL

- Generator: 런타임 구현 (`recipe-api-authoring`, `recipe-data-dto`, `recipe-data-fetch`, `policy-tanstack-query`)
- Watcher: 현재 변경의 pass/fail 판정 (`policy-review-checklist`)
- Evaluator: 후속 14개 CP 도메인 확장 리스크 기록
