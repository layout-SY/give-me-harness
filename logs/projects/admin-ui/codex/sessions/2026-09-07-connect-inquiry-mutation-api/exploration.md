# 탐색

## 요청

실제 문의 mutation API 5개를 기존 조회 기반에 연결하고 UI 인계 문서를 작성한다.

## 조사 대상 경로

`src/entities/inquiries`, `src/shared/api`, `src/entities/cp-proposal/hook`, `src/entities/cp-notice/hook`, `src/app/providers/query-client.ts`, `src/mocks`, `tests/inquiries-*.test.mjs`, `src/shared/ui/no-results`와 공용 Table을 확인했다.

## 현재 코드와 인접 구현의 사실

- 조회 API는 `/admin/inquiries`이고 ApiClient·Zod parser·TanStack Query를 사용한다.
- 기존 답변 등록만 `/v1/inquiries/{id}/answer`의 multipart API이며 저장소 내 UI 사용처가 없다. 나머지 mutation 4개는 없다.
- 공용 ApiClient에 PUT이 없다. 기존 get/post/patch/delete와 동일한 envelope 처리가 필요하다.
- DTO 상태는 `OPEN/IN_PROGRESS/COMPLETED`, 오래된 enum에는 `RESOLVED/CLOSED`가 남아 있어 어휘 통일이 필요하다.
- 조회 MSW만 있고 공통 handler 배열에 등록되어 있지 않다. 미답변 mock의 `id: 0` 답변 객체는 사용자가 확인한 null 계약으로 바꾼다.
- 공용 QueryClient는 mutation 실패를 중앙 오류 reporter로 전달하고 mutation을 자동 재시도하지 않는다.
- 기존 `NoResults`는 `src/shared/ui/no-results/no-results.tsx`의 default export이며 기본 문구는 `내역이 없습니다.`다.

## 불러온 스킬

중앙 snapshot의 skill-index, policy-index, task-role-routing과 logic/handoff/pipeline 계약, git-branch-strategy, documentation, coding-convention, implementation-quality, type-definition, data-fetch-layer, validation, abstraction-strategy, recipe/api-authoring, recipe/data-dto, reference/custom-hooks를 읽었다. Codex 문서 템플릿을 확인했다. 라우팅 문서가 참조하는 `references/workflows.md`는 snapshot에 없어 제공된 공통 단계·역할 계약을 따른다.

## 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| ApiClient, ApiResult, unwrapApiResult | 재사용 | 인증·envelope·오류 처리 경계 일치 |
| inquiryKeys, 조회 hook | 확장 | 같은 문의 목록과 상세 캐시를 소유 |
| TanStack Query mutation | 재사용 | 인접 도메인에 동일한 서버 상태 소유 패턴 존재 |
| NoResults | UI 인계 | 사용자 지시와 기존 빈 결과 표시가 일치 |
| 기존 Node test, tsx, Vite, MSW | 재사용 | 새 테스트 프레임워크 없이 요청과 상태 검증 가능 |

## 재사용하지 않은 후보와 이유

useApi와 useFetchAdapter는 이 변경의 서버 캐시 소유자와 다르므로 신규 mutation을 감싸지 않는다. multipart 답변 transport는 새로운 JSON 계약과 일치하지 않는다.

## 새 자산 필요 여부와 근거

문의 전용 mutation hook 및 캐시 동기화가 필요하다. 같은 목록·상세 캐시를 갱신하는 네 작업의 후처리는 문의 도메인 내부에서만 재사용한다. 서로 다른 도메인의 CRUD를 공용화하지 않는다.

## 성능·의존성 영향

mutation 성공 시 문의 목록과 대상 상세만 갱신한다. 새 패키지를 추가하지 않는다.

## 제약 조건 및 미확인 사항

실제 서버 연결 검증은 요청되지 않았다. 제공되지 않은 상태 자동 전이와 서버의 업무 오류 코드는 mock의 검증용 동작과 구분하여 인계한다.

## 결론

현재 clean sy-main에서 승인된 Logic branch를 생성했다. 문의 API·mock과 공용 PUT을 수정하고 UI에는 공개 hook과 null 답변 표시 계약을 인계한다.
