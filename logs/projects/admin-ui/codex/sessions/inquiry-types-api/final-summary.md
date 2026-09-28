# 최종 요약

## 제공 사항

문의 타입 CRUD의 API·DTO·parser·TanStack Query hook 연결을 완료하고 `sy-main`에 병합했다. 기존 문의 답변 등록·수정·삭제와 상태 변경 구현을 재사용했다. 병합 후 문의 타입·문의·공통 응답·인증 테스트 56개와 lint·build가 통과했다.

## 작업 위치와 Git 상태

- 프로젝트: `asan-metaverse-admin-ui`
- 작업 브랜치: `feature/inquiry-types-api`
- 작업 위치: `/private/tmp/asan-metaverse-admin-ui-inquiry-types-api`
- 직접 부모: `sy-main`
- 분기 기준: `2b9ca35bd20fb9b071d18655e859576fc9a02e49`
- 현재 HEAD: `7db04d9624495406e5b3b93aca0a8d2a4c66b5f6`
- Git 생성 보호 작업: `2aa58089650a4757adbfd6ea65a48eb3` 완료.
- 커밋: `7db04d9 feat(inquiries): 문의 타입 CRUD API와 조회·변경 훅 추가`.
- 사용자 명령 실행 승인 후 보호 작업 `4ee103eb3140d9e312b9e371082a7deb`으로 소스·MSW·테스트 14개 파일을 stage·commit했다. 616줄 추가, 1줄 삭제.
- 커밋 직후 `git status --short --branch`에서 미커밋 변경이 없음을 확인했다.
- 사용자 명령 실행 승인 후 보호 작업 `6edba37162f04bcf982d4b056bab9059`으로 `feature/inquiry-types-api@7db04d9`를 `sy-main@ea64f72`에 merge 방식으로 통합했다.
- 병합 커밋: `e1743e229c659e893c93229205910125cec67918` (`merge: feature/inquiry-types-api 작업을 sy-main에 통합`). 두 부모는 `ea64f72f6ede900d34e9ba8f8d5a37ca8a5e08f0`, `7db04d9624495406e5b3b93aca0a8d2a4c66b5f6`이다.
- 병합 검증은 기본 checkout `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`에서 실행했다. 보호 작업은 검증 성공 후 `retained` 상태로 끝났다. 작업 branch·worktree는 유지했고 원격 push는 실행하지 않았다.
- 구현은 별도 worktree에서만 수행했다. 기본 checkout에서 확인된 `PR_sy-main-to-dev.md`는 이번 작업 산출물이 아니며 수정하지 않았다.

## 변경 이유와 내용

타입 CRUD는 기존 inquiries slice에 구현되어 있지 않았다. 사용자가 선택한 구조대로 별도 `inquiry-type` 모듈을 추가해 기존 문의 API와 함께 공개한다.

| 기능 | 요청 계약 | 공개 API |
| --- | --- | --- |
| 타입 목록 | GET `/admin/inquiries/types`, `page`, `size` | `inquiryTypeClient.getList`, `useInquiryTypeListQuery` |
| 타입 등록 | POST `/admin/inquiries/types`, `{ code, name }` | `inquiryTypeClient.postType`, `useCreateInquiryTypeMutation` |
| 타입 수정 | PUT `/admin/inquiries/types/{typeId}`, `{ name }` | `inquiryTypeClient.putType`, `useUpdateInquiryTypeMutation` |
| 타입 삭제 | DELETE `/admin/inquiries/types/{typeId}` | `inquiryTypeClient.deleteType`, `useDeleteInquiryTypeMutation` |

- 외부 공개 경계: `src/entities/inquiries/index.ts`.
- 요청 page·size는 명시적으로 전달하며, page는 1 기준이다. 서버가 지원하는 요청 0을 허용하고 응답 page 1을 보존한다.
- 타입 항목은 `id`, `code`, `name`을 검증한다. code는 서버 문자열로 처리하며 정적 enum으로 제한하지 않는다.
- 요청 schema가 허용 필드만 전송하며, 수정 요청에서 code·id 같은 추가 필드는 제외한다.
- 성공 응답은 문자열 data로 검증한다. 성공 시 타입 등록은 타입 목록만, 수정·삭제는 타입명에 의존하는 문의 목록·상세도 취소 후 무효화한다.
- HTTP·업무·파싱 실패는 오류로 전달하고 조회 캐시를 성공 처리하지 않는다. AbortSignal을 Axios까지 전달한다.
- 타입 MSW를 문의 상세 handler보다 먼저 등록해 `/types`가 `/:inquiryId`에 가로채이지 않게 했다.

## 재사용 자산

`ApiClient`, `ApiResult`, 인증 `customConfig`, `withAbortSignal`, `unwrapApiResult`, `PageResponseDto`, `createPageResponseSchema`, `parseInquiryMutationResponse`, 앱 QueryClient 오류 정책, 기존 문의 답변 API·hook·테스트.

## 검증

아래 구현 검증은 작업 worktree에서 실행했다.

| 명령 | 결과 |
| --- | --- |
| `npm ci --offline --ignore-scripts` | lockfile 기준 의존성 설치 성공, 패키지 파일 변경 없음 |
| 현재 bundle의 `python3 -I …/.agent-policy/runtime/formatting.py apply` | 수정한 소스·테스트 14개 파일 Prettier 포맷 성공 |
| `node --test tests/inquiry-types-contract.test.mjs tests/inquiry-types-query-mutation.test.mjs tests/inquiries-contract.test.mjs tests/inquiries-mutation.test.mjs tests/inquiries-msw.test.mjs tests/common-response-contract.test.mjs` | 51개 통과, 실패 0 |
| `npm run lint` | 통과 |
| `npm run build` | TypeScript·Vite 빌드 통과 |
| `git diff --check` | 통과 |

검증 내용은 실제 Axios의 경로·메서드·인증·body·query, 첫 페이지 0/1과 다음 페이지, 공통 응답·빈 목록, 캐시 무효화 범위와 활성 목록 재조회, 늦은 응답 취소, 업무 실패·HTTP 실패·네트워크 실패·잘못된 응답·취소를 포함한다. 기존 답변·상태 변경 테스트도 모두 통과했다.

### 병합 검토 및 사후 검증

- 최종 검토 `aabb3e4b11234e90a9dc88526bb31b45`: 부모의 공통 페이지 DTO·인증 기본값 변경, 형제 branch와 삭제 이력 및 미커밋 변경을 비교했다. 텍스트 충돌과 문의 계약을 막는 충돌은 발견하지 못했다.
- 부모 `ea64f72`에서 기존 아이템 테스트의 모순된 기대값을 확인했다. `node --test tests/items-query-mutation.test.mjs`는 11개 중 10개 통과, 1개 실패했다. 실패 지점은 `tests/items-query-mutation.test.mjs:252`이며 문의 병합 전부터 발생했다. 이 파일은 이번 병합에서 수정하지 않았다.
- 병합 후 `npm run lint`, `npm run build`: 보호 실행기 기록에서 각각 종료 코드 0을 확인했다.
- 병합 후 `node --test tests/inquiry-types-contract.test.mjs tests/inquiry-types-query-mutation.test.mjs tests/inquiries-contract.test.mjs tests/inquiries-mutation.test.mjs tests/inquiries-msw.test.mjs tests/common-response-contract.test.mjs tests/auth-api-contract.test.mjs`: 56개 통과, 실패 0.
- 다른 작업의 이벤트 UI branch와 `.env.template` 미커밋 변경은 이번 통합에 포함하지 않았다.

## 알려진 제한

- 검증은 MSW를 사용하는 로컬 계약 테스트다. 실서버 요청이나 화면 연결은 수행하지 않았다.
- 타입 MSW는 제공된 6개 타입과 문자열 성공 응답을 사용하는 고정 fixture다. 기본 handler의 mutation이 목록 내용을 영속적으로 바꾸지는 않는다. 변경 후 재조회 검증은 테스트별 handler에서 응답을 전환한다.
- 타입 삭제 제약·생성 ID·중복 code 정책은 서버에서 처리한다. 제공되지 않은 업무 규칙을 추가하지 않았다.
- 빌드에는 500 kB 초과 청크 경고와 `vite-tsconfig-paths`를 Vite 내장 설정으로 대체할 수 있다는 안내가 있다. 빌드는 성공했다.
- 별도 리뷰 에이전트는 호출하지 않았다.

## 사용 예와 다음 단계

```ts
const types = useInquiryTypeListQuery({ page: 1, size: 10 });
const createType = useCreateInquiryTypeMutation();
const updateType = useUpdateInquiryTypeMutation();
const deleteType = useDeleteInquiryTypeMutation();

createType.mutate({ payload: { code, name } });
updateType.mutate({ typeId, payload: { name } });
deleteType.mutate({ typeId });
```

향후 문의 화면에서는 `sy-main`에 통합된 공개 hook과 기존 답변 hook을 함께 사용할 수 있다.

## 산출물

`.codex/logs/sessions/inquiry-types-api/plan.md`, `exploration.md`, `final-summary.md`.
