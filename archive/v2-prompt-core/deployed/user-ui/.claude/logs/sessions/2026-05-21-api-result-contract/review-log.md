# Watcher Review Log — PR-3 파일럿 게이트

**날짜:** 2026-05-21
**검토 범위:** Section 4 파일럿 검증 게이트
**판정:** PASS (조건부: non-blocker 1건 PR-4 전 수정 권고)

---

## 항목별 판정

### 1. discriminated union 좁히기 정확성 — PASS

- `useDiscussDetailFetch.tsx`: `if ("canceled" in result) return false` → `if (!result.success) return false` → `result.data` 접근 순서 정확. 타입 안전.
- `ExecuteResult<T> = ApiResult<T> | { canceled: true }` 구조에서 `"canceled" in result` 가드가 올바른 discriminant 역할 수행 ✓
- `ApiResult` 성공/실패 분기 후 `result.data`/`result.error` 접근 모두 타입 안전 ✓
- 양쪽 접근 누락 케이스 없음 ✓

### 2. race 가드 동작 — PASS

- `useApi.tsx`: `seqRef` 기반 토큰 발행 구현 확인.
- `currentSeq === seqRef.current` 비교로 폐기된 호출 감지 ✓
- `useDiscussDetailFetch`와 `useDiscussionCommentDelete`는 각자 독립적인 `useApi` 인스턴스 사용 → seqRef 격리 ✓
- 취소 시 `{ canceled: true }` 반환 → 상태 변경 없이 early return ✓
- finally 블록에서 `currentSeq === seqRef.current` 조건으로 isLoading 해제 → 마지막 호출만 해제 ✓

### 3. isLoading 단일화 — PASS

- `useDiscussDetailFetch.tsx`: `useAsyncTask` import 제거, `useApi`의 `isLoading`만 외부 노출 ✓
- `const { api, execute, isLoading } = useApi()` 단일 레이어 ✓
- 이중 isLoading 레이어 없음 ✓

### 4. silent failure 없음 — PASS (단, 1건 주석 처리)

- `useDiscussDetailFetch.tsx`: 모든 execute 호출에 `silent: false` 명시 ✓
- `useDiscussionCommentDelete.tsx`: `silent: false` 명시 ✓
- `index.tsx` 인라인 unwrap: `if (!result.success) throw new CustomException(result.error)` → useFetchAdapter onError 콜백 경유 → isLoading 정리 ✓
- `proposalPostDetailCommentWidget.tsx` 인라인 unwrap: 동일 패턴 ✓

**주석 (non-blocker):** `useDiscussionCommentDelete.tsx`의 `execute` 반환값이 미할당(discard)됨. `onSuccess` 콜백 경유로 성공 처리하고, 취소/실패는 callback 미호출로 묵시적 처리. 기능상 silent failure 없음(silent:false 명시). 단, 반환값 기반 분기를 사용하지 않아 plan의 정식 흐름 패턴과 불일치. PR-4에서 일관성 확보 권고.

### 5. 외부 동작 동등성 — PASS

- 성공 시: `Dialog.alert` + `pubsub.publish` + 모달 닫기(useDiscussDetailModal에서 처리) + refetch 흐름 유지 ✓
- 실패 시: `silent: false` 명시로 오류 Dialog 자동 표시 ✓
- 삭제 confirm 흐름: `Dialog.confirm` → yes 분기 → 요청 → 결과 처리 ✓

### 6. legacy-unwrap.ts 제거 영향 — PASS

- `legacy-unwrap.ts` 파일 미존재 확인 ✓ (plan에서 삭제 대상으로 명시된 파일명이 실제로는 `server-response.unwrap.ts`이며 `@deprecated` 마킹 후 유지)
- `unwrapApiResult` 잔존 사용처 없음 (grep 결과 0건) ✓
- `api-result.ts` 배럴에서 `unwrapServerResponse`는 export 유지되나 외부 호출부 없음 ✓
- `unwrapServerResponse` 직접 호출: `api-client.ts` 외부 사용처 0건 ✓

### 7. 타입/린트 — PASS

- `yarn tsc --noEmit`: 오류 없음 (Done in 4.68s) ✓
- `yarn lint`: 오류 없음 (Done in 1.65s) ✓

### 8. useFetchAdapter 인라인 unwrap 패턴 — PASS (주석 포함)

- `index.tsx` 및 `proposalPostDetailCommentWidget.tsx` 모두 동일한 인라인 unwrap 패턴 적용 ✓
- `// NOTE: useFetchAdapter는 아직 throw 기반 계약을 사용한다 (PR-4 이후 ApiResult 전환 예정).` 마커 양쪽 파일에 일관적으로 표시 ✓
- 패턴: `const result = await api.dao.method(params); if (!result.success) throw new CustomException(result.error); return result.data;` ✓

---

## 발견된 이슈

### [NON-BLOCKER] useDiscussionCommentDelete — 데드 pubsub 이벤트

**파일:** `src/pages/dao/discuss-posts-management/detail/commend/hooks/useDiscussionCommentDelete.tsx`
**코드:** `pubsub.publish("refresh-dao-proposals-discussion-posts")`
**문제:** 해당 이벤트의 subscriber가 존재하지 않음. 댓글 삭제 후 부모 게시글 목록이 갱신되지 않을 수 있음.
**영향:** 댓글 목록 자체는 `onSuccess: refetch`로 정상 갱신됨. UX 영향은 부모 목록의 카운트/상태 갱신 누락 가능성.
**권고:** 의도가 목록 갱신이면 `"refresh-dao-proposals-discussion-posts-list"`로 수정. 불필요하면 publish 제거.
**심각도:** non-blocker (댓글 삭제 기능 자체는 정상 동작)

### [NON-BLOCKER] useDiscussionCommentDelete — execute 반환값 미사용 (패턴 불일치)

**파일:** `src/pages/dao/discuss-posts-management/detail/commend/hooks/useDiscussionCommentDelete.tsx`
**코드:** `await execute(...)` (반환값 미할당)
**문제:** plan 정식 흐름은 execute 반환값 기반 분기. 현재 onSuccess 콜백 혼용 패턴 사용.
**영향:** 기능상 문제 없음 (silent:false 명시, onSuccess 콜백 정상 동작). 단, PR-4 확대 시 패턴 불일치로 혼란 가능.
**권고:** PR-4 시 반환값 기반 분기로 통일.
**심각도:** non-blocker

---

## 판정 요약

```yaml
summary: PR-3 파일럿 검증 — discriminated union, race 가드, isLoading 단일화, silent failure 방지, 타입/린트 전 항목 통과. non-blocker 2건 발견.
decision: approved
review_result: 8개 게이트 항목 모두 PASS. 데드 pubsub 이벤트 1건과 execute 반환값 미사용 패턴 1건이 non-blocker로 식별됨.
pass_fail: pass
violations: []
required_fixes:
  - "[권고] useDiscussionCommentDelete.tsx의 pubsub 이벤트명 확인 및 수정 (PR-4 전)"
  - "[권고] execute 반환값 기반 분기 패턴으로 통일 (PR-4 시)"
repeat_issue_detected: false
escalation_needed: false
reasons:
  - discriminated union 좁히기 정확
  - race 가드 seqRef 격리 확인
  - isLoading 단일 레이어 확인
  - silent:false 전 호출부 명시
  - tsc/lint PASS
  - legacy-unwrap/unwrapApiResult 잔존 없음
  - 인라인 unwrap TODO 마커 일관 표시
artifacts:
  - review-log.md
next_action: PR-4 (DAO 도메인 확대) 진행 승인. PR-4 시작 전 useDiscussionCommentDelete pubsub 이벤트명 수정 권고.
status: approved
```
