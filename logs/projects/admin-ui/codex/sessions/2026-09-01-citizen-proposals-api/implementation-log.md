# 구현 로그

## 승인된 범위

- 브랜치: `task/connect-citizen-proposals-api`
- 부모 및 직접 merge 대상: `sy-main@202fdad6e1a0c8c528ade743a5cb79af9294dc46`
- 승인 경로: `.env`, `src/app`, `src/shared/api/common/api-result`, `src/entities/cp-proposal`, `src/pages/cp-proposal/hook`, `src/pages/cp-proposal/model`, `src/mocks/cp-proposal.handlers.ts`, `tests`, 현재 세션 산출물 디렉터리

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `src/shared/api/common/api-result/**` | `number | string` code를 정규화하고 `"SUCCESS"`를 성공으로 판정하며 문자열 오류를 `apiCode`에 보존 | 기존 숫자 오류 계약을 유지하면서 신규 envelope 수용 |
| `src/entities/cp-proposal/api/**` | 실제 목록·상세 Zod schema, query parser, GET endpoint, 반복 배열 직렬화, API→UI parser 구현 | typed backend 응답이 기존 표시 모델로 변환됨 |
| `src/entities/cp-proposal/model/**` | 상세 모델에 `expectedEffect`, `referenceCase`, `updatedAt` 추가 | 상세 backend 필드 보존 |
| `src/entities/cp-proposal/hook/**` | 상세 ID를 양의 정수로 검증하고 legacy process 응답 parser를 분리 | 잘못된 상세 경로 차단 및 기존 mutation 유지 |
| `src/pages/cp-proposal/**` | `size: 20`, 기본 sort, 반복 status query, 신규 pagination과 total KPI 사용 | 목록 조회 계약과 화면 상태 일치 |
| `src/mocks/cp-proposal.handlers.ts` | `/citizen/proposals` 목록·상세, query 검증, pagination, 400·404 문자열 envelope 구현 | MSW가 실제 공개 계약을 모사 |
| `src/app/index.tsx`, `src/app/mock-api-policy.ts` | 정확한 `dev` marker에서만 MSW 시작, CP·citizen 미처리 요청 감시 | 기본 실행은 실제 API, dev에서만 mock |
| `.env` | `VITE_ENVIRONMENT=dev`를 로컬 주석 상태로 설정 | mock 비활성 기본값 유지, Git ignore 대상 |
| `tests/*.test.mjs` | envelope, query, parser, API 경로, MSW HTTP, mock gate 회귀 테스트 추가·조정 | 브라우저 없는 계약 검증 확보 |

## 결정 사항

- API 상태는 `UNDER_REVIEW → REVIEWING`, `REJECTED → RETURNED`으로 transport 경계에서 변환한다.
- `author: null`은 기존 UI 계약을 위해 `탈퇴한 회원`으로 표시한다.
- Axios 배열 직렬화는 `indexes: null`로 설정해 `status=A&status=B` 형태를 만든다.
- 상태별 집계가 없으므로 KPI를 추정하지 않고 `total` 하나만 사용한다.
- 신규 계약이 없는 process mutation은 `/v1/cp/proposals/{proposalId}/process`에 유지한다.
- 문자열 오류 코드를 기존 숫자 `ApiError.code`에 강제로 넣지 않고 `ApiError.apiCode`에 보존한다.
- `expectedEffect`, `referenceCase`, `updatedAt`은 모델에 보존하되 UI 소유권과 요청 범위를 지켜 렌더링을 추가하지 않는다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `node --test tests/*.test.mjs` | PASS, 34 tests |
| `npm run build` | PASS, TypeScript project build 및 Vite production build 완료 |
| 변경 23개 파일 대상 `npx eslint ...` | PASS, 출력 없음 |
| `GIT_MASTER=1 git diff --check` | PASS |
| `npm run lint` | FAIL, 현재 변경 밖 기존 73 errors와 5 warnings; Watcher가 변경 파일 lint 통과를 별도 확인 |
| `lsp_diagnostics` | 실행 불가, `typescript-language-server` 미설치 |
| no-excuse 검사 | 실행 불가, `bun` 부재와 Node type stripping 제한; `git diff --check`와 LOC 검사로 대체 |

## Watcher 인계

- 검토 대상은 추적 변경 19개와 신규 파일 4개다.
- 사용자 제약상 브라우저, 스크린샷, 시각 QA를 수행하지 않는다.
- 실제 backend live 호출은 수행하지 않았으며 계약·MSW HTTP·build 결과를 근거로 검토한다.
- 저장소 전체 lint 실패는 승인 범위 밖 기존 오류와 현재 변경 오류를 분리해야 한다.
- Watcher 세션 `ses_fa4193626ffeQL0v0onPrmrBMM`이 현재 변경을 PASS로 판정했다.
