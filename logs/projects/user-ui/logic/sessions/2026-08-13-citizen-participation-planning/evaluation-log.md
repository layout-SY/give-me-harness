# 평가 로그

## 현재 판정과의 경계

여기서는 Watcher 판정을 다시 평가하지 않는다. 구현 전 계획의 장기 구조 위험만 기록한다.

## 장기 관찰 사항

- 제안·투표·토론·정책·설문은 목록/상세 외형이 비슷해도 상태 전이와 mutation 의미가 다르므로 도메인 모델을 합치지 않는다.
- 카드 UI shell과 filter control은 실제 UI 2개 이상에서 props 계약이 반복된 뒤 공용화한다.

## 목록에 등록할 재사용 가능 자산

- 구현과 검증이 끝난 뒤 query key factory, paged DTO, API result unwrap이 도메인 중립임이 확인되면 `.codex/memory/reusable-assets.md` 등록을 검토한다.
- 현재는 미구현 계획이므로 등록하지 않는다.

## 기술 부채

- 기존 `useApi`와 TanStack Query가 공존하면 오류 표시 정책이 이원화될 수 있다.
- `ApiClient`의 `ApiResult`는 실패를 resolve하므로 query adapter가 누락되면 TanStack Query가 성공으로 오인할 수 있다.
- 실제 backend schema 없이 만든 fixture는 계약 드리프트 위험이 있다.

## 프로세스 개선 사항

- backend와 endpoint/envelope/status/pagination 표를 먼저 합의하고 OpenAPI 또는 JSON schema로 고정한다.
- Claude Code UI와 연결할 props/callback 타입을 UI 구현 전에 문서로 교환한다.
- mock fixture를 예시 데이터가 아닌 승인된 계약의 executable specification으로 관리한다.

## 권고 사항

도메인별 독립 API/query를 유지하고, 반복이 실제로 확인된 query key 및 pagination 경계만 shared로 승격한다. 구현 전에 `plan.md`의 10개 결정 항목을 해소한다.
