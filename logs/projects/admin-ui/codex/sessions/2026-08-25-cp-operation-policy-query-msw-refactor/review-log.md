# 리뷰 로그

## 리뷰 대상
- 시민참여 운영 정책 설정 query·MSW·controller-view 전환

## 결과
- paused_after_generator (Watcher 미실행)

## 체크리스트 검토
- SKILL 준수: 페이지 fixture import 제거, policy query key, AbortSignal 전달, 부수효과는 surface
- 재사용 확인: 공용 정책 컨트롤러 미추출, 보상 정책 save/apply 패턴 재사용
- 검증 확인: tsc/eslint 통과, 저장 Dialog·적용 후 마지막 적용일 확인
- Payload 완결성: postPermission/commentPermission/reportPermission/defaultExposure/changeReason
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
