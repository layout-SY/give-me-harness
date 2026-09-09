# 계획

## 목표

- 백엔드가 `isMine`을 아직 내려주지 않는 동안 vote comment 목록 Zod 계약이 파싱 실패하지 않게 한다.
- 댓글 목록이 화면에 다시 렌더링되도록 하고, 소유권 필드는 백엔드 추가 전까지 없어도 된다.

## 범위

- `voteCommentSchema`의 `isMine`을 optional로 완화한다.
- `isMine`이 없는 목록 응답을 성공으로 고정하는 회귀 테스트를 수정한다.
- 세션 8종 산출물을 `.codex/logs/sessions/2026-09-04-vote-comment-ismine-optional/`에 작성한다.

## 제외 사항

- `src/shared/api/error/api-failure-diagnostics.ts`의 `<field>` 마스킹 수정
- `comment.dto.ts`의 `isMine` 변경. 이미 optional이다.
- production UI, hook, parser, MSW fixture 수정
- 사용자 승인 전 commit, merge, 브랜치 삭제

## 제약 조건

- 백엔드는 `isMine`을 곧 필수로 둘 예정이지만 지금은 필드 추가가 보류다.
- `useCitizenCommentActions`는 `isMine === true`만 내 댓글로 본다. 필드가 없으면 수정/삭제는 열리지 않는다.
- 이미지 캡처, 브라우저 자동화, 시각 QA는 실행하지 않는다.

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 계보·범위 확인 | Planner | `policy-git-branch-strategy` | `sy-main`에서 `task/vote-comment-ismine-optional` 생성 |
| 계약 탐색 | Planner | `recipe-api-authoring`, `recipe-data-dto`, `policy-data-fetch-layer` | 필수 `isMine`이 실제 응답과 어긋남을 확인 |
| 스키마·테스트 | Generator | `policy-coding-convention`, `policy-type-definition` | optional 계약과 회귀 테스트 |
| 독립 판정 | Watcher | `policy-review-checklist` | 승인 범위 PASS/FAIL |
| 장기 평가 | Evaluator | `policy-portfolio`, `policy-documentation` | 백엔드 필드 복원 시점을 부채로 기록 |

## 검증

- `npx vitest run src/features/citizen-participation/api/http/voteComments.api.test.ts`
- `npm run build`
- `npm run lint`
- `python3 -I .codex/hooks/test_governance_hooks.py`
- `git diff --check`

## 위험 요소 및 결정 사항

- `isMine`을 `default(false)`로 두면 타입이 항상 boolean이 되지만, 서버가 아직 소유권을 모른다는 사실과 `false`가 섞인다. 사용자는 optional을 요청했다.
- 스키마만 완화하면 parser와 hook은 추가 수정 없이 목록을 통과한다.
- 전체 `npm run test`의 투표 제출·결과 라우트 실패는 이번 변경 경로 밖이다.

## 승인

- 상태: approved
- 구현 승인: 사용자가 `isMine`을 optional로 두고 연관 코드를 수정하라고 지시했고, 이어서 `작업 진행`으로 승인했다.
- 브랜치 승인: `task/vote-comment-ismine-optional`을 `sy-main@167852a74a7ecaab25b230b4236b71ed2115e6b3`에서 생성하고 직접 merge 대상으로 `sy-main`을 사용한다.
- 필수 문구: `이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?`
