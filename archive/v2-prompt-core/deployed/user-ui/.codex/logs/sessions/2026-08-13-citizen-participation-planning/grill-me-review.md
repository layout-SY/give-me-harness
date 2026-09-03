# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| endpoint | backend가 예정한 base namespace는 무엇인가? | 미확정 | PDF에 endpoint 없음 | `/v1/api/citizen-participation` 임시 사용 |
| envelope | 성공/오류 응답 구조는 무엇인가? | 미확정 | 기존 저장소는 `ServerResponse<T>` 사용 | 기존 envelope 유지 |
| 인증 | 조회와 mutation의 인증 정책은 각각 무엇인가? | 미확정 | 사용자 활동과 제출에는 사용자 식별 필요 | 공개 조회와 인증 mutation 구분 |
| pagination | page 기준과 metadata는 무엇인가? | 미확정 | PDF는 댓글 pagination만 표현 | 1-based page + item/page count |
| mock | mock server 활성 조건은 무엇인가? | 미확정 | 실제 backend 전환 필요 | `VITE_ENABLE_MSW=true` |
| 상태 | 도메인별 상태 값과 사용자 동작은 무엇인가? | 일부 UI label만 확인 | backend 상태 계약 없음 | backend wire value 확정 후 constants 작성 |
| form | 필수 필드와 제한은 무엇인가? | 일부 필수 표시만 요구 | API validation 계약 없음 | 규칙 수신 후 Zod schema 확정 |
| routing | 상세 이동이 새로고침·공유 가능해야 하는가? | 요구상 id 상세 조회 필요 | state-only 이동은 직접 접근 불가 | URL parameter 사용 |

## 결론

계획은 임의로 backend 계약을 확정하지 않았고 각 미확정 항목에 선택 가능한 권고안을 제공한다. 사용자 답변과 명시적 승인 전에는 애플리케이션 구현을 시작할 수 없다.
