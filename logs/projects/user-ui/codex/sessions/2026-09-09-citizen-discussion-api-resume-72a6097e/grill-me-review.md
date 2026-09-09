# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

확인할 질문을 먼저 정리하고 현재 소스·사용자 요청·실행 결과로 답했다. 이미 계약과 사실로 확인된 사항을 사용자에게 다시 질문하지 않았다.

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 타입 | 어떤 경계에서 타입이 충돌하는가? | Zod 추론 optional의 명시적 undefined와 공통 ContentListQueryDto의 optional 계약 사이 | discussion.dto.ts·common/content.dto.ts와 수정 후 npm run build 성공 | 쿼리 키 입력에서 undefined 속성을 생략하는 최소 수정 유지 |
| 캐시 | 어떤 요청 값이 캐시 구분에 필요한가? | page·size·mine·status·search·sort | useDiscussionListQuery의 query key에 모두 반영 | 공통 DTO와 무효화 prefix 유지 |
| 검증 | 전체 테스트 실패가 현재 변경에서 발생했는가? | 현재 실행의 5개 실패가 인계된 투표 실패와 일치 | npm run test 결과와 API `/ballots`·mock `/responses` 불일치 | 기존 실패를 명시하고 투표 계약 수정은 별도 작업으로 분리 |
| 외부 계약 | 실제 backend와 호환된다고 말할 근거가 있는가? | 없음. API 테스트는 임시 계약을 확인했다 | discussion.api.test.ts의 MSW와 browserHandlers.test.ts의 로컬 HTTP 서버 | 실제 서버 호환 완료로 보고하지 않음 |
| 통합 | 현재 sy-main으로 어떤 병합 방식이 필요한가? | 두 branch가 갈라져 있어 merge commit 필요 | 분기 이후 sy-main에 예약 팝업 커밋 c79f3d8 추가 | merge-commit 최종 계약을 준비하고 별도 승인 |

## 결론

현재 타입 수정은 공통 계약을 확대하지 않고 빌드 실패를 해결한다. 테스트의 기존 실패와 실제 서버 검증 미실시는 병합 검토자가 확인할 제한이다.
