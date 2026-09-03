# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 날짜 경계 | 입력 형식과 실제 달력 유효성은 어디서 보장되는가? | 공용 `isoCalendarDateSchema`가 입력 경계에서 모두 보장한다. | 윤년·불가능 날짜·비표준 구분자 real-module 테스트 통과 | 도메인 내부가 아닌 공용 입력 boundary에서 한 번 parse한다. |
| strictness | 입력 unknown key 거부가 응답 호환성까지 바꾸는가? | 바꾸지 않는다. `.strict()`는 지정 입력 schema에만 적용했다. | comment/proposal 응답 extra key 허용, board/report strict 응답 테스트 통과 | 입력과 응답 schema를 별도 계약으로 유지한다. |
| parser 소유권 | bulk-hide 응답은 어느 계층이 신뢰 경계를 소유하는가? | CP board API parser가 소유한다. | parser/barrel 공개 및 malformed/non-array 거부 테스트 | hook local schema보다 API 공개 parser를 사용한다. |
| cache | parser 이동이 성공 후 상태 전이를 바꾸는가? | 바꾸지 않는다. detail update와 list invalidation callback이 유지된다. | Watcher 최신 diff 검토 | parser 호출만 교체하고 cache callback은 그대로 둔다. |
| 범위 | 요구와 무관한 UI·package·config 변경이 있는가? | 없다. | Watcher 최신 status/diff PASS | logic/test/session 문서만 유지한다. |
| 검증 | 저장소 baseline 실패를 branch 결함과 구분했는가? | 구분했다. 변경 파일 ESLint와 실제 테스트/build는 통과했다. | Watcher Attempt 2 PASS 및 사용자 승인 | 실행 결과를 숨기지 말고 비차단 baseline 위험으로 기록한다. |
| 병합 | 승인된 target과 방식으로 history가 반영됐는가? | `sy-main`에 ff-only로 반영돼 target/source HEAD가 `5aa158a`로 일치한다. | post-merge status·ancestry·gate 재검증 | guard를 우회하지 않고 native OpenCode 계약 아래에서 병합한다. |

## 결론

- 현재 변경에서 차단 결함은 발견되지 않았다.
- 응답·cache·UI/package 불변 조건과 승인 범위를 모두 지켰다.
- full lint/test 한계는 현 변경과 분리해 후속 프로세스 부채로 남긴다.
- Claude Code를 사용하지 않고 GPT Sol로 merge·사후 검증을 완료했다.
