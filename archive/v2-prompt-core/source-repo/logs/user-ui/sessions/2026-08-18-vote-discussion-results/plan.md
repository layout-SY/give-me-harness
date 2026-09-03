# 계획

## 목표

Vote·Discussion 목록과 상세가 각 content ID의 집계를 사용하되 전체 상태가 `closed`일 때만 결과를 공개하고, 현재 사용자의 제출 완료 상태는 `open` 상태에서도 별도로 표시한다.

## 범위

- 기존 `agreeCount`, `disagreeCount`, `neutralCount` 응답 계약 확인
- count→ratio presentation 매핑
- 종료된 Vote·Discussion mock 항목 추가
- Vote·Discussion 선택 request와 `{ completed, choice }` 응답
- 상세 응답의 `myVoteChoice`, `myDiscussionChoice`
- Claude Code `hasSubmitted` UI와 route 연결

## 제외 사항

- 진행 중 전체 집계 공개
- Claude Code 소유 production UI 파일 직접 수정
- 다른 세션 소유 auth·meeting·shared text-input 변경

## 역할과 스킬

| 구간 | 역할 | 스킬 | 결과 |
| --- | --- | --- | --- |
| 탐색 | Hephaestus + Explore | `recipe-data-dto`, `recipe-api-authoring` | 기존 API count 계약 확인 |
| 기능 구현 | Hephaestus | `programming`, `policy-data-fetch-layer`, `debugging` | parser·mock·presentation·route 연결 |
| UI 구현 | Claude Code | `project-ui` | ResultBar·`hasSubmitted` 화면 계약 |
| 검토 | 수동 Watcher 대체 | `policy-review-checklist` | 범위 PASS/FAIL 근거 |

## 검증

- 진행 항목은 ratio prop과 ResultBar가 없어야 한다.
- 종료 Vote는 31/69, 종료 Discussion은 30/45/25를 표시해야 한다.
- Vote 찬성 및 Discussion 중립 제출 후 완료 문구·disabled 상태가 보여야 한다.
- 제출 후 상세 GET에 현재 사용자 선택값이 유지되어야 한다.

## 승인

- 상태: approved
- 근거: 사용자의 결과 데이터 확인·구현 지시, 종료 전 비공개 지시, 제출 화면 변화 확인 지시
