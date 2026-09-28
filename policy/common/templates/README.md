# 세션 문서 템플릿

기존 변경의 commit·merge만 수행하는 요청에는 `documentation`의 산출물 예외를 적용하여 템플릿을 복사하거나 빈 문서를 만들지 않는다. 같은 작업에서 구현을 변경한 경우에는 해당 작업 문서에 Git 처리 결과를 함께 기록한다.

`owner`의 기본 기록은 `plan.md`와 `final-summary.md`다. 부분 기여자 및 인계는 `handoff.md`를 사용한다. 탐색·구현·리뷰·평가·grill-me·portfolio 템플릿은 필요한 작업에서 선택하며 실제 실행 근거를 작성한다. 문서 누락은 Git 접근이나 작업 시작의 차단 조건이 아니다.

renderer는 같은 템플릿을 각 host에 제공한다. 다른 세션의 기록은 읽기 전용이다. 정의되지 않은 보조 기록은 자기 세션의 `unknown/`에 둔다.

`handoff.template.md`에는 보내는 현재 위치와 인계 대상 작업 위치를 구분하고, 작업 공간별 branch·worktree 절대 경로·기준 HEAD·부모 관계와 역할별 구체적인 작업·연결 계약·완료 기준을 작성한다. UI·Logic이 공유 공간에서 순차 작업하거나 분리 공간에서 병렬 작업하는 이유와 순서를 함께 남긴다. 작업 공간 계획은 세션의 브랜치 접근 권한이 아니다. 상세 예시는 `.agent-policy/common/skills/policy/task-role-routing/references/handoff-and-ownership.md`를 따른다.
