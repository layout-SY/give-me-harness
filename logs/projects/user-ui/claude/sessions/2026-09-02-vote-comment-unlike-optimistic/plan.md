# 계획

## 목표

- 투표 댓글 목록 응답의 `likedByMe`를 UI `CommentItem.liked`로 전달한다.
- 이미 좋아요한 댓글을 누르면 기존 DELETE mutation이 선택되고 좋아요 상태와 수가 낙관적으로 감소하도록 복원한다.
- DELETE 404에서 이전 댓글 캐시가 복원되는 회귀 근거를 유지한다.

## 범위

- `src/pages/citizen-participation/model/presentation.ts`의 DTO-to-UI adapter
- 투표 댓글 API, hook, MSW fixture·handler 관련 테스트 계약
- `.codex/logs/sessions/2026-09-02-vote-comment-unlike-optimistic/` 필수 산출물

## 제외 사항

- production UI 마크업과 스타일 변경
- 기존 DELETE mutation·API 구현의 재작성
- 댓글 presentation 및 fixture 모듈 분할 리팩터링
- commit, merge, push, 원격 브랜치 작업

## 제약 조건

- API/cache 계약의 `likedByMe`와 UI 계약의 `liked`를 adapter 경계에서만 변환한다.
- 다른 세션의 변경을 되돌리거나 승인 scope 밖 파일을 수정하지 않는다.
- 화면 캡처·브라우저 자동화 없이 기존 Vitest 경로로 사용자 동작을 검증한다.

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 탐색·계획 | Planner | `policy-git-branch-strategy`, `policy-harness`, `reference-index` | 원인·scope·재사용 여부 확정 |
| 구현 | Generator | `programming`, `policy-coding-convention`, `policy-type-definition` | `likedByMe → liked` adapter 복원 |
| 검증 | Generator | `policy-validation`, `policy-data-fetch-layer` | 관련·전체 회귀 및 build 통과 |
| 검토 | Watcher | `policy-review-checklist` | 독립 PASS/FAIL 판정 |
| 장기 평가 | Evaluator | `policy-codex-native-quality`, `policy-abstraction-strategy` | 현재 범위와 분리된 후속 권고 |
| 문서화 | Generator | `policy-documentation`, `policy-portfolio` | 필수 8종 산출물 완성 |

## 검증

- 관련 Vitest 7 files, 51 tests
- `npm run test`
- `npm run lint`
- `npm run build`
- `git diff --check`
- 변경 파일 LOC 확인

## 위험 요소 및 결정 사항

- `likedByMe`와 `liked`의 명칭 드리프트가 다시 발생하면 UI가 POST를 선택할 수 있으므로 adapter와 회귀 테스트를 함께 정렬한다.
- 기존 mutation이 이미 DELETE, 낙관적 감소, 오류 rollback을 구현하므로 중복 구현하지 않는다.
- 대형 모듈 분할은 버그 수정 scope를 확대하므로 Evaluator 후속 권고로 남긴다.

## 승인

- 상태: approved
- 구현 승인: 명시적 `진행` 지시 확인
- 브랜치 승인: `task/vote-comment-unlike-optimistic`, 부모·직접 merge 대상 `sy-main`, 부모 HEAD `a32b462f3d6e`
- 필수 문구: `이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?`
