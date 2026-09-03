# 계획

## 요청 요약
- 구현·수정·리팩터링과 AI 하네스 변경 완료 후 이력서/포트폴리오 경험 기록을 필수 산출물로 남긴다.
- 문제 상황, 사용자·에이전트 제안과 선택, 기술의 구체적 목적, 적용, before/after 결과, 검증·피드백·회고를 기록한다.

## 작업 유형
- hybrid: policy + harness

## 범위
- `policy-portfolio`와 portfolio template 확장
- AGENTS·policy·agent·workflow·multi-agent spec의 완료 책임 정렬
- Stop hook의 source/config/harness/untracked 변경 감지와 portfolio 필수 섹션 검증
- hook 회귀 테스트와 이번 작업의 portfolio 기록

## 제외 범위
- 기존 portfolio entry 마이그레이션
- 파일 변경 없는 질의응답·탐색·audit-only 작업 강제
- 애플리케이션 `src/` 동작 변경

## 섹션
1. 정책·template 규격
2. 역할·workflow 책임 정렬
3. Stop hook과 회귀 테스트
4. 문서화·품질 게이트

## 필요 에이전트
- Orchestrator: 문서·정책·hook 구현 및 portfolio 작성
- Watcher: 현재 변경 pass/fail
- Evaluator: 장기 하네스 리스크 평가

## 필요 스킬
- `policy-portfolio`
- `policy-documentation`
- `policy-harness`
- `policy-review-checklist`
- `policy-index`
- `programming`

## 승인 기록
- 사용자가 `진행해줘`로 구현을 승인했다.
