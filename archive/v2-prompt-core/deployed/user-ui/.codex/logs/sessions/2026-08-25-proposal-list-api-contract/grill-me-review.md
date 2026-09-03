# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

별도 grill-me 인터뷰 세션은 열지 않았다. 아래 행은 구현 전에 사용자 대화에서 닫힌 분기만 기록한다.

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 목록 요청 필드 | proposal list 요청에 어떤 query가 포함되어야 하는가? | `page`와 `size`만 추가한다. | 사용자: `API 요청단에는 page/size만 추가` | list DTO에서 `status`/`sort`/`myActivity`를 빼고 `page`/`size`만 보낸다. |
| 내 활동 필터 | 내 활동 데이터는 어느 요청으로 받는가? | 별도 API이며 `content`로 페이지를 구분하고 `page`/`size`가 필요하다. | 사용자: `?content='proposal' or ?content='vote'`, `여기에도 page,size가 있어야돼` | 기존 `/me/activity`에 `content`·`page`·`size`를 보내고 list URL에는 `myActivity`를 넣지 않는다. |
| DTO 사용처 | 새 응답을 옛 content list DTO로 되돌릴 것인가? | 아니오. 확정 구조가 목록 계약의 단일 출처다. | 사용자 확인: `API 요청 및 DTO 사용처의 dto를 변경` | `parseProposalList`와 `toProposalListItem`이 `GetProposalListResponseDto`를 직접 사용한다. |

## 결론

닫힌 분기는 구현에 반영했다. 열려 있는 것은 activity 응답 본문과 proposal 상세 계약이다.
