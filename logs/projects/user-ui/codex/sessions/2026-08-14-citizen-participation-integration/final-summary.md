# 시민참여 production UI 통합 요약

## 완료

- 13개 production route 등록
- main, 5개 목록, 5개 상세, my activity 조회 연결
- vote와 discussion 참여 mutation 연결
- service tab, shortcut, pagination, filter, search, 상세/목록 이동 연결
- DTO→UI presenter와 route regression test 추가

## 제한

- 제안 submit, comment 신고, survey 참여는 backend/UI 계약 불일치로 요청하지 않는다.
- Production UI와 shared UI는 수정하지 않았다.

## 검증

- Route·presenter 테스트 4개 통과
- 전체 Vitest 135개 중 133개 통과
- Production build 통과
- 전체 lint 통과
- 기존 meeting API insecure URL 테스트 2개 실패는 integration 범위 밖
