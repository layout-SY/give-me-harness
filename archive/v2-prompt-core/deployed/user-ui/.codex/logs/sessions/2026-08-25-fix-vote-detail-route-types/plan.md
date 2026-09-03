# 계획

## 목표

`VoteDetailRoute`의 `Unsafe assignment of an error typed value`를 제거한다. `useVoteDetailQuery` 결과가 오류 유형으로 추론되지 않게 import 경계를 고친다.

## 범위

- `CitizenParticipationDetailRoutes.tsx`의 feature barrel import를 훅·페이지 깊은 경로로 교체

## 제외 사항

- 투표 상세 API/DTO 변경
- `VoteDetailPage` 마크업 변경
- citizen-participation 전체 라우트의 barrel import 일괄 제거

## 제약 조건

- 사용자 지시: `Fix it`
- 동작은 유지하고 import/타입 경계만 수정

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| import 수정 | Hephaestus | coding-convention, type-definition | 훅 반환 타입이 해석됨 |
| 검증 | Hephaestus | documentation | eslint·관련 테스트 통과 |
| 문서 | Hephaestus | documentation, portfolio | 세션 산출물 8종 |

## 검증

대상 파일 eslint, 상세 라우트 vitest

## 위험 요소 및 결정 사항

- 같은 파일의 토론 라우트도 barrel을 쓰면 같은 오류가 날 수 있어 함께 깊은 경로로 옮긴다.

## 승인

- 상태: approved
- 승인 문구: `Fix it`
