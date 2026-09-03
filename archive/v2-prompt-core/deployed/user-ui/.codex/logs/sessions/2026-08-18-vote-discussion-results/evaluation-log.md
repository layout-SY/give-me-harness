# 평가 로그

## 현재 판정과의 경계

여기서는 Watcher 판정을 다시 평가하지 않는다.

## 장기 관찰 사항

- 전체 lifecycle 상태와 개인 submission 상태를 분리한 계약은 Survey 등 다른 참여 기능에도 재사용 가능하다.
- POST 후 상세 GET 일관성을 제공하는 stateful MSW factory가 화면 상태 회귀를 잘 포착한다.

## 목록에 등록할 재사용 가능 자산

- `calculateVotePercentages`: 기존 Vote 비율 계산 재사용
- `resultRatios.ts`: UI ratio 이름으로 변환하는 presentation adapter
- `createCitizenParticipationHandlers`: 사용자 선택과 댓글 reaction을 격리하는 stateful mock factory

## 기술 부채

- `mocks/fixtures.ts`가 pure LOC 246이므로 다음 데이터 확장 시 반드시 분리해야 한다.
- 공통 `ContentDetailDto`의 domain별 개인 선택 optional 필드는 content union schema로 발전할 여지가 있다.

## 프로세스 개선 사항

- Claude UI 완료 신호에 prop 이름·문구·disabled 조건을 포함하면 통합 재확인 횟수를 줄일 수 있다.
- mutation 완료 화면은 request body, response, refetch persistence, DOM 변화 네 층을 함께 검증한다.

## 권고 사항

- 실제 backend 계약 확정 시 `myVoteChoice`와 `myDiscussionChoice` 명칭을 OpenAPI와 대조한다.
- 다음 mock 데이터 추가 전에 fixture 모듈을 content/comment로 분리한다.
