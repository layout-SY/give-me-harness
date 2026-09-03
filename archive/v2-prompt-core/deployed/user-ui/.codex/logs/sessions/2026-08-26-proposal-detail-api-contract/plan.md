# 계획

## 목표

제안 상세 GET을 확정 응답 DTO에 맞추고, 시민참여 API path 접두사를 `/citizen`으로 바꾼다.

## 범위

- `GET /citizen/proposals/{proposalId}` 응답 DTO: id, title, background, content, expectedEffect, referenceCase, status, author|null, createdAt, updatedAt
- 시민참여 API·MSW·테스트 경로 `/v1/api/citizen-participation` → `/citizen`
- 파서·훅·presentation 매퍼·MSW 상세 매퍼 연결

## 제외 사항

- 토론·정책·설문 상세 DTO 재설계
- 제안 목록 author null 계약 (이번 명세는 상세만)
- ProposalDetailPage 마크업

## 제약 조건

- 사용자 지시: 제안 상세 요청/응답 DTO 설정, path 접두사는 `/citizen`, `v1`/`api` 없음
- 작성자 탈퇴 시 `author`는 `null`
- 미확정 필드(`reviewResult` 등)를 응답 DTO에 넣지 않음

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| DTO/parser | Hephaestus | recipe-api-authoring, recipe-data-dto, type-definition | GetProposalDetailResponseDto |
| path | Hephaestus | data-fetch-layer | `/citizen/proposals`, `/citizen/votes` |
| 훅·매퍼 | Hephaestus | data-fetch-layer | useProposalDetailQuery, toProposalDetail |
| 검증 | Hephaestus | documentation | eslint·tsc·테스트 |

## 검증

대상 eslint, `tsc -b`, 시민참여 API·MSW·presentation·페이지 테스트

## 위험 요소 및 결정 사항

- `useCitizenContentDetailQuery`에서 proposal을 빼지 않으면 ContentDetailDto 파서가 새 필드를 거부한다.
- UI 라우트는 훅 연결이 없으면 상세가 깨지므로 `CitizenReadDetailRoutes`만 훅을 교체한다.

## 승인

- 상태: approved
- 승인 문구: `설정해`
