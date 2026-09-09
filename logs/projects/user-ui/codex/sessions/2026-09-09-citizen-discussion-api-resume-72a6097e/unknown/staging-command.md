# 스테이징 명령 — 실행 완료

작업 위치: `/Users/okand/SynologyDrive/asan-metaverse-user-ui-worktrees/citizen-discussion-api-resume`

목적: 검증된 시민참여 소스와 테스트 22개 파일만 Git index에 추가하여 커밋을 준비한다. 커밋·병합은 이 명령에 포함되지 않는다.

중앙 PreToolUse가 최초 실행 전에 독립 명령 승인을 요구했다. 사용자 승인 후 아래 동일 명령을 같은 위치에서 1회 실행해 exit 0으로 완료했다. 스테이징된 변경은 22파일·872추가·177삭제이며 diff 검사도 통과했다. 현재 pending 명령은 별도 git commit이며 handoff.md에 기록했다.

```sh
git add -- src/features/citizen-participation/api/comment/comment.dto.ts src/features/citizen-participation/api/discussion/discussion.api.ts src/features/citizen-participation/api/discussion/discussion.dto.ts src/features/citizen-participation/api/discussion/discussion.api.test.ts src/features/citizen-participation/api/discussion/discussion.parser.ts src/features/citizen-participation/hook/useCitizenCommentActions.ts src/features/citizen-participation/hook/useCitizenParticipationMutations.ts src/features/citizen-participation/hook/useCitizenParticipationQueries.ts src/features/citizen-participation/hook/useDiscussionParticipation.test.tsx src/features/citizen-participation/hook/useDiscussionParticipation.ts src/features/citizen-participation/index.ts src/features/citizen-participation/testing.ts src/features/citizen-participation/mocks/browserHandlers.test.ts src/features/citizen-participation/mocks/browserHandlers.ts src/pages/citizen-participation/model/presentation.test.ts src/pages/citizen-participation/model/presentation.ts src/pages/citizen-participation/model/resultPresentation.test.ts src/pages/citizen-participation/model/useDiscussionDetailController.test.tsx src/pages/citizen-participation/model/useDiscussionDetailController.ts src/pages/citizen-participation/ui/CitizenListRoutes.tsx src/pages/citizen-participation/ui/CitizenParticipationDetailRoutes.tsx src/pages/citizen-participation/ui/CitizenResultRoutes.test.tsx
```
