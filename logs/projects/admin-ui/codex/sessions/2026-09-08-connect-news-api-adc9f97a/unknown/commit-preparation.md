# 로컬 커밋 준비

실행 완료: 별도 사용자 승인 후 아래 git commit 명령이 exit 0으로 완료됐다. 결과 커밋은 `79d31f8bf5e5cb0d72e609e76c14b1fd069b198e`이며 작업 폴더는 clean이다. 이 문서는 실행 준비와 승인 과정을 보존한다.

빌드 미실행·전체 lint 실패를 명시한 채 현재 작업을 보존하기 위한 준비다. 완료 판정·병합이 아니다.

- branch: task/connect-news-api, ACTIVE
- worktree: /Users/okand/SynologyDrive/asan-metaverse-admin-ui
- 준비 당시 HEAD: 98fc4624d4ff3f1257585373147fb137dcc54058
- 커밋 후 HEAD: 79d31f8bf5e5cb0d72e609e76c14b1fd069b198e
- 확인한 변경 파일: 기존 8개, 신규 13개, 모두 V3 승인 scope 안
- index: 승인된 git add 실행 성공, 21 files changed / 1053 insertions / 258 deletions
- 문서: 현재 assignment의 ignored 세션 로그에 보존
- 검증: 대상 28개·전체 134개 테스트 PASS, 변경 파일 lint PASS, 전체 lint 68 errors/5 warnings, build 미실행

## staging 명령 — 사용자 별도 승인 후 실행 완료

```sh
git add -- src/entities/news src/entities/cp-notice/model/types.ts src/mocks/news.handlers.ts src/pages/cp-board/hook/use-cp-notice-form-controller.tsx src/pages/cp-board/hook/use-cp-notice-form-process.tsx src/pages/cp-board/lib/cp-notice-form.model.ts src/pages/cp-board/model/cp-notice-form.config.ts tests/news-contract.test.mjs tests/news-form.test.mjs tests/news-msw.test.mjs tests/news-mutation.test.mjs
```

사용자 별도 승인을 받아 이 명령이 exit 0으로 완료됐다. git diff --cached --check는 PASS이고 unstaged source 변경은 없다. 이후 아래 git commit을 요청했으나 중앙 PreToolUse가 별도 정확한 명령 승인을 요구하며 차단했다. 이전 git add 승인은 성공 시 소비됐으며 commit에 재사용하지 않는다.

## 승인 후 실행 완료한 정확한 커밋 명령

```sh
git commit -m "feat : 공지사항 admin API와 수정 폼 연결" -m "5개 news API의 DTO·parser·query·mutation과 기존 공지 수정 폼을 연결한다." -m "테스트 134개와 변경 파일 lint 통과. 빌드는 승인 훅 차단으로 미실행이며 전체 lint의 기존 오류 68개가 남아 있다."
```

## 커밋 메시지 초안

```text
feat : 공지사항 admin API와 수정 폼 연결

5개 news API의 DTO·parser·query·mutation과 기존 공지 수정 폼을 연결한다.
테스트 134개와 변경 파일 lint 통과. 빌드는 중앙 승인 훅 차단으로 미실행이며 전체 lint의 기존 오류 68개가 남아 있다.
```

원격 반영·sy-main 병합·완료 lifecycle·브랜치 정리는 이 준비 범위에 포함하지 않는다.
