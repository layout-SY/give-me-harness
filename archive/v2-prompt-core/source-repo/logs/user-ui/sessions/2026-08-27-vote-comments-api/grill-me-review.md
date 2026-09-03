# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 전송 계약 | 서버가 보내는 원본 shape는 어디서 검증되는가? | vote 전용 Zod schema에서 검증된다. | `api/vote/vote.dto.ts`, `parseVoteCommentList` | transport DTO와 화면 모델을 분리한다. |
| 정렬 | 허용하지 않은 sort가 API 타입을 통과할 수 있는가? | `VoteCommentSort` 공개 타입에서는 통과하지 않는다. | `VOTE_COMMENT_SORT`, `GetVoteCommentListQueryDto` | 폐쇄형 vocabulary를 유지한다. |
| 캐시 | page가 같고 size·sort가 다른 요청이 같은 cache를 쓰는가? | 서로 다른 query object를 key에 포함한다. | `model/queryKeys.ts` | 모든 query 의존값을 key에 포함한다. |
| UI 호환 | 좋아요 정보가 없는 댓글이 가짜 좋아요 수를 표시하는가? | 해당 속성을 만들지 않아 좋아요 제어가 렌더링되지 않는다. | `comment.dto.ts`, `presentation.ts`, `CommentList` 기존 계약 | 없는 서버 필드를 합성하지 않는다. |
| 상태·오류 | vote 상태가 조회를 차단하는가? | mock의 published vote 1~4는 모두 성공하고 draft 99만 404다. | `voteComments.handlers.test.ts` | 상태와 무관한 조회 계약을 유지한다. |
| 회귀 | 일반 댓글의 좋아요·신고 흐름이 유지되는가? | discussion 경로 회귀 테스트가 통과한다. | `mocks/handlers.test.ts`, mutation tests | vote와 일반 댓글 transport를 분리한다. |

## 결론

원본 계약 검증, 정규화, cache 의존성, mock과 회귀 테스트가 같은 경계를 가리키며 차단 결함이 없다.

## 추가 검토 — nullable 제안 작성자

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 경계 계약 | 외부 응답의 null 가능성이 런타임·정적 타입에 모두 표현되는가? | Zod schema와 DTO가 모두 nullable이다. | `proposal.dto.ts` | nullability를 trust boundary에서 보존한다. |
| 화면 변환 | null 작성자를 데이터 계층에서 가짜 객체로 합성하는가? | 원본 null을 유지하고 presentation에서 빈 문자열로 변환한다. | `presentation.ts` | 표시 fallback은 presentation이 소유한다. |
| 부분 실패 | 반려 항목 한 건이 지원 상태 항목 전체를 제거하는가? | mixed 응답 parser 테스트와 module driver에서 전체 4건이 파싱된다. | `citizenParticipation.test.ts`, 직접 driver | 배열 전체 손실을 방지한다. |
| 회귀 | parser와 presentation 실패 원인을 분리해 확인할 수 있는가? | 각 경계에 별도 테스트가 있다. | 두 test 파일 | 경계별 회귀를 유지한다. |
| 범위 | production UI를 불필요하게 변경했는가? | 변경하지 않았다. | 4-file diff | UI 오류 상태는 별도 승인 작업으로 둔다. |

### 결론

실제 nullability를 경계 타입에 반영하고 기존 UI 표시 계약을 최소 fallback으로 유지했다. 차단 결함은 없다.
