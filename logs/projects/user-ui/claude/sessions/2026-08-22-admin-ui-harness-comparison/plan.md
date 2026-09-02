# 계획

## 목표

admin-ui 두 OpenCode 세션과 user-ui 현재 세션의 하네스 동작을 비교하고, 반복된 UI/CSS 소유권 침범과 브라우저·Watcher·이미지 QA의 구조적 원인을 근거 문서로 남긴다.

## 범위

- 세 main session과 child session 통계 및 핵심 message 확인
- 두 저장소의 AGENTS, CLAUDE, Hook, settings, Git 추적, test command 비교
- user-ui 반영 완료 영역과 host별 hard gate 미완성 영역 구분
- `docs/admin-ui-harness-gap-analysis.md` 작성

## 제외 사항

- admin-ui 또는 user-ui application source 수정
- 하네스 구현·이식
- 브라우저, screenshot, visual QA, Watcher·review agent 실행
- 사용자 또는 다른 세션의 worktree 변경 정리

## 제약 조건

- 관찰한 세션·파일·명령 결과만 기록한다.
- 상관관계를 원인으로 과장하지 않는다.
- admin-ui Python Hook과 OpenCode 실행 경계의 차이를 명시한다.

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 세션 조사 | Hephaestus | coding-agent-sessions | 두 admin OpenCode session과 user-ui control 확인 |
| 하네스 조사 | Hephaestus | policy-harness | 선언과 실제 강제 경로 비교 |
| 문서화 | Hephaestus | policy-documentation, policy-portfolio | 분석 문서와 8종 산출물 작성 |

## 검증

- user-ui governance 22 tests
- admin-ui portfolio gate regression script
- 문서 구조 validator와 trailing whitespace 확인

## 위험 요소 및 결정 사항

- Claude Code 세션과 OpenCode 세션을 혼동하지 않고 사용자가 지적한 Hephaestus 동작은 OpenCode session을 기준으로 판단한다.
- user-ui 현재 세션에도 과거 Watcher child 실행이 있었음을 별도 한계로 기록한다.

## 승인

- 상태: approved by direct user documentation request
- 사용자 요청: 비교 내용을 먼저 문서화한 뒤 user-ui 반영 상태를 확인한다.
