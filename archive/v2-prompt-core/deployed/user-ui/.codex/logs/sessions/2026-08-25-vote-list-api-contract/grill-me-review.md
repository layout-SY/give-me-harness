# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

별도 grill-me 인터뷰 세션은 열지 않았다. 아래 행은 구현 전에 사용자 대화에서 닫힌 분기만 기록한다.

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 목록 계약 분리 | 투표 목록을 공용 content list DTO에 남길 것인가? | 아니오. proposal과 같이 전용 DTO를 쓴다. | 사용자 확정 JSON과 구현 전 계획 확인 후 `작업 진행` | `GetVoteListQueryDto`/`GetVoteListResponseDto`와 `parseVoteList`를 사용처까지 관통한다. |
| status 어휘 | 토론·설문·정책 status도 `IN_PROGRESS`로 바꿀 것인가? | 아니오. 투표만 `IN_PROGRESS`/`CLOSED`. | 계획: `PARTICIPATION_STATUS` 유지. 사용자 승인 `작업 진행` | `VOTE_STATUS`를 추가하고 다른 타입은 `scheduled`/`open`/`closed`를 유지한다. |
| 선택 query | 첫 화면에서 `status`/`sort`를 보낼 것인가? | 아니오. `page`/`size`만 보낸다. 필터 UI는 추가하지 않는다. | 계획 제외 사항. 사용자 승인 `작업 진행` | DTO에는 optional 필드를 두고 라우트는 `{ page, size }`만 전달한다. |
| 내 활동 | 투표 내 활동도 목록 DTO로 바꿀 것인가? | 아니오. 기존 activity content list를 유지한다. | 계획 제외 사항. 사용자 승인 `작업 진행` | `useMyActivityQuery("vote")` + `toVoteListItemFromContent` |
| 미허용 status | `UPCOMING`/`CANCELLED`를 클라이언트에 넣을 것인가? | 아니오. 서버는 400을 주고 클라이언트는 보내지 않는다. | 사용자 요청 설명과 계획 | `z.enum(VOTE_STATUS)`만 허용한다. |

## 결론

닫힌 분기는 구현에 반영했다. 열려 있는 것은 투표 내 활동 응답 본문, 투표 상세 envelope, status/sort 필터 UI다.
