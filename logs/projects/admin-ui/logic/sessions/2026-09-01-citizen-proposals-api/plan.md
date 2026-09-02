# 계획

## 목표

- 시민참여 제안 목록과 상세를 실제 `GET /citizen/proposals`, `GET /citizen/proposals/{proposalId}` 계약에 연결한다.
- 숫자 코드와 문자열 코드 응답 envelope를 기존 `ApiResult` 경계에서 안전하게 정규화한다.
- `VITE_ENVIRONMENT=dev`일 때만 MSW를 시작하고 기본 실행은 실제 backend를 사용한다.

## 범위

- `.env`
- `src/app`
- `src/shared/api/common/api-result`
- `src/entities/cp-proposal`
- `src/pages/cp-proposal/hook`
- `src/pages/cp-proposal/model`
- `src/mocks/cp-proposal.handlers.ts`
- `tests`
- `.codex/logs/sessions/2026-09-01-citizen-proposals-api`

## 제외 사항

- production UI 마크업과 스타일 변경
- 계약이 제공되지 않은 `/v1/cp/proposals/{proposalId}/process` mutation 이전
- backend가 제공하지 않는 상태별 KPI 임의 합성
- 브라우저 실행, 스크린샷, GIF, 시각 QA
- push와 원격 브랜치 작업

## 제약 조건

- 사용자 요구에 따라 QA는 테스트 코드로만 수행하고 실제 브라우저나 캡처를 사용하지 않는다.
- `.env`의 `VITE_ENVIRONMENT=dev`는 주석 상태로 두어 실제 backend 연결을 기본값으로 유지한다.
- API와 UI의 상태 vocabulary가 다르므로 transport 경계에서 명시적으로 변환한다.
- 현재 backend 계약의 nullable `author`와 문자열 `code`를 타입과 parser에서 처리한다.
- 전역 lint의 기존 오류를 승인 범위 밖에서 수정하지 않는다.

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 브랜치 격리 | Hephaestus | `policy-git-branch-strategy` | 승인된 `task/connect-citizen-proposals-api`에서만 변경 |
| 재사용 탐색 | Hephaestus, Explore | `skill-index`, `reference-index`, `reference-components`, `reference-custom-hooks` | 기존 entity/query/API 경계 재사용 |
| API 계약 | Hephaestus | `recipe-api-authoring`, `recipe-data-dto`, `recipe-data-fetch`, `policy-data-fetch-layer`, `policy-type-definition` | typed GET, DTO/parser, query 연결 |
| mock 및 검증 | Hephaestus | `policy-validation`, `policy-coding-convention`, `policy-tanstack-query` | 실제 계약과 동일한 MSW 및 Node 테스트 |
| 독립 판정 | Watcher | `policy-review-checklist` | 현재 변경의 PASS/FAIL 판정 |
| 장기 평가 | Evaluator | `policy-abstraction-strategy`, `policy-portfolio` | 현재 판정과 분리된 후속 개선점 |

## 검증

- `node --test tests/*.test.mjs`
- `npm run build`
- 변경 파일 대상 `npx eslint ...`
- `npm run lint`로 저장소 전체 기존 실패 분리
- `GIT_MASTER=1 git diff --check`
- Watcher의 파일별 계약 검토

## 위험 요소 및 결정 사항

- 공통 `ServerResponse` 확장은 모든 `ApiClient` 소비자에 영향을 줄 수 있어 기존 숫자 오류 코드는 유지하고 문자열 오류만 `ApiError.apiCode`에 보존한다.
- 목록 API에는 상태별 집계가 없으므로 KPI는 `total` 하나만 사용한다.
- 기존 상세 UI 모델에 필요한 일부 필드는 API에 없으므로 현재 표시 호환 기본값을 채우되, 실제 backend 데이터처럼 새 의미를 만들지 않는다.
- 실제 인증 backend 호출은 사용자 QA 제약과 인증 정보 부재로 수행하지 않고 계약 테스트, MSW HTTP 테스트, production build로 검증한다.

## 승인

- 구현 승인: 사용자의 `작업 진행`
- 브랜치 생성 승인: `task/connect-citizen-proposals-api`, 부모 및 직접 merge 대상 `sy-main@202fdad6e1a0c8c528ade743a5cb79af9294dc46`
- 상태: approved and implemented
- 필수 문구: `이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?`
