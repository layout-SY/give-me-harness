# 시민 토론 API 타입 오류 수정과 완료 준비

## 목표와 작업 유형

기존 토론 API 구현의 TS2379를 수정하고 검증·커밋 후 sy-main 병합의 최종 계약을 준비한다. 작업 유형은 기존 feature의 버그 수정과 완료 준비다.

## 요청과 승인

- 사용자 요청: `.codex/logs/sessions/2026-09-08-logic-d7a35053/handoff.md`를 읽고 남은 타입 오류 수정·검증·커밋을 진행하며, sy-main 병합은 최종 계약을 준비해 별도 승인을 요청한다.
- inject role: logic, Git 통합 담당자: codex, 책임: owner.
- 현재 assignment: `72a6097ea5164284ba3f882f5e0bcddb`.
- 현재 assignment의 harness-state-v3.json에서 이번 사용자 요청의 implementation_approved, skill_confirmed, exploration_completed가 모두 true임을 첫 소스 수정 전에 확인했다. 이전 assignment의 승인을 복사하지 않았다.

## 범위와 순서

1. 승인된 워크트리의 조회 훅에서 선택 속성의 undefined를 생략해 캐시 키 DTO와 타입을 맞춘다.
2. 같은 워크트리에서 `npm run lint`, `npm run test`, `npm run build`, `git diff --check`로 검증하고 기존 투표 실패를 구분한다.
3. 현재 세션에 owner 산출물을 작성하고 검토 결과와 제한을 기록한다.
4. 변경된 경로를 명시해 stage·commit한 후 source·target HEAD를 고정한 finish-proposal을 만든다.
5. 병합 방식·통합 워크트리·검증 명령·정리 여부·전체 SHA-256을 보고해 별도 병합 승인을 요청한다.

## Git 계약과 소유권

- branch: `task/citizen-discussion-api-resume`, 상태 ACTIVE.
- worktree: `/Users/okand/SynologyDrive/asan-metaverse-user-ui-worktrees/citizen-discussion-api-resume`.
- parent 및 직접 merge 대상: `sy-main`.
- 분기 당시 parent HEAD: `466567aee8476459c813c0575e3593eb296f8f33`.
- V3 계약 SHA: `7279d610ed7aad373703ff54dd9d715798298e6e2bcc8aedf5b4d45061f66d66`.
- 기존 소스 scope: 시민참여 api·hook·model·mocks·index.ts·testing.ts와 시민참여 pages.
- 현재 세션 산출물은 launcher 지정 디렉터리에 작성한다. 이전 세션 문서는 읽기 전용 인계 근거다.

## 선택과 제약

인접 useVoteListQuery처럼 page·size·mine을 명시하고 status·search·sort는 정의된 경우에만 넣는 최소 수정을 선택한다. 공통 ContentListQueryDto의 optional 계약 확대나 새 공용 정규화 함수는 필요하지 않다. 타입 단언과 TypeScript 설정 완화를 사용하지 않는다.

토론 임시 wire 계약의 재설계, 기존 투표 API/mock 실패 수정, UI 시각 변경과 중앙 정책 수정은 이번 재개 요청에 포함하지 않는다. 실제 서버 계약 호환성은 검증하지 않았다.

## 스킬

task-role-routing, git-branch-strategy, coding-convention, type-definition, data-fetch-layer, implementation-quality, documentation, portfolio 및 api-authoring을 읽었다. 현재 수정에는 인접 조회 훅과 기존 DTO·캐시 키를 재사용한다.

## 병합 준비 시 확인할 사항

현재 sy-main은 `c79f3d8c74c0536fa2d3afb983fb2e121742f076`으로 분기 이후 예약 팝업 커밋이 추가됐다. 따라서 커밋 후 merge-commit 계약이 필요하다. 현재 target 워크트리는 `/Users/okand/SynologyDrive/asan-worktrees/reservation-restricted-popup`이며 읽기 전용 확인 시 clean이었다. 최종 proposal 직전에 다시 확인한다. 병합·정리 승인은 아직 없다.
