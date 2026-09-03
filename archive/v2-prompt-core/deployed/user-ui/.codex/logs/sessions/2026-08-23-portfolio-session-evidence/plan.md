# 계획

## 목표

기존 admin-ui 하네스 비교 포트폴리오에 OpenCode의 사용자 지시, compaction 전후 목표 변화, 세션 사용량, 사용자 비용·품질 피드백을 명확히 기록하고 향후 모든 AI 세션 사고가 같은 근거 수준을 따르도록 정책과 템플릿을 강화한다.

## 범위

- `AGENTS.md`와 포트폴리오·문서화 policy skill의 세션 사고 근거 규칙
- `portfolio-log.md` 스키마와 복사 템플릿의 전용 필드·실제 사례 예시
- 기존 admin-ui 하네스 비교 포트폴리오와 분석 문서의 chronology·사용량 근거
- 현재 변경의 필수 8종 산출물

## 제외 사항

- 애플리케이션 source, UI, CSS와 package 변경
- admin-ui 또는 user-ui의 Hook·host adapter 구현
- 전체 세션 token을 특정 브라우저·검토 작업의 소비량으로 환산하는 추정
- unrelated `src/shared/ui/date-range-picker/date-range-picker.tsx` 변경

## 제약 조건

- 원본 OpenCode session metadata와 transcript에서 직접 확인한 값만 사용한다.
- 예시 수치와 사용자 피드백을 다른 작업의 성과로 재사용하지 않는다.
- 사용량 총계와 반복 작업 사이의 인과 해석 한계를 함께 기록한다.
- 필수 Watcher 문서 판정 외의 리뷰 에이전트나 브라우저·시각 QA를 실행하지 않는다.

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 세션 근거 확인 | Hephaestus | `coding-agent-sessions` | 사용자 지시·compaction·사용량 원본 확인 |
| 정책·템플릿 변경 | Hephaestus | `policy-portfolio`, `policy-documentation`, `policy-harness` | 재사용 가능한 세션 사고 기록 규칙 |
| 현재 변경 판정 | Watcher | `policy-review-checklist` | 근거 정확성·요청 충족 PASS/FAIL |

## 검증

- 필수 산출물 artifact validator
- Markdown trailing whitespace 검사
- `GIT_MASTER=1 git diff --check`
- `npm run lint`
- `npm run build`

## 위험 요소 및 결정 사항

- session token은 전체 세션 총량이므로 특정 위반 작업의 비용으로 단정하지 않는다.
- `.codex/templates/portfolio-log.md`의 현재 사례는 표현 예시이며 복사 가능한 현재 작업 근거가 아님을 명시한다.
- Markdown LSP가 구성되지 않은 경우 artifact validator와 정적 명령으로 대체하고 제한을 기록한다.

## 승인

- 상태: approved
- 승인: 2026-08-23 사용자 `진행해줘`
- 필수 문구: `이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?`
