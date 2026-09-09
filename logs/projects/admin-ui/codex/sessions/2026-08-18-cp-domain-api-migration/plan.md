# CP 전체 도메인 API 마이그레이션 계획

## 결론

- Dashboard 기준 구현을 나머지 13개 CP entity에 도메인별 수직 슬라이스로 적용한다.
- 목록형 도메인은 UI 필터·페이지를 query key와 Axios params에 포함하고 MSW가 필터·pagination을 수행한다.
- 페이지의 fixture 직접 import를 제거하고 fixture는 mock API의 seed 데이터로만 사용한다.
- 각 도메인은 Watcher PASS 후 다음 도메인으로 진행한다.

## 임시 데이터 기준

- 일반 목록형 도메인: 120건 이상의 결정적 seed 데이터
- 활동 로그: 240건 이상의 결정적 seed 데이터
- 상세·설정 singleton: 기존 fixture 보존 후 mutation 가능한 session state로 전환
- 브라우저 전체 새로고침 이후 durable persistence는 현재 범위에서 제외

## 적용 순서

1. Proposal
2. Vote
3. Discussion
4. Policy
5. Survey
6. Comment
7. Report
8. Board
9. Notice
10. Activity Log
11. Reward
12. Main Display
13. Operation Policy

## 공통 계약

- API: `ApiClient<unknown> → unwrapApiResult → Zod parser`
- Query: query 결과를 바꾸는 모든 필터·페이지를 query key에 포함
- 목록 응답: `ServerResponse<TableApiResponseDto<TItem, TTab>>`
- Mutation: 갱신된 entity를 반환하고 영향받는 최소 query key만 invalidate
- MSW: 400/404/409 오류 계약과 handler factory closure state 사용

## 역할과 SKILL

- Generator: DTO·parser·API·query/mutation·MSW·UI 연결
- Watcher: 현재 섹션 pass/fail 판정
- Evaluator: 전체 완료 후 장기 중복·상태 vocabulary 평가
- 적용: `recipe-api-authoring`, `recipe-data-dto`, `recipe-data-fetch`, `policy-tanstack-query`, `component-table`
