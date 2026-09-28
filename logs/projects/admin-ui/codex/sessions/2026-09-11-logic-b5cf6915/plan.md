# 계획

## 병합 요청

사용자가 `news-management-ui로 merge 진행`을 요청했다. source는 task/logic-type-lint의 7c5f91c, target은 기본 checkout의 task/news-management-ui cd08d5e였다. 직접 부모 관계·미처리 자식·형제와 이전 실패 이력·함수 문맥 diff·호출부를 확인한 뒤 사용자의 `명령 실행 승인`으로 보호 작업 67762d945c31414596a71afbb6f5bf16을 실행했다. 2개 커밋·16개 파일이 ff-only로 통합됐으며 target에서 lint(오류·경고 0건)·build·별도 tsc·전체 Node 테스트 163개가 모두 통과했다. 두 branch의 HEAD는 7c5f91c이고 worktree는 깨끗하다. branch·worktree를 보존했으며 원격 반영은 수행하지 않았다. 요청한 수정·커밋·병합·검증은 완료됐다.

## 추가 요청: 생성 파일 lint 제외

사용자가 `eslint.config.js`의 `globalIgnores`에 `public/mockServiceWorker.js`를 추가하는 구체적인 계획을 제시하고 “이거 수정하고, 커밋해”라고 승인했다. Logic 역할의 도구 설정 범위로 처리한다. 작업 위치는 기존 source worktree이며 시작 HEAD는 fd619a6이다. 생성 파일 자체는 편집하지 않고 지정한 한 줄을 수정해 재생성 시에도 lint 경고가 사라지도록 한다. `npm run lint`, `tsc --noEmit -p tsconfig.app.json`, `npm run build`, `git diff --check`가 모두 통과했다. 이 변경만 별도 커밋하며 새로운 Git 작업의 보호 승인 절차를 따른다. 병합은 이번 커밋 승인에 포함되지 않는다. 아래 내용은 앞선 Logic 오류 수정 계획의 이력이다.

## 목표

사용자가 지정한 `logic-type-lint` 브랜치에서 UI 오류를 제외한 Logic 오류의 존재와 범위를 실행 근거로 확인한다.

사용자의 후속 설명에 따라 최종 기준 브랜치는 `task/news-management-ui`이며, 그 브랜치에서 Logic 오류가 없어야 한다. 두 브랜치의 HEAD·diff를 대조하고 기본 checkout에서도 lint를 직접 실행해 현 상태를 확인한다.

## 작업 유형

- 최초 조사 후 사용자 명시 지시에 따라 Logic 타입·lint 수정으로 전환.

## 범위

- 작업 위치: `/private/tmp/asan-metaverse-admin-ui-logic-type-lint-7ca0171b`.
- 대상: `task/logic-type-lint`, HEAD `cd08d5ed3ecd94a45d216fd28afe15fd418d8c76`.
- 기본 checkout과 Git common directory가 같은 linked worktree임을 확인했다.
- 실제 소스와 인접 DTO·콜백 참조를 읽고 lint 결과를 Logic 책임으로 분류한다.

## 제외 사항

UI 오류 수정, 패키지·정책 변경, 실서버 요청 및 시각 QA. Git stage·commit·merge는 수정본과 검증 결과를 준비한 뒤 별도 명령 실행 승인을 따른다.

## 제약 조건

기존 변경을 보존한다. 이전 세션 기록은 맥락으로만 사용하며 현재 검증 결과를 다시 수집한다. 자기 세션 문서만 기본 checkout에 작성한다.

## 스킬 및 역할

- 확인된 역할: `logic` (inject와 사용자 요청).
- 역할 판단 근거: API·DTO·공용 이벤트 계약의 오류 조사.
- 승인할 Git 작업: 없음.
- 산출물 책임: owner.

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 브랜치·worktree 조회 | logic | task-role-routing, git-branch-strategy | 실제 대상·HEAD·미커밋 상태 확인 |
| 오류 조사 | logic | implementation-quality | 재현되는 오류와 파일·행 확인 |
| 기록 | logic | documentation | 이번 실행 근거와 제한을 plan·final-summary에 보존 |

## 검증

- [x] 대상 worktree에서 `npm run lint`로 잔여 오류를 수집한다.
- [x] 같은 위치에서 `npm run build`와 별도 `tsconfig.app.json` 타입 검사로 컴파일 오류를 확인한다.
- [x] 기존 `tests/`의 27개 테스트 파일을 Node test runner로 실행한다.
- [x] `git status`와 `git diff --check`로 대상 소스에 변경이 없는지 확인한다.

## 위험 요소 및 결정 사항

서버 응답의 미확인 필드를 새로 추정하지 않는다. 기존 전체 응답 DTO가 있는 이벤트 목록·상세 등은 그 DTO를 재사용한다. 전체 응답 형태가 없는 미사용 API는 반환 data를 unknown으로 노출해 호출자가 검증 없이 필드에 접근하지 못하게 한다. 계산하는 응답은 기존 DTO 및 실제 계산 필드에 타입을 부여한다.

빈 업로드 DTO는 인접 multipart API·이미지 업로드 hook에서 사용하는 FormData로 제한한다. 사용처가 없는 콜백은 구체적인 인자와 반환을 추정하지 않고 (...args: never[]) => unknown으로 제한한다. 이벤트 이름·payload 나머지 필드·PubSub 싱글턴은 보존한다.

수정 위치는 기존 `task/logic-type-lint` linked worktree다. API 8개·빈 DTO 3개·이벤트 계약 1개와 필요한 로컬 DTO·테스트가 예상 diff다. 검증은 응답 전달·계산·multipart 요청 동작 및 안전한 타입 경계 테스트, 전체 lint·타입·build·기존 테스트 순서다. 최종 병합 대상은 `task/news-management-ui`다.

## 승인

- 구현 지시: 사용자의 “그거 logic-type-lint에서 오류 수정하라고. 그 수정본을 news-manaement-ui 브랜치에 merge 하게”에 따라 확인된 39건을 해당 브랜치에서 수정한다.
- Git 변경은 아직 실행하지 않았으며 정확한 명령에 대한 별도 승인을 받는다.
- 실제 승인 상태: 최초 보호 훅 차단 후 사용자의 `진행해`로 승인됐다. 이번 15개 파일 변경이 적용됐고 lint 오류 0건·타입·build·테스트 163개 통과를 확인했다.
- 사용자가 제공한 `/admin/news` 5개 endpoint 명세를 공지사항 계약의 정본으로 추가한다. news.api.ts·news.dto.ts·news.parser.ts·목록/폼 model과 기존 테스트를 대조했다. 요청 필드·enum·기본 페이지·검색 쌍·PATCH 누락과 false 구분·mutation null 처리에 현재 대응 코드가 있다. 이번 39건은 news 파일에서 발생한 오류가 아니다.
