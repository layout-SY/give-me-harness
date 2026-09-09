# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부: 해법을 전제하지 않는 질문을 먼저 정리하고 원문 명세·현재 코드·실행 결과로 답했다.
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부: 전송·표시·동시성·완료 기준에 관한 확인 질문으로 구성했다.

아래 답변은 명세와 코드를 확인한 검토 답변이다. 새 사용자 답변이나 추가 승인을 받은 것으로 기록하지 않는다.

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 전송 계약 | 기존 폼에서 서버가 저장하는 필드는 무엇인가? | title/content/status를 PATCH한다. | 폼 payload mapper와 tests/news-form.test.mjs | type/isPinned는 폼 입력 계약이 없으므로 미전송해 기존 값을 유지한다. |
| 표시 | 메인 노출과 상단고정의 관계는 무엇인가? | 원문 명세가 관계를 정의하지 않는다. | 사용자가 제공한 5개 API 명세 | 관계를 추정하지 않고 메인 노출을 UNSUPPORTED로 표시한다. |
| 집계 | 고정 항목과 목록 집계의 관계는 어떻게 정의되는가? | 명세만으로 확정할 수 없다. | 원문 목록 응답과 parser 테스트 | totalElements/totalPages/pinnedItemCount와 서버 순서를 그대로 보존한다. |
| 응답 | mutation은 어떤 데이터를 반환하는가? | raw null이며 ApiClient에서는 undefined다. | MSW·Axios 및 mutation parser 테스트 | void로 처리하고 query를 갱신한다. |
| 동시성 | 이전 조회가 저장·삭제 후 캐시에 어떤 영향을 주는가? | 이전 요청을 취소하지 않으면 늦은 응답이 도착할 수 있다. | tests/news-mutation.test.mjs의 취소·캐시 복원 방지 테스트 | 성공 시 해당 목록·상세 요청을 취소한 뒤 갱신 또는 제거한다. |
| 사용 경로 | 기존 목록의 식별자는 실제 공지 ID와 어떤 관계인가? | 혼합 목록은 NT-형식 mock ID이고 실제 API는 숫자 ID를 사용한다. | 현재 cp-board 목록과 noticeId 라우트 | 임의 변환하지 않고 숫자 ID 목록 연결을 UI 후속 작업에 명시한다. |
| 완료 | 현재 어떤 검증 결과가 확보됐는가? | 전체 테스트 134개와 변경 파일 lint는 통과했으며 전체 lint는 실패, 빌드는 보류다. | 실행 기록과 사용자 빌드 보류 지시 | 병합 요청과 검증 완료를 구분하고 실패·미검증 상태를 유지한다. |

## 결론

승인된 Logic 구현과 실행 가능한 테스트 근거는 마련됐다. 타입/build 검증과 전체 검증 기준 충족이 남아 있다.
