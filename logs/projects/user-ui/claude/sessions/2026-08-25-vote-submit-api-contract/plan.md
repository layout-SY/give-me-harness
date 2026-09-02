# 계획

## 목표

투표하기 POST를 확정 요청 `{ choice }`와 409 코드(`ALREADY_VOTED`·`VOTE_NOT_STARTED`·`VOTE_CLOSED`·`VOTE_CANCELLED`)에 연결한다. 진행 중인 투표만 성공하고 1인 1표는 재투표를 거절한다.

## 범위

- `VoteRequestDto`를 `{ choice }`만 전송
- `VOTE_CONFLICT_CODE`와 MSW 409 분기
- 문자열 `code`를 `toServerResponse`/`ApiError`가 보존
- `parseVoteResponse`와 `useVoteMutation`이 choice만 전달

## 제외 사항

- 미확정 200 응답 재설계. 기존 `{ id, completed, choice }` 유지
- POST 경로를 `/responses`에서 변경
- `VoteDetailPage` 마크업·409 안내 UI
- 댓글 API 변경

## 제약 조건

- 사용자 지시: `얘도 연결해줘`
- 성공 응답 JSON은 이번 요청에 없음. 임의로 바꾸지 않음
- Claude Code 소유 `VoteDetailPage`는 읽기 전용

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| DTO/API | Hephaestus | recipe-api-authoring, recipe-data-dto | choice만 전송 |
| 오류 계약 | Hephaestus | type-definition, data-fetch-layer | 409 코드 구분 |
| MSW/테스트 | Hephaestus | recipe-api-authoring | status별 409 검증 |
| 문서 | Hephaestus | documentation, portfolio | 세션 산출물 8종 |

## 검증

관련 vitest, `npm run lint`, `npm run build`

## 위험 요소 및 결정 사항

- 공용 `code`를 숫자만 받으면 문자열 409가 0으로 떨어진다. `number | string`으로 보존한다.
- 라우트는 `IN_PROGRESS`가 아니면 POST하지 않는다. 서버 409는 레이스·직접 호출용이다.

## 승인

- 상태: approved
- 승인 문구: `얘도 연결해줘`
