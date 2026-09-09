# 탐색

## 확인 결과

TS2379의 원인은 Zod로 추론된 GetDiscussionListQueryDto의 status·search·sort가 명시적 undefined를 허용하는 반면 ContentListQueryDto의 optional 속성은 exactOptionalPropertyTypes에 따라 undefined를 허용하지 않는다는 점이다. 기존 spread를 인접 useVoteListQuery와 같은 조건부 속성 구성으로 바꾸면 공통 DTO 수정 없이 해결할 수 있다.

## 요청과 조사 경로

사용자가 지정한 이전 handoff.md, plan.md, implementation-log.md를 읽고 실제 git status·log·worktree·V3 metadata와 비교했다. 현재 조회 훅, common/content.dto.ts, discussion.dto.ts, model/queryKeys.ts와 토론 API·참여 hook·controller·MSW 구현 및 테스트를 읽었다.

## 인접 구현과 재사용

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| useVoteListQuery | 속성 구성 패턴 재사용 | optional 값이 undefined이면 키에서 생략한다 |
| citizenParticipationKeys.list | 유지 | 목록 무효화 prefix와 모든 필터·페이지 의존성을 보존한다 |
| ContentListQueryDto | 유지 | 다른 콘텐츠까지 타입을 확대할 필요가 없다 |
| 기존 Vitest·ESLint·TypeScript 빌드 | 사용 | 새 검증 프레임워크가 필요하지 않다 |

새 공용 자산이나 의존성은 도입하지 않는다. source 수정은 조회 훅의 객체 구성 한 곳이다.

## 스킬 확인

중앙 snapshot의 task-role-routing·git-branch-strategy·Logic·handoff·pipeline 역할 문서, skill-index, coding-convention, type-definition, data-fetch-layer, implementation-quality, documentation, portfolio와 api-authoring 및 Codex 산출물 템플릿을 읽었다.

## 확인한 기존 실패

vote.api.ts는 `/citizen/votes/:id/ballots`를 요청한다. mocks/handlers.ts와 api/http/citizenParticipation.api.test.ts는 `/responses` handler를 사용한다. 현재 전체 테스트에서도 HTTP 1개·mock 참여 3개·완료 표시 1개의 투표 실패가 재현됐다. 토론 테스트는 모두 통과했다.

## 제약과 미확인 사항

빌드는 최초에 중앙 PreToolUse가 명령 실행 승인을 요구하며 차단했다. 사용자 독립 승인 후 동일 명령으로 TypeScript 검사와 번들 생성에 성공했다. 다른 명령으로 타입 검사를 우회하거나 승인 상태를 수정하지 않았다. 실제 서버 호환성과 시각 QA는 실행하지 않았다. sy-main의 예약 팝업 변경은 시민참여 경로와 겹치지 않지만 병합 이후 검증은 별도 완료 계약 승인 후 수행한다.
