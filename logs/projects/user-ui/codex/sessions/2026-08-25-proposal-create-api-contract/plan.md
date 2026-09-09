# 계획

## 목표

제안하기 POST를 확정된 요청 body와 201 `Location: /citizen/proposals/{id}` 성공 계약에 맞춘다.

## 범위

- `CreateProposalRequestDto`를 `title`/`background`/`content`/`expectedEffect`/`referenceCase: string | null`로 재정의
- `postProposal`가 허용 필드만 복사해 전송
- 폼 UI 필드(`detail`/`effect`/`reference`)를 요청 DTO로 매핑. 빈 참고 사례는 `null`
- 201 `Location`에서 숫자 `id`를 읽어 상세로 이동
- MSW가 201과 Location을 재현하고, 상세 fixture는 기존 `ContentDetailDto`에 저장

## 제외 사항

- `ProposalWritePage` 마크업·폼 필드명 변경
- proposal 상세 GET DTO 재설계
- 사용자 예시에 없던 201 JSON body 필드 발명
- 다른 mutation(`MutationResponseDto`) 일괄 교체

## 제약 조건

- 사용자 지시: `기존에 있는 API 내용 이 구조에 맞게 수정해`
- 성공은 201과 `Location: /citizen/proposals/{id}`
- `referenceCase`만 선택. 생략하면 `null`로 저장
- Axios interceptor가 `response.data`만 넘기므로 Location을 unwrap 단계에서 보존해야 한다

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| DTO/parser | Hephaestus | recipe-api-authoring, recipe-data-dto, type-definition | 확정 body와 Location 기반 `{ id }` |
| API/훅/폼 매퍼 | Hephaestus | data-fetch-layer, validation | 허용 필드만 전송, 빈 참고는 null |
| 201 unwrap | Hephaestus | data-fetch-layer | Location이 `toApiResult`까지 전달 |
| MSW/테스트 | Hephaestus | recipe-api-authoring | Axios 경로로 계약 검증 |
| 라우트 연결 | Hephaestus | coding-convention | `String(id)`로 상세 이동 |
| 문서 | Hephaestus | documentation, portfolio | 세션 산출물 8종 |

## 검증

`npx vitest run src/features/citizen-participation src/pages/citizen-participation`, `npm run lint`, `npm run build`

## 위험 요소 및 결정 사항

- 201 JSON body 예시는 없었다. Location을 응답 계약의 출처로 두고 `{ id }`는 path에서만 파생한다.
- 폼 필드명은 UI에 두고 API 이름으로 매핑한다.
- GET 상세는 아직 옛 `body`/`detail`/`effect`/`reference`를 쓰므로 MSW만 내부 매핑한다.

## 승인

- 상태: approved
- 승인 문구: `기존에 있는 API 내용 이 구조에 맞게 수정해`
