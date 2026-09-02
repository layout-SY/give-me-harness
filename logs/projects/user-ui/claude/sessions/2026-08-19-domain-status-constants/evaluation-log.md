# 평가 로그

## 현재 판정과의 경계

Watcher 판정을 반복하지 않고 이후 계약 확장 위험만 기록한다.

## 장기 관찰 사항

- domain constant와 UI value를 같은 이름으로 export하지 않는 구조가 의미 혼동을 줄인다.
- API uppercase와 UI lowercase를 route adapter로 분리하면 backend 계약 변경이 production UI에 전파되지 않는다.
- VoteChoice와 OpinionStance 저장소 분리는 겹치는 값이 있어도 서로 다른 개념임을 타입으로 유지한다.

## 기술 부채

- `ContentStatus`와 `contentStatusSchema`는 ProposalStatus와 미확정 participation lifecycle의 공용 union이다.
- backend가 나머지 lifecycle 값을 확정하면 content type별 discriminated schema와 query DTO로 분리해야 한다.
- `fixtures.ts`와 `presentation.ts`는 pure LOC 경고 구간이다.

## 권고 사항

- 다음 상태 집합을 받을 때 기존 `PARTICIPATION_STATUS`를 추측해 재사용하지 말고 도메인별 상수를 추가한다.
- content type과 status의 조합을 Zod discriminated union으로 고정한다.
- production UI가 uppercase를 직접 사용하도록 바뀌는 시점에 route adapter를 제거한다.
