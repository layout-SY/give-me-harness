# 탐색

## 요청

- 시민참여 제안 목록·상세가 mock fixture가 아니라 실제 backend 응답을 소비하도록 연결한다.
- `VITE_ENVIRONMENT` 값이 정확히 `dev`일 때만 mock API를 사용하고 `.env`에서는 해당 값을 주석 처리한다.
- 브라우저와 캡처 없이 테스트 코드로만 QA한다.

## 대상 관련 사실

- 기존 목록과 상세은 `src/entities/cp-proposal/api/cp-proposal.api.ts`의 `/v1/cp/proposals` resource 및 legacy DTO를 사용했다.
- 실제 목록 계약은 `page`, `size`, 반복 `status`, `author`, `title`, 반복 `sort` query와 `{ content, total, page, size }` pagination을 제공한다.
- 실제 상세 계약은 `id`, `title`, `content`, `expectedEffect`, `referenceCase`, `status`, `author`, `createdAt`, `updatedAt`을 제공한다.
- 실제 응답 envelope의 성공 코드는 문자열 `"SUCCESS"`이며 기존 공통 경계는 숫자 성공 코드 중심이었다.
- API 상태 `UNDER_REVIEW`, `REJECTED`는 UI 상태 `REVIEWING`, `RETURNED`와 vocabulary가 다르다.
- 목록 작성자는 `null`일 수 있지만 기존 표시 모델은 문자열 작성자명을 요구한다.
- 기존 `customConfig`는 `authRequired: true`를 통해 Axios Bearer token interceptor로 연결된다.
- 기존 목록 화면은 상태별 KPI를 기대했지만 새 목록 계약은 전체 `total`만 제공한다.
- `.env`는 Git ignore 대상이며 실제 API base URL은 `https://admin-api.synthoria.co.kr/`로 설정되어 있다.

## 불러온 스킬

- `policy-git-branch-strategy`
- `skill-index`, `policy-index`, `recipe-index`, `reference-index`
- `reference-components`, `reference-custom-hooks`
- `recipe-api-authoring`, `recipe-data-dto`, `recipe-data-fetch`
- `policy-coding-convention`, `policy-type-definition`, `policy-validation`
- `policy-data-fetch-layer`, `policy-tanstack-query`, `policy-abstraction-strategy`
- `policy-documentation`, `policy-review-checklist`, `policy-portfolio`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| 기존 시민제안 목록·상세 UI | 재사용 | 요청은 transport와 상태 조율 변경이며 production UI 변경이 필요하지 않다. |
| 신규 공용 UI | 생성하지 않음 | 새 마크업, 상호작용, 접근성 요구가 없다. |
| 기존 Table·검색 UI | 변경하지 않음 | 페이지 hook이 기존 표시 모델을 유지해 UI 계약을 보존한다. |

## 제약 조건 및 미확인 사항

- 실제 backend 인증 정보가 없어 live 요청 결과는 직접 확인하지 않았다.
- 사용자 지시에 따라 브라우저 bootstrap과 시각 QA를 실행하지 않았다.
- 처리 mutation의 신규 backend 계약은 제공되지 않아 legacy endpoint를 유지했다.
- `expectedEffect`, `referenceCase`, `updatedAt`은 모델에 보존하지만 이번 범위에서 production UI 렌더링을 추가하지 않았다.
- `typescript-language-server`가 설치되지 않아 LSP 진단을 사용할 수 없었다.

## 결론

- 기존 UI를 유지하면서 API DTO, Zod parser, query hook, 공통 envelope mapper, MSW 계약을 transport 경계에서 교체하는 것이 최소 변경이다.
- mock 활성화 판정을 순수 함수로 분리하면 브라우저 없이 정확한 `dev` gate를 검증할 수 있다.
- backend에 없는 상태별 집계를 임의 계산하지 않고 제공된 `total`만 표시한다.
