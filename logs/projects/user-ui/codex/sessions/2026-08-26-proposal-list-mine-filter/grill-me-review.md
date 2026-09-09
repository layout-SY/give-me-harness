# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

별도 grill-me 인터뷰 세션은 열지 않았다. 아래 행은 구현 전에 사용자 대화에서 닫힌 분기만 기록한다.

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 내 제안 필터 | 내가 등록한 제안은 어느 요청으로 받는가? | `GET /citizen/proposals?mine=true` | 사용자: `mine=true면 토큰의 사용자가 등록한 제안만 내려간다` | 제안 목록 토글이 list API에 `mine=true`를 보낸다. `/me/activity`를 쓰지 않는다. |
| 목록 본문 | 목록 아이템에 본문 필드가 있는가? | 없다. 상세에서만 내려간다. | 사용자: `목록에는 본문 4필드가 없고 상세 조회에서만 내려간다` | list 스키마에 `background`·`content`·`expectedEffect`·`referenceCase`를 넣지 않는다. |
| 정렬 | 어떤 sort가 허용되는가? | `createdAt`·`id`, 기본 `createdAt,desc` | 사용자: `sort는 createdAt·id만 허용하며 기본값은 createdAt,desc다` | 허용 값을 상수로 두고 기본값을 전송한다. 정렬 UI는 이번 범위가 아니다. |
| 필터 문구 | 목록 필터 라벨은 무엇인가? | 「내활동만 보기」 | 사용자: `제안 목록 보기에 "내활동만 보기" 항목이 필터로 들어갔어` | 기존 토글 라벨만 바꾼다. |

## 결론

닫힌 분기는 구현에 반영했다. 열려 있는 것은 투표·토론의 `mine` 계약과 정렬 UI다.
