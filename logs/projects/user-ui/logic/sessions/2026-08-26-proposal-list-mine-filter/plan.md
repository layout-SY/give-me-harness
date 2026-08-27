# 계획

## 목표

확정된 `GET /citizen/proposals` 계약을 반영한다. `mine=true`면 토큰 사용자가 등록한 제안만 받고, `sort`는 `createdAt`·`id`만 허용하며 기본값은 `createdAt,desc`다. 제안 목록 화면에 「내활동만 보기」 필터를 연결한다.

## 범위

- `GetProposalListQueryDto`에 `mine?`·`sort?` 추가, 허용 sort 상수
- `getProposalList`가 `page`/`size`/`sort`를 보내고, `mine===true`일 때만 `mine=true`와 인증 설정을 붙인다
- 제안 목록 훅·query key가 `mine`·`sort`를 포함한다
- `ProposalListRoute`가 `/me/activity` 대신 같은 목록 API에 `mine=true`를 보낸다
- 제안 목록 토글 라벨을 「내활동만 보기」로 바꾼다
- MSW가 `mine=true`일 때 `item.mine === true`만 반환한다
- 목록 응답에 본문 4필드가 없음을 테스트로 고정한다

## 제외 사항

- 투표·토론·정책 목록의 `/me/activity` 분기
- 내 활동 페이지(`CitizenAuxiliaryRoutes`)의 activity 훅
- 정렬 UI 컨트롤 추가
- 목록 카드 `summary` 제거
- 다른 콘텐츠 타입 목록 응답 재설계

## 제약 조건

- 명시 승인 후 구현. 사용자 지시: `추가해`
- 목록에는 `background`·`content`·`expectedEffect`·`referenceCase`가 없고 상세에서만 내려간다
- `sort`는 `createdAt`·`id`만 허용한다
- 사용자가 제안 목록 필터 UI 추가를 이 작업에 배정했다

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| DTO/전송 | Hephaestus | recipe-api-authoring, recipe-data-dto, type-definition | `mine`/`sort`가 확정 query로만 전송됨 |
| 훅/라우트 | Hephaestus | data-fetch-layer, hook-extraction | 목록 화면이 단일 `useProposalListQuery`를 씀 |
| UI 라벨 | 사용자가 이 작업에 배정 | publishing, styles | 기존 토글에 「내활동만 보기」 라벨 |
| MSW/테스트 | Hephaestus | recipe-api-authoring | `mine=true`와 본문 4필드 부재를 검증 |
| 문서 | Hephaestus | documentation, portfolio | 세션 산출물 8종 |

## 검증

`npx vitest run` (관련 스위트), `npm run build`, `npm run lint`

## 위험 요소 및 결정 사항

- `mine` 기본값은 false이므로 `mine=false`를 query에 실지 않는다
- `sort` 기본값 `createdAt,desc`는 전송 계층에서 항상 붙인다
- 제안 목록의 내 활동은 `/me/activity`가 아니라 list endpoint의 `mine`이다

## 승인

- 상태: approved
- 승인 문구: `추가해`
