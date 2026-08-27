# 계획

## 목표

`proposal.api.ts`의 `Unsafe assignment of an error typed value`를 제거하고, 같은 오류가 반복되는 원인을 끊는다.

## 범위

- 생성 DTO를 `createProposal.dto.ts`로 분리
- pages·테스트의 feature barrel import를 깊은 경로로 교체
- barrel에서 생성 DTO/parser 재export 제거
- Location 파싱을 `postProposal` 안으로 옮겨 mutations가 god parser에 의존하지 않게 함

## 제외 사항

- `parseVoteResponse`를 mutations에서 제거하는 일괄 정리
- feature barrel 자체를 삭제

## 제약 조건

- 사용자 지시: `Fix it`
- 생성 POST 동작은 유지

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| import/DTO 분리 | Hephaestus | coding-convention, type-definition | error 유형 할당이 사라짐 |
| 검증 | Hephaestus | documentation | eslint·vitest 통과 |
| 문서 | Hephaestus | documentation, portfolio | 세션 산출물 8종 |

## 검증

대상 eslint, 관련 vitest

## 위험 요소 및 결정 사항

- CLI eslint는 이미 통과했다. IDE `projectService`가 순환 그래프에서 `error` 유형을 넣는다.
- `title`만 통과하고 나머지 필드가 실패한 것은 옛 `CreateProposalRequestDto`(`title`/`body`/`detail`/`effect`)가 사용처에 남아 있던 증상이다.

## 승인

- 상태: approved
- 승인 문구: `Fix it`
