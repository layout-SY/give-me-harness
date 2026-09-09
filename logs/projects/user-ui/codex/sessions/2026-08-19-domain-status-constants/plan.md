# 계획

## 목표

확정된 ProposalStatus, VoteChoice, OpinionStance를 서로 독립된 uppercase `as const` 계약으로 정의하고 API·mock·route에서 동일 값을 사용한다.

## 범위

- ProposalStatus: `RECEIVED`, `UNDER_REVIEW`, `ADOPTED`, `REJECTED`
- VoteChoice: `AGREE`, `DISAGREE`
- OpinionStance: `AGREE`, `DISAGREE`, `NEUTRAL`
- Zod request/response/detail parser와 MSW 상태 저장
- lowercase production UI와 uppercase transport 사이 route adapter
- proposal presentation 표시 매핑과 관련 테스트

## 제외 사항

- 아직 확정되지 않은 Vote·Discussion·Policy·Survey lifecycle status 재정의
- Claude Code 소유 production UI 파일 수정
- auth·meeting 범위 밖 테스트 수정

## 역할과 스킬

| 구간 | 역할 | 스킬 | 결과 |
| --- | --- | --- | --- |
| 탐색 | Hephaestus + Explore | `skill-index`, `policy-index` | API와 UI 영향 범위 분리 |
| 구현 | Hephaestus | `programming`, `policy-coding-convention`, `policy-type-definition` | 상수·DTO·mock·route adapter |
| 검토 | 수동 Watcher 대체 | `policy-review-checklist` | 범위와 검증 근거 판정 |

## 승인

- 상태: approved
- 근거: 사용자가 확정 값 세 종류를 제시하고 즉시 반영하도록 지시함
