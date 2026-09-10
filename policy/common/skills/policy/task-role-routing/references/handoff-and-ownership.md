# Handoff와 작업 기록

handoff는 작업 연속성을 위한 상태 기록이며 구현 승인이나 Git 변경 승인을 대신하지 않는다.

## 작성 시점과 내용

작업자·host·role·세션이 바뀌거나 중단할 때 목표, 현재 상태, 완료·대기 작업, 결정, 실제 경로·branch·HEAD·worktree, dirty/staged 변경, 명령과 검증 결과, 다음 조치를 기록한다. 역할 필드는 `requested_roles`, `confirmed_roles`, `completed_roles`, `next_role`을 사용한다. 인계받는 세션은 최신 사용자 요청과 실제 Git 상태를 함께 확인한다. inject role이 있으면 같은 역할을 반복 확인하지 않는다.

## 산출물

`owner`는 `plan.md`와 `final-summary.md`를 작성한다. 부분 기여자 또는 중단·인계는 `handoff.md`로 남긴다. 세부 탐색·구현·리뷰·평가·portfolio·grill-me 문서는 필요에 따라 선택한다. 문서 누락으로 Git이나 다음 작업을 차단하지 않는다.

자기 세션의 논리적 산출물 경로만 수정한다. 다른 host의 설정·로그와 다른 세션 기록은 읽기 전용이다. 이미 커밋된 기록을 branch 병합으로 전달할 수 있다. 정의되지 않은 보조 기록은 자기 세션의 `unknown/`에 둔다.

## Git과 동시 작업

모든 세션은 프로젝트의 모든 branch/worktree에서 사용자 승인 후 Git 변경을 실행할 수 있다. contributor·host·assignment로 실행자를 제한하지 않는다. 완료 통합은 미처리 하위 작업이 없는 자식에서 직접 부모로 수행하며 형제 검토와 승인을 받는다. 세션 독점 Git claim과 CLOSED 해제 절차는 없다. 보호 실행기의 짧은 Git lock을 사용하며 병렬 구현에는 별도 linked worktree를 사용한다. 다른 작업의 변경을 덮어쓰거나 임의로 commit하지 않는다.

새 정책 적용 시 현재 세션을 handoff하고 새 inject assignment를 시작한다. Git 소유권 이전 명령은 필요하지 않으며, 과거 assignment를 resume하면 원래 bundle을 사용한다.
