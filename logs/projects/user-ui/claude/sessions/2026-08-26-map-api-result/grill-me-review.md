# Grill-me 검토

사용자 지시가 범위(로컬 `toCreatedProposalResult`를 전역 패턴으로 교체)를 이미 지정했다. 별도 grill-me 인터뷰는 진행하지 않았다.

확인된 결정:

- 공용 변환: `mapApiResult`가 실패 통과 + 성공 data 매핑
- 성공 envelope 생성: 기존 `toApiResult` 재사용
- 도메인 변환: 제안 Location 파서, 투표 zod schema는 각 API에 유지
- 제외: 훅 `unwrapApiResult` 경로, 토론·댓글 like
