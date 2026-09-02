# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

검토 질문은 “현재 선택이 옳은가”가 아니라 “사용자 요구와 공개 계약을 어떤 실행 근거로 충족하는가”에서 시작했다. 답변은 승인 pathspec의 최신 소스, Node 테스트, build, ESLint, npm clean-install dry-run과 Watcher 판정으로 제한했다.

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 요구 충족 | 현재 사용자 표면은 요청된 목록·상세 조회만 제공하는가? | 예. 목록·상세 GET, pagination, retry, 상세 이동만 남고 write surface는 제거됐다. | `cp-vote.api.ts`, 두 controller와 UI, Watcher PASS | 조회-only 요구와 일치하므로 유지한다. |
| 실제 계약 | endpoint와 query serialization은 공개 계약과 같은가? | 예. `/citizen/votes`, `/citizen/votes/{voteId}`와 반복 `sort`를 사용한다. | `cp-vote.api.ts`, contract/MSW 테스트 | API path와 `indexes: null` serializer를 계약 테스트로 계속 보호한다. |
| 데이터 정합성 | backend에 없는 데이터를 parser나 UI가 생성하는가? | 아니오. 실제 목록·상세 필드만 model에 남겼다. | DTO·parser·types·UI diff | placeholder 작성자·댓글·처리 이력·공개 정책을 복원하지 않는다. |
| 입력 경계 | 잘못된 page·size·sort·ID와 불일치 집계가 거부되는가? | 예. Zod schema와 parser가 기본값·상한·허용 어휘·양의 정수·집계 합계를 검증한다. | `cp-vote.dto.ts`, contract 테스트 | runtime schema를 외부 데이터 경계로 유지한다. |
| 서버 상태 | 요청 취소와 query key가 실제 요청 의존값을 반영하는가? | 예. 목록·상세 signal이 Axios까지 전달되고 상세 key는 검증된 ID 또는 `null`을 사용한다. | query hook과 API source, Watcher 점검 | 현재 TanStack Query 경계를 유지한다. |
| UI 책임 | UI가 transport·parser·domain mutation 책임을 포함하는가? | 아니오. UI는 controller props와 표시용 백분율만 소비한다. | Claude Code handoff와 두 UI 파일 | 기능 로직은 UI 밖에 유지한다. |
| 오류 계약 | 400·401·404가 status와 body 모두 observable하게 검증되는가? | 예. 실제 `fetch` 기반 MSW 테스트가 검증한다. | `citizen-votes-msw.test.mjs` 7개 테스트 | mock 내부 함수 호출보다 HTTP 표면 테스트를 유지한다. |
| 테스트 안정성 | Node 22 crash 해결이 assertion·검증 강도를 약화했는가? | 아니오. assertion 14개는 유지하고 Vite loader lifecycle만 `tsx` 직접 import로 교체했다. | 16/16 최종 실행과 20회 반복 exit 0 | Vite 설정 완화나 실패 무시 대신 `tsImport` 경로를 유지한다. |
| 회귀 테스트 | 삭제된 mutation 계약이 기존 테스트에 남아 있는가? | 아니오. 날짜 경계 테스트에서 시민투표 mutation schema를 제거했다. | `cp-date-input-boundaries.test.mjs`, 2개 테스트 성공 | read-only 범위와 테스트 매트릭스를 함께 유지한다. |
| dependency | 새 loader가 clean install에서 재현되는가? | 예. `tsx@4.23.13`이 package와 npm lock에 기록되고 `npm ci` dry-run이 성공한다. | `package.json`, `package-lock.json`, npm dry-run | npm lock 동기화 결과를 유지한다. |
| 승인 범위 | 현재 작업이 미소유 변경을 수용하거나 stage하는가? | 아니오. `yarn.lock`은 별도 동시 변경으로 분리됐다. | branch scope와 `review-log.md` | 모든 stage/commit은 승인 pathspec을 명시하고 `yarn.lock`을 제외한다. |
| QA 제약 | 금지된 브라우저·캡처·실 backend QA를 수행했거나 수행했다고 추정하는가? | 아니오. 모두 미실행으로 기록했다. | 사용자 지시, review/evaluation log | 허용된 Node HTTP 테스트와 정적 검증만 근거로 사용한다. |

## 결론

- 승인된 citizen-votes pathspec에는 차단 결함이 없다.
- 실제 조회 계약, runtime 검증, query orchestration, read-only UI, observable MSW 동작과 Node 22 테스트 안정성이 직접 실행 근거로 연결된다.
- Watcher 최종 판정은 **PASS**이며 Evaluator의 권고는 모두 후속 비차단 과제다.
- `yarn.lock`, 브라우저·실 backend 검증, 전체 lint 기준선, npm vulnerability 정리는 현재 승인 범위 밖으로 남긴다.
