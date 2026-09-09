# 평가 로그

## 상태

- 전체 13개 도메인 적용 후 장기 평가 예정.
- Proposal 기준 구현에서 후속 목록형 도메인에 재사용할 API/MSW/query 경계를 확정했다.

## 평가 항목

- query key 누락과 과도한 invalidation
- DTO/schema/model 중복
- 상태 vocabulary drift
- mock helper의 과잉 추상화 여부
- 실제 backend 교체 비용

## Proposal 기준 관찰

- TanStack Query 목록은 `useFetchAdapter`와 혼합하지 않고 query key가 filter·page를 전부 소유하는 구조가 적합하다.
- MSW 상대 경로는 외부 `VITE_API_BASE_URL` 요청을 가로채지 못하므로 `*/v1/...` wildcard 패턴이 필요하다.
- 많은 페이지 번호는 문서 전체가 아니라 Pagination 내부에서 수평 스크롤해야 한다.
- 공용 Navigation의 callback type은 generic으로 보존해야 enum consumer의 strict function type 오류를 피할 수 있다.
- 목록·상세 mutation은 유효값뿐 아니라 persisted value와 비교한 dirty guard를 버튼과 submit 양쪽에 적용해야 한다.
- 모바일에서 화면 밖으로 이동한 navigation content는 시각적 숨김만으로 부족하며 `inert`로 탭 순서도 격리해야 한다.
