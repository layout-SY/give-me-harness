# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| endpoint | 목록과 상세 요청은 어떤 resource로 전송되는가? | `/citizen/proposals`, `/citizen/proposals/{proposalId}`로 전송된다. | `src/entities/cp-proposal/api/cp-proposal.api.ts` | 제공된 실제 backend resource를 사용한다. |
| 인증 | 요청 인증은 어떤 경계를 통해 적용되는가? | 기존 `customConfig.authRequired: true`가 Axios interceptor의 Bearer token 처리로 연결된다. | `src/entities/cp-proposal/api/cp-proposal.api.ts`, `src/shared/api/axios` | 기존 인증 경계를 재사용한다. |
| query | 배열 query와 기본 pagination/sort는 backend 계약과 일치하는가? | `size: 20`, `createdAt,desc`, 반복 status key를 사용한다. | `cp-proposal.dto.ts`, `cp-proposal.api.ts`, `cp-proposal-list.config.ts` | 배열 index 없이 반복 key로 직렬화한다. |
| envelope | 문자열 성공·오류 코드는 기존 숫자 계약을 깨지 않고 처리되는가? | `"SUCCESS"`는 성공, 문자열 오류는 `ApiError.apiCode`에 보존된다. | `server-response.ts`, `api-error.mapper.ts`, 계약 테스트 | 숫자 `code`와 문자열 `apiCode`의 의미를 분리한다. |
| 상태 | API와 UI의 상태 vocabulary는 어디에서 변환되는가? | entity parser와 페이지 검색 mapper에서 명시 변환된다. | `cp-proposal.parser.ts`, `cp-proposal-list.config.ts` | transport와 UI 상태를 암묵적으로 혼용하지 않는다. |
| nullable author | 탈퇴한 작성자의 목록 행은 어떻게 표시되는가? | `null`을 `탈퇴한 회원`으로 변환한다. | `cp-proposal.parser.ts`, 계약 테스트 | 기존 문자열 UI 계약을 유지하며 null 의미를 드러낸다. |
| pagination | backend가 제공하지 않는 집계값을 합성하는가? | 합성하지 않고 `total`, `page`, `size`와 계산 가능한 `pageCount`만 사용한다. | `cp-proposal.parser.ts`, `use-cp-proposal-list-data.tsx` | 상태별 KPI는 backend 계약 전까지 만들지 않는다. |
| 상세 | 상세 ID와 상세 필드는 경계에서 검증되는가? | 양의 정수 ID와 상세 Zod schema를 사용한다. | `use-cp-proposal-detail-query.ts`, `cp-proposal.dto.ts` | 경로 입력과 외부 응답을 각각 parse한다. |
| mock | mock은 어떤 환경에서 시작되는가? | `VITE_ENVIRONMENT`가 정확히 `dev`일 때만 시작된다. | `mock-api-policy.ts`, `mock-api-policy.test.mjs` | 유사 값이나 기본 development mode를 자동 허용하지 않는다. |
| legacy mutation | 목록·상세와 함께 process endpoint도 이전해야 하는가? | 신규 mutation 계약이 없어 기존 endpoint를 유지했다. | `cp-proposal.api.ts`, 사용자 제공 계약 | 확인되지 않은 endpoint를 추정하지 않는다. |
| 검증 | 실제 사용 표면은 무엇으로 확인했는가? | Node의 MSW HTTP 요청, parser/API 계약 테스트, production build로 확인했다. | `node --test tests/*.test.mjs`, `npm run build` | 사용자 제약에 따라 브라우저 없이 테스트 표면을 사용한다. |
| lint | 저장소 전체 lint 실패가 현재 변경의 결함인가? | 현재 변경 23개 파일은 통과했고, 전역 73 errors는 변경 밖 기존 경로다. | 변경 파일 ESLint, Watcher의 `npm run lint` | 현재 회귀와 baseline 부채를 분리해 기록한다. |

## 결론

- 제공된 endpoint, 인증, query, envelope, 상태, nullable author, pagination, 상세, 404, mock gate 요구를 근거별로 충족한다.
- 조치가 필요한 현재 변경 결함은 발견되지 않았다.
- 실제 backend live 호출과 브라우저 bootstrap은 사용자 제약 및 인증 정보 부재로 확인하지 않았다는 잔여 위험을 유지한다.
