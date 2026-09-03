# implementation-log.md

## Stage
- Date: 2026-04-21
- Scope: 공용 API 에러 처리 — axios 필드 매핑 수정 + i18n 에러코드 등록
- Status: completed

---

## 근본 원인

백엔드 응답 구조와 axios 인터셉터 필드 매핑 불일치.

| 필드 | 백엔드 실제 | 기존 코드가 읽던 값 | 결과 |
|------|-----------|-----------------|------|
| 에러 코드 문자열 | `data.msg` | `data.message` | 항상 `""` → 빈 alert |
| 숫자 결과코드 | `data.result` | `data.code` | `undefined` |

---

## 변경 내역

### 1. `src/apis/axios-instance.ts`

```ts
// before
code: data.code,
message: data.message ?? "",

// after
code: data.result ?? data.code,
message: data.msg ?? data.message ?? "",
```

- `data.result ?? data.code`: 신규 필드 우선, 기존 필드 fallback (하위호환 유지)
- `data.msg ?? data.message ?? ""`: 동일 방식

### 2. `src/hooks/use-api.tsx`

- `useLanguage` 훅 추가
- `CustomException` catch 시 i18n 룩업:
  ```ts
  const translated = (mui as Record<string, string>)[`_api_err_${err.message}`];
  Dialog.alert({ content: <p>{translated ?? err.message}</p> });
  ```
- 알 수 없는 에러코드 → raw 메시지 fallback

### 3. `src/assets/i18n/ko.json`, `ja.json`

- 키 네이밍 규칙: `_api_err_{BACKEND_ERROR_CODE}`
- 추가된 에러코드 35개:

| 에러코드 | 한국어 |
|---------|-------|
| PROPOSAL_REGIST_DATE_ERROR | 투표 기한 범위가 올바르지 않습니다. |
| PROPOSAL_CREATE_NO_PERMISSION | 제안을 등록할 권한이 없습니다. |
| PROPOSAL_UPLOAD_FAIL | 제안 등록에 실패했습니다. |
| USER_NOT_FOUND | 사용자를 찾을 수 없습니다. |
| PROPOSALS_LIST_LOAD_FAIL | 제안 목록을 불러오는데 실패했습니다. |
| PROPOSAL_NOT_AUTHOR | 제안 작성자가 아닙니다. |
| INVALID_IMAGE_ID | 해당 제안의 이미지가 아닙니다. |
| INVALID_IMAGE_PAYLOAD | 이미지 주소가 없습니다. |
| PROPOSAL_IMAGE_UPLOAD_FAIL | 이미지 업로드에 실패했습니다. |
| INVALID_IMAGE_FILE_NAME | 파일명이 올바르지 않습니다. |
| INVALID_IMAGE_FILE | 이미지 파일이 올바르지 않습니다. |
| PROPOSAL_NOT_FOUND | 제안을 찾을 수 없습니다. |
| PROPOSAL_DELETE_NOT_ALLOWED | 제안 삭제가 허용되지 않습니다. |
| PROPOSAL_DELETE_TARGET_NOT_FOUND | 삭제할 제안을 찾을 수 없습니다. |
| PROPOSAL_DELETE_FAIL | 제안 삭제에 실패했습니다. |
| REVIEWS_LIST_LOAD_FAIL | 심사 목록을 불러오는데 실패했습니다. |
| PROPOSAL_LOAD_FAIL | 제안을 불러오는데 실패했습니다. |
| PROPOSAL_VOTE_FAIL | 투표에 실패했습니다. |
| DISCUSSION_POSTS_LIST_LOAD_FAIL | 토론 게시글 목록을 불러오는데 실패했습니다. |
| DISCUSSION_POST_NOT_FOUND | 토론 게시글을 찾을 수 없습니다. |
| DISCUSSION_POST_DELETE_FAIL | 토론 게시글 삭제에 실패했습니다. |
| REVIEW_NOT_REGISTERED_YET | 아직 심사가 등록되지 않았습니다. |
| PROPOSAL_REVIEW_NOT_APPROVED | 제안 심사가 승인되지 않았습니다. |
| DISCUSSION_POSTS_UPLOAD_FAIL | 토론 게시글 등록에 실패했습니다. |
| POST_LOAD_FAIL | 게시글을 불러오는데 실패했습니다. |
| DISCUSSION_COMMENT_NOT_FOUND | 댓글을 찾을 수 없습니다. |
| INVALID_PARENT_COMMENT | 유효하지 않은 상위 댓글입니다. |
| DISCUSSION_COMMENTS_UPLOAD_FAIL | 댓글 등록에 실패했습니다. |
| DISCUSSION_COMMENTS_LIST_LOAD_FAIL | 댓글 목록을 불러오는데 실패했습니다. |
| DISCUSSION_COMMENT_DELETE_FAIL | 댓글 삭제에 실패했습니다. |
| UPLOAD_PROPOSAL_REVIEW_FAIL | 제안 심사 등록에 실패했습니다. |
| CLOSE_VOTE_FAIL | 투표 마감에 실패했습니다. |
| INVALID_SORT_VALIDATION | 정렬 값이 올바르지 않습니다. |
| RANGE_DATE_ERROR | 시작일 또는 종료일을 올바르게 입력해주세요. |

---

## 동작 흐름 (수정 후)

```
백엔드 400 응답 {"result":0,"msg":"PROPOSAL_NOT_FOUND","data":{}}
  → axios interceptor
    → CustomException { code: 0, message: "PROPOSAL_NOT_FOUND" }
  → useApi execute catch
    → mui["_api_err_PROPOSAL_NOT_FOUND"] = "제안을 찾을 수 없습니다."
    → Dialog.alert("제안을 찾을 수 없습니다.")

미등록 에러코드 "UNKNOWN_ERROR" → fallback → Dialog.alert("UNKNOWN_ERROR")
```

---

## 잔여 리스크

- `axios-instance.ts`의 400 외 상태코드(401, 403, 500 등)는 여전히 `console.error`만 처리
- `useApi.execute`의 `useCallback` deps 배열이 비어 있어 `mui` 최신값 보장 안 됨
  - 현재는 언어 전환이 없는 경우 문제 없지만, 런타임 언어 전환 시 stale closure 발생 가능
