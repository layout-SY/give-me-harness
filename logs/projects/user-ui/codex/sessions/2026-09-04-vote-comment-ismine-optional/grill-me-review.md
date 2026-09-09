# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

구현 전에 원인 설명과 선택지를 제시했고, 사용자가 `isMine` optional과 목록 렌더링 복원을 선택했다. 아래는 그 결정 트리다.

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 실패 위치 | 목록이 안 그려지는 직접 원인은 parser인가 UI인가? | `getVoteCommentListResponseSchema.parse`가 `isMine` 누락으로 실패한다. | 실제 응답에 `isMine` 없음, `voteCommentSchema` 필수 boolean | 스키마를 실제 응답에 맞춘다. |
| 필드 의미 | 없는 `isMine`을 `false`로 채울 것인가, 부재로 둘 것인가? | 사용자는 optional을 요청했다. 백엔드 추가가 보류다. | 사용자 지시, `commentSchema`도 optional | `z.boolean().optional()` |
| 소유권 동작 | 필드가 없을 때 수정/삭제는 열려야 하는가? | 열면 안 된다. `isMine === true`만 관리 대상이다. | `useCitizenCommentActions.ts` | hook을 바꾸지 않는다. |
| 테스트 | `isMine` 없는 응답을 계속 거절해야 하는가? | 지금은 성공해야 목록이 산다. | 기존 거절 테스트가 화면 장애를 고정하고 있었음 | 성공 계약으로 바꾼다. |
| 진단 로그 | `<field>` 마스킹도 같이 고칠 것인가? | 이번 범위에서 제외한다. | 사용자 후속 지시가 목록 렌더링에 집중 | 별도 작업으로 남긴다. |

## 결론

- 목록 파싱 실패를 막기 위해 vote comment `isMine`만 일시 optional로 둔다.
- 소유권 UI는 서버 필드가 올 때까지 비활성인 상태가 계약과 맞다.
- 진단 로그 필드명 노출과 필수 전환은 후속 작업이다.
