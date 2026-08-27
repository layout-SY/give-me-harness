# 리뷰 로그

## 리뷰 대상
- 신고 목록/상세 query·MSW·controller-view 전환

## 결과
- paused_after_generator (Watcher 미실행)

## 체크리스트 검토
- SKILL 준수: 페이지 fixture import 제거, query key에 필터·페이지 포함, AbortSignal 전달, 부수효과는 surface
- 재사용 확인: 공용 목록 컨트롤러 미추출, 게시판 패턴만 도메인 전용으로 복제
- 검증 확인: tsc/eslint 통과, 목록 저장·상세 저장·404 렌더 확인
- Payload 완결성: process는 변경 필드만, 목록은 status/memo, 상세는 status/exposure/memo
- 성능 우려: 없음
- 중복 코드 우려: 도메인 전용 hook 유지

## 위반 사항
1. 없음 (Generator 자체 점검)

## 필수 수정 사항
1. 없음

## 반복 이슈
- false

## 에스컬레이션
- none
