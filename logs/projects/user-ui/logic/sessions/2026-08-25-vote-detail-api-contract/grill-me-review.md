# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

별도 grill-me 인터뷰 세션은 열지 않았다. 아래 행은 구현 전에 사용자 대화에서 닫힌 분기만 기록한다.

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 상세 계약 분리 | 투표 상세를 공용 `ContentDetailDto`에 남길 것인가? | 아니오. 확정 JSON이 목록과 다른 전용 `data`다. | 사용자 JSON과 `작업 진행` | `GetVoteDetailResponseDto`와 `parseVoteDetail`를 사용처까지 관통한다. |
| 조회 범위 | 시작 전·중단 투표를 상세에서 파싱해야 하는가? | 예. 링크를 연 사용자에게 투표 불가 이유를 보여주기 위해 조회된다. | 사용자: `목록과 달리 시작 전·중단된 투표도 조회된다` | 상세 status에 `UPCOMING`/`CANCELLED`를 넣고 목록 필터에는 넣지 않는다. |
| myChoice | 미로그인·미투표는 필드를 생략하는가? | 아니오. `null`이다. | 사용자: `토큰을 보내지 않았거나 아직 투표하지 않았으면 null` | `myChoice: VoteChoice \| null` |
| 찬반 수 | 중단된 투표의 집계를 보여주는가? | 아니오. CLOSED만 값이 있고 중단은 가린다. | 사용자: `완료된(CLOSED) 투표에만 값이 있고 그 외에는 null` | CLOSED가 아니면 `null` |
| 댓글 | 상세 응답에 의견을 포함하는가? | 아니오. 별도 comments 조회다. | 사용자: `의견 목록은 이 응답에 없다` | 기존 comments 훅을 유지한다. |

## 결론

닫힌 분기는 구현에 반영했다. 열려 있는 것은 `VoteDetailPage`의 예정/중단 전용 뱃지와 댓글 URL 표기 통일이다.
