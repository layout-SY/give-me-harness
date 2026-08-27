# 최종 요약

제안 상세 GET은 `{ id, title, background, content, expectedEffect, referenceCase, status, author, createdAt, updatedAt }`를 읽고, 탈퇴 작성자는 `author: null`이다. 시민참여 API 접두사는 `/citizen`이다. `/v1/api`는 쓰지 않는다.

## 제공 사항

- `GetProposalDetailResponseDto` / `parseProposalDetail` / `useProposalDetailQuery`
- `/citizen/proposals`, `/citizen/votes` 등 전송 경로

## 제외 사항

- 토론·정책·설문 상세 재계약
- 제안 목록 author null

## 검증

| 명령어 | 결과 |
| --- | --- |
| `tsc -b` | 성공 |
| eslint 변경 파일 | 성공 |
| vitest handlers+api+presentation | 33 passed |

## 산출물

`.codex/logs/sessions/2026-08-26-proposal-detail-api-contract/` 8종

## 남은 제한 사항

화면 `reviewResult`는 API에 없어 status 라벨로 표시한다.

## 다음 단계

없음
