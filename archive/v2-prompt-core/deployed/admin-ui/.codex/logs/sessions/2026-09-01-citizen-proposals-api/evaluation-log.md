# 평가 로그

## 현재 판정과의 경계

여기서는 Watcher 판정을 다시 평가하지 않는다.

- Watcher가 현재 변경을 PASS로 판정했으며 Evaluator는 장기 아키텍처, 재사용 자산, 기술 부채, 프로세스 개선만 기록했다.
- Evaluator 세션: `ses_fa4193404ffeLgdqT5hcN2Ebm9`

## 장기 관찰 사항

1. **높음: 공통 응답 계층의 복수 envelope 지원**
   - `src/shared/api/common/api-result/**`가 숫자와 문자열 code를 함께 수용한다.
   - 두 번째 문자열-code API 계열이 연결되면 envelope별 adapter가 성공 조건을 소유하는 구조를 검토한다.
2. **중간: 시민제안 상태 변환 분산**
   - API→UI, UI→API 검색, mock 변환이 parser, 페이지 설정, handler에 분산되어 있다.
   - 다음 상태 변경 전 시민제안 도메인 로컬 status codec으로 통합한다.
3. **중간: 신규 GET과 legacy process 계약 공존**
   - `/citizen/proposals` GET과 `/v1/cp/proposals` mutation이 같은 도메인 API 모듈에 있다.
   - 다음 endpoint 이전 시 transport 계약을 파일 또는 명시적 접두어로 분리한다.
4. **높음: 기존 UI 모델을 위한 표시 기본값 합성**
   - API에 없는 `reviewComment`, `departmentLabel`, `histories` 등이 기본값으로 채워진다.
   - 다음 상세 기능 확장 전 citizen 조회 모델과 관리자 처리 모델의 의미 경계를 재검토한다.
5. **중간: 상태별 KPI와 신규 목록 계약의 차이**
   - backend가 `total`만 제공하므로 상태별 KPI 요구가 유지되면 별도 집계 계약이 필요하다.

## 목록에 등록할 재사용 가능 자산

- 등록 권고: `src/shared/api/common/api-result/**`의 숫자·문자열 envelope 정규화 경계
  - 제한: 모든 문자열이 아니라 현재 `"SUCCESS"`만 성공으로 해석한다.
- 등록 권고: `src/app/mock-api-policy.ts`의 mock API 런타임 정책
  - 제한: 정확한 `dev` marker와 `/v1/cp/`, `/citizen/` 감시 범위를 함께 문서화한다.
- 지금 등록하지 않음: 시민제안 상태 mapping
  - 도메인 로컬 codec으로 통합된 뒤 재사용 자산으로 등록한다.
- 지금 등록하지 않음: citizen mock response factory
  - 단일 handler 사용이므로 두 번째 소비자가 생기기 전에는 공용화하지 않는다.
- 실제 `.codex/memory/reusable-assets.md` 수정은 중앙 정책과 승인 범위 밖이므로 이번 브랜치에서 수행하지 않았다.

## 기술 부채

- `src/mocks/cp-proposal.handlers.ts`가 envelope, 상태 변환, 정렬, 필터, pagination, legacy mutation을 함께 소유한다. 다음 citizen endpoint 추가 시 transport fixture mapper와 in-memory 동작 분리를 검토한다.
- `VITE_ENVIRONMENT=dev` mock 실행 방법이 README나 `.env.example`에 없다. 후속 문서 작업에서 실제 API 모드와 mock 모드의 환경값을 기록한다.
- Vite SSR 테스트 bootstrap이 여러 `tests/*.test.mjs`에 반복된다. 동일 생명주기가 이미 다수 확인되므로 테스트 helper 추출 후보이다.

## 프로세스 개선 사항

- backend 계약 변경 체크리스트에 endpoint, query 직렬화, envelope, vocabulary mapper, nullable 필드, pagination, AbortSignal, MSW 오류, mock 환경을 포함한다.
- backend 대표 success/error payload를 transport fixture로 관리하고 parser 테스트와 MSW 계약 검증에서 공유한다.
- 도메인 API 이전표에 목록·상세 GET은 `/citizen`, process mutation은 `/v1/cp`라는 혼합 상태를 endpoint별로 기록한다.

## 권고 사항

1. 다음 작업 전 공통 envelope와 mock 런타임 정책의 지원 범위를 재사용 자산 목록에 등록한다.
2. 다음 상태 변경 전 시민제안 도메인 로컬 status codec을 도입한다.
3. 다음 상세 또는 처리 API 연결 전 조회 모델과 관리자 처리 모델의 의미 경계를 분리한다.
4. 두 번째 문자열-code 도메인이 생기면 envelope adapter와 mock response factory의 공용화를 재평가한다.
5. 별도 유지보수 범위에서 mock 환경 문서와 Vite SSR 테스트 helper를 추가한다.
