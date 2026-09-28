# 설계 점검

구현자의 자체 점검이며 사용자 답변이나 독립 Watcher 판정으로 해석하지 않는다.

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부: 구현 선택을 정답으로 전제하지 않는 질문을 먼저 기록하고 코드·실행 결과로 답변했다.
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부: 상태·요청·검증의 현재 근거를 묻고 권장 답변을 별도 열에 기록했다.

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 통합 | 남은 UI 연결은 무엇인가? | 페이지 export까지 구현, 라우트·메뉴·MSW registry는 scope 밖이다. | index.ts·승인 scope·UI handoff | 기존 소유권을 확인한 담당자에게 연결 계약 인계 |
| 검색 | 입력과 적용 검색을 어떻게 구분하는가? | local draft와 URL query를 분리한다. | use-cp-news-list-controller.ts | 현재 구조 유지 |
| 집계 | 고정 행·페이지 수의 기준은 무엇인가? | 서버 값을 그대로 전달한다. | 독립 집계를 확인한 news-list-controller 테스트 | 실 서버 의미는 API 계약 확인 |
| 수정 | 미입력과 false를 어떻게 구분하는가? | Partial draft의 undefined를 검사한다. | cp-news-form.model.ts·실제 PATCH 테스트 | 현재 DTO 경계 유지 |
| 성공 | 생성 응답에 ID가 없으면 어떻게 하는가? | void 성공 뒤 목록으로 이동한다. | 실제 POST·요청 guard 테스트 | 응답 상세를 가정하지 않음 |
| 경합 | 요청 중 화면·ID가 바뀌면 어떻게 되는가? | 공통 잠금·generation과 페이지 key로 분리한다. | request guard의 중복·생명주기 테스트·form page | UI 연결 후 실제 이동 확인 |
| 검증 | 미확인 동작은 무엇인가? | 실제 DOM 이벤트·라우터 effect 통합은 미검증이다. | implementation-log의 실행 범위 | SSR·helper 결과를 브라우저 검증으로 표현하지 않음 |
| 완료 | 전체 완료 조건이 충족됐는가? | build·commit 완료, 별도 app 타입 검사·전체 lint 기존 오류, 독립 검토·merge 대기다. | 실행 결과·Git HEAD 6f1d322·review-log | 실제 실패·미실행 상태 유지 |

## 결론

다른 페이지로 공용화하거나 새 의존성을 추가할 근거는 현재 없다.
