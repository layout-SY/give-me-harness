# 리뷰 로그

## 리뷰 대상
- 활동 로그 목록 query DTO, getList, MSW, 목록 페이지 분해

## 결과
- Generator self-review 통과, Watcher 미실행 → `paused_after_generator`

## 체크리스트 검토
- SKILL 준수: query key에 필터/페이지 포함, AbortSignal 전달, Zod parser, 페이지 fixture import 없음
- 재사용 확인: 공용 목록 추상화 훅을 만들지 않고 도메인 전용 훅 복제
- 검증 확인: tsc/eslint, 브라우저 조회·초기화·상세 회귀
- Payload 완결성: 목록 아이템에 `targetType` 필수, count에 `todayCount`와 활동유형 tab count
- 성능 우려: `placeholderData: previousData`로 페이지 전환 시 깜빡임 완화
- 중복 코드 우려: vote/survey와 구조가 닮았으나 공용화 4조건 미충족으로 복제 유지

## 위반 사항
1. 없음 (self-review)

## 필수 수정 사항
1. 없음

## 반복 이슈
- false

## 에스컬레이션
- none
