# Final Summary — ApiResult 정식 계약 승격 + useApi 통합 (중단 시점 기록)

- 세션: 2026-05-21
- 상태: **진행 중 중단**. PR-1, PR-2, PR-3 완료. PR-4 이후 미진행.

---

## 완료된 작업

### PR-1 — 기반 타입 정리 + api-client ApiResult 전환
- `ApiErrorData` → `unknown` 단순화
- `toApiError` 시그니처 정리 (사전 정규화된 ServerResponse 받음, 중복 정규화 제거)
- `unwrapServerResponse` `@deprecated` 마킹
- `api-client.ts` 반환 → `Promise<ApiResult<T>>`, CustomException 의존 제거
- 마이그레이션 어댑터 `legacy-unwrap.ts` 신설 (PR-3에서 삭제됨)
- tsc/lint PASS

### PR-2 — useApi execute 개선 + race 가드
- `execute` 오버로드 2종: 신규(`Promise<ApiResult<T> | { canceled: true }>`) + 레거시(`Promise<T | undefined>`)
- silent 기본값 `false → true` (opt-in 전환), dev `console.warn` 누락 감지
- `seqRef` race 가드 + `isMountedRef` unmount 가드
- `isLoading=false`는 마지막 seq에만 적용
- tsc/lint PASS

### PR-3 — 파일럿 (discussion + useDiscussDetailFetch)
- `discussion.api.ts` 11개 메서드 → `Promise<ApiResult<T>>` 정식 노출, 어댑터 호출 제거
- `useDiscussDetailFetch`: `useAsyncTask` 완전 제거, `Promise<boolean>` 반환으로 호출부 분기 단순화
- `useDiscussDetailModal`: try/catch → boolean 분기
- `legacy-unwrap.ts` 파일 삭제 + 배럴 export 제거 (사용처 0건 확인)
- `useFetchAdapter` 경유 2곳은 인라인 unwrap으로 임시 어댑팅
- Watcher 게이트 **PASS**
- tsc/lint PASS

---

## 미해결 이슈 (재개 시 우선 처리)

### [non-blocker, 버그성] pubsub 이벤트명 불일치
- 위치: `src/pages/dao/discuss-posts-management/detail/commend/hooks/useDiscussionCommentDelete.tsx`
- 발행 이벤트: `"refresh-dao-proposals-discussion-posts"` (subscriber 없음)
- 정합 이벤트: `"refresh-dao-proposals-discussion-posts-list"` (끝에 `-list`)
- 영향: 댓글 자체는 `onSuccess: refetch`로 정상 갱신되지만, 부모 게시글 목록 카운트/상태 갱신이 누락될 가능성
- 권고: PR-4 첫 커밋에 포함하거나 별도 hotfix

### [non-blocker, 스타일] execute 반환값 미사용 + 콜백 혼용
- 위치: 위와 동일 파일
- 현상: `await execute(...)` 반환값을 받지 않고 `onSuccess` 콜백으로 처리
- plan Section 2상 콜백은 하위 호환 부가물로 허용. 기능 문제 없음.
- 권고: PR-4 확대 시 반환값 기반 분기로 통일

---

## 미진행 PR (재개 시 plan 그대로 사용)

### PR-4~6 — DAO 도메인 확대 (3개 분할)
- 잔여 DAO 도메인: dao, events, users(DAO 관련), videos 등 — `src/apis/services/dao/**` 및 `src/apis/services/{events,users,videos}/**`
- 도메인 단위로 PR 끊어 진행
- `useFetchAdapter` 경유 호출부도 ApiResult 마이그레이션 동반 (PR-3에서 임시 인라인 unwrap으로 둔 2곳 정리 포함)

### PR-7 — users/videos/usage 구형 패턴 전환
- `any` 캐스팅 + 직접 instance 호출 구조 → `createApiClient` 적용 후 ApiResult 전환
- DTO 타입 정비 병행

### PR-8 — useAsyncTask 폐기 + silent 정리
- `src/hooks/use-async-task/useAsyncTask.ts` 삭제 (PR-3 시점에 유일 사용처 useDiscussDetailFetch에서는 제거됨, 다른 사용처 전수 확인 필요)
- silent 기본값 flip 영향 전수 검토 (85개 호출부) — `silent: false` 명시가 필요한 곳 식별 후 일괄 패치
- `useApi`에서 legacy throw 경로 + `isApiResultShape` 런타임 분기 제거 (모든 도메인 ApiResult 전환 완료 후)
- 최종 watcher → evaluator 게이트

---

## 상위 결정 (확정, 변경 시 재합의 필요)

1. **ApiResult discriminated union이 정식 계약** — 도메인 API는 `Promise<ApiResult<T>>` 반환, `throw`는 네트워크/취소 등 진짜 예외에만 사용.
2. **useAsyncTask 폐기, useApi로 단일화** — `execute`가 ApiResult 직접 반환.
3. **i18n 인터셉터 위치 유지** — 표현 계층 이전은 본 세션 범위 밖.

---

## 산출물 위치

- `plan.md` — 전체 계획
- `exploration.md` — 현재 상태 조사
- `implementation-log.md` — PR-1/PR-2/PR-3 변경 내역
- `review-log.md` — PR-3 watcher 게이트 결과
- `final-summary.md` — 본 문서

dependency:
- `.claude/logs/dependency/2026-05-21-api-result-contract.md`

---

## 재개 절차

1. `final-summary.md`의 "미해결 이슈" 우선 처리 (pubsub 이벤트명 수정)
2. `plan.md`의 PR-4 단위부터 순차 진행
3. 도메인 단위 PR 분할 원칙 유지 (한 번에 모두 변경 금지)
4. 각 PR 완료 후 watcher 게이트 → 통과해야 다음 PR 진행
5. PR-8 완료 후 evaluator 최종 게이트
