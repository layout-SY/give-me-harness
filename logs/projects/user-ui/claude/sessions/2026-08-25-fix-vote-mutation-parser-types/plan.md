# 계획

## 목표

`useVoteMutation`의 `.then(parseVoteResponse)`에서 나는 `Unsafe argument of type error typed`를 제거한다.

## 범위

- `voteApi.postVote`가 `vote.dto` 스키마로 응답을 파싱
- mutations는 `unwrapApiResult`만 사용

## 제외 사항

- 투표 요청/응답 JSON 계약 변경
- `VoteDetailPage` 마크업
- parser의 `parseVoteResponse` 삭제

## 제약 조건

- 사용자 지시: `Fix it`
- 생성 POST와 같은 패턴: API에서 파싱하고 훅은 parser god 모듈을 `.then`하지 않는다

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| API/훅 | Hephaestus | type-definition, coding-convention | error 유형 인자 제거 |
| 검증 | Hephaestus | documentation | eslint·vitest 통과 |
| 문서 | Hephaestus | documentation, portfolio | 세션 산출물 8종 |

## 검증

대상 eslint, 관련 vitest

## 위험 요소 및 결정 사항

- mutations가 `citizenParticipation.parser`를 `.then`하면 parser 순환으로 함수가 `error` 유형이 된다.

## 승인

- 상태: approved
- 승인 문구: `Fix it`
