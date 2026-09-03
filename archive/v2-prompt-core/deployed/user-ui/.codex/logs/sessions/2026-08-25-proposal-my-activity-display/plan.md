# 계획

## 목표

제안 목록의 「내 활동 보기」토글이 `/me/activity?content=proposal&page=&size=`를 호출하고, 확정된 목록 응답을 파싱해 같은 카드 목록에 표출한다.

## 범위

- `useMyProposalActivityQuery`가 activity 응답을 `parseProposalList`로 좁힘
- MSW `content=proposal`일 때 SUCCESS + `{ items, total, page, size }`
- `ProposalListRoute`가 토글 on에서 이 훅의 데이터를 `toProposalListItem`으로 렌더
- 내 활동 화면의 제안 필터가 같은 응답을 깨지 않도록 `toActivityItemFromProposalList` 연결

## 제외 사항

- vote/discussion/policy 목록 토글의 응답 재설계
- 내 활동 화면 전체(`content` 생략) 응답 재설계
- `ProposalListPage` 요약 영역 제거

## 제약 조건

- 사용자 지시 `구현해봐` 이후 구현
- activity 응답 본문은 별도 스펙이 없어, 같은 화면에 그리는 확정 proposal list 응답을 사용

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 훅/API | Hephaestus | data-fetch-layer, recipe-data-fetch | content=proposal 요청과 확정 목록 파싱 |
| 사용처 | Hephaestus | coding-convention | 토글 on 시 카드 표출 |
| 검증 | Hephaestus | review-checklist | 라우트 테스트로 요청 key와 제목 확인 |

## 검증

관련 vitest, `npm run build`, `npm run lint`

## 위험 요소 및 결정 사항

activity 응답이 확정 목록과 다르면 파싱이 실패한다. 현재는 사용자 확정 목록 응답을 그대로 사용한다.

## 승인

- 상태: approved
- 승인 문구: `구현해봐`
