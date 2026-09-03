# 탐색

## 결론

- Dashboard를 제외한 13개 CP entity는 API 골격이 있으나 페이지가 fixture를 직접 소비한다.
- 목록 UI의 상태·유형·검색어·기간 필터 대부분은 현재 데이터 요청에 연결되지 않는다.
- `Table`은 표시 컴포넌트로 재사용하되 신규 CP 목록의 서버 상태는 TanStack Query가 단독 소유한다.
- `useFetchAdapter`는 `useApi`와 로컬 서버 상태를 소유하므로 신규 TanStack Query 목록과 혼합하지 않는다.
- 현재 UI에 정렬 입력이 없는 화면에는 임의의 sort query를 추가하지 않는다.

## API 범위

- 참여형 도메인: 목록·상세·처리 15 endpoints
- 운영형 도메인: 댓글·신고·게시판·공지·활동·보상 19 endpoints
- 설정형 도메인: 메인 노출·운영 정책 6 endpoints
- 총 약 40 endpoints

## 임시 계약

- 실제 backend 명세가 없어 query/body 필드명은 현재 UI state와 프로젝트 convention을 기준으로 한다.
- pagination은 1-based `page`, `size`를 사용한다.
- 날짜 범위는 `startDate`, `endDate`를 사용한다.
- 이 계약은 실제 backend 명세가 제공되면 교체한다.
