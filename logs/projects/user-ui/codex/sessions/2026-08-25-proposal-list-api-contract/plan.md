# 계획

## 목표

확정된 proposal list 응답과 수정된 요청 계약(`page`/`size`만 전송)을 DTO·API·훅·MSW·목록 사용처에 반영한다. 내 활동 필터는 `content`·`page`·`size`를 쓰는 `/me/activity` 별도 요청으로 분리한다.

## 범위

- `GetProposalListQueryDto` / `GetProposalListResponseDto` 재설계
- `proposalApi.getProposalList`가 `page`/`size`만 전송
- `ActivityListQueryDto`를 `content?`·`page`·`size`로 변경
- `useProposalListQuery`, `useMyActivityQuery` enabled 분기
- MSW proposal list SUCCESS envelope 및 숫자 id 아이템
- `CitizenListRoutes`·presentation mapper가 새 DTO를 직접 사용

## 제외 사항

- proposal 상세/작성 응답 재설계
- vote/discussion/policy/survey 목록 응답 재설계
- `status`/`sort`를 proposal list 요청에 유지
- `ProposalListPage` 요약 영역 제거, `REJECTED` 뱃지 추가
- 공용 `ServerResponse` 타입을 string `code`로 전면 교체

## 제약 조건

- 명시 승인 후 구현. 사용자 지시: `이렇게 수정 작업 진행해`
- Claude Code UI 파일은 목록 DTO 사용처인 `CitizenListRoutes.tsx`만 최소 연결
- 미확정 activity 응답 형태는 기존 `ActivityListResponseDto` 유지

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| DTO/parser | Hephaestus | recipe-api-authoring, recipe-data-dto, type-definition | 확정 JSON과 같은 목록 계약 |
| API/훅 | Hephaestus | data-fetch-layer, hook-extraction | list와 activity 요청 분리 |
| MSW/테스트 | Hephaestus | recipe-api-authoring | Axios 경로로 계약 검증 |
| 사용처 | Hephaestus | coding-convention | 새 DTO를 화면 매퍼에 직접 연결 |
| 문서 | Hephaestus | documentation, portfolio | 세션 산출물 8종 |

## 검증

`npx vitest run` (관련 스위트), `npm run build`, `npm run lint`

## 위험 요소 및 결정 사항

- 목록 요청에서 `status`/`sort`/`myActivity`를 보내지 않는다.
- `code === "SUCCESS"`만 공용 unwrap에 추가하고 기존 `success: true`는 유지한다.
- activity 응답 페이지네이션 필드(`pageSize` 등)는 미확정이라 바꾸지 않는다.

## 승인

- 상태: approved
- 승인 문구: `이렇게 수정 작업 진행해`
