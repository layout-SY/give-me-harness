# 최종 요약

## 제공 사항

- `GET /citizen/votes/{voteId}/comments` 전용 typed API와 DTO
- page 1, size 20, `createdAt,desc` 기본 query와 반복 sort 지원
- `createdAt`·`id` 전용 sort vocabulary
- numeric ID와 `total/page/size`를 기존 댓글 화면 모델로 변환하는 parser
- vote 전용 TanStack Query 분기와 page·size·sort cache key
- 좋아요 필드가 없는 vote 댓글의 안전한 표시·cache 처리
- 상태 무관 조회, draft 404, 작성·신고를 포함한 MSW 계약
- API·parser·mock 회귀 테스트와 feature exports

## 제외 사항

- production UI 수정
- backend·인증 환경 검증
- 기존 meeting API 보안 테스트 실패 수정
- branch 생성, commit, merge, push

## 검증

| 명령어 | 결과 |
| --- | --- |
| 대상 Vitest | 5 files, 36 tests PASS |
| `npm run build` | PASS |
| `npm run lint` | PASS |
| `npm test` | 216 PASS, unrelated meeting tests 2 FAIL |
| Watcher | PASS |
| Axios+MSW API client 사용 | endpoint·기본 query·복수 sort·정규화·draft 404 확인 |

## 산출물

`plan.md`, `exploration.md`, `implementation-log.md`, `grill-me-review.md`, `review-log.md`, `evaluation-log.md`, `final-summary.md`, `portfolio-log.md`

## 남은 제한 사항

- TypeScript LSP와 no-excuse 전용 스크립트는 도구 미설치·런타임 제한으로 실행하지 못했다.
- `npm test` 전체 성공은 기존 meeting API 보안 테스트 2건 때문에 달성하지 못했다.
- 현재 작업은 브랜치 전략상 별도 작업 브랜치 없이 dirty `sy-main`에서 수행된 운영 편차가 있다.

## 다음 단계

- 이번 변경만 별도 승인된 브랜치·commit 단위로 정리하려면 선행 `AGENTS.md`, `package.json` 변경의 소유권과 worktree 사용 상태를 먼저 확정한다.

## 추가 완료 사항 — nullable 제안 작성자

### 제공 사항

- 실제 제안 목록의 `author: null`을 허용하는 Zod·DTO 계약
- 지원 상태 제안의 null-safe 작성자 표시 매핑
- mixed nullable parser와 presentation 회귀 테스트
- 원 dirty worktree를 보존한 `task/fix-proposal-list-null-author` linked worktree 구현

### 검증

- 대상 2 files, 18 tests PASS
- `npm run build` PASS
- `npm run lint` PASS
- 직접 module driver: 4건 parse, 3건 UI 상태 매핑
- Watcher PASS
- 전체 suite는 기존 meeting API 2건 실패, 211건 통과

### 제한 사항

- production UI의 query error와 정상 빈 결과 구분은 별도 작업이다.
- linked worktree 경로는 LSP 도구 cwd 밖이어서 `tsc -b`로 대체했다.
- no-excuse 스크립트는 TypeScript 7 `unstable/*` API 요구와 프로젝트 TypeScript 6.0.3의 불일치로 실행하지 못했다.
- commit·merge는 수행하지 않았고 별도 승인이 필요하다.
