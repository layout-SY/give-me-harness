# 탐색 기록

## 대상 경로
- `src/hooks/`
- `src/pages/dao/discuss-posts-management/detail/hook/useDiscussDetailFetch.tsx`
- `src/pages/dao/proposal-manage/detail/hooks/useProposalDetailFetch.tsx`

## 발견한 기존 재사용 자산
- 발견 항목: `useApi`
- 재사용 제안: API execute는 그대로 사용하고, 화면 단위 loading runner만 별도 hook으로 분리
- 근거: `useApi`는 API 호출/에러 Dialog를 담당하지만 도메인 화면의 local loading 템플릿을 대체하지는 않음

- 발견 항목: 반복 `setIsLoading(true) -> execute -> finally setIsLoading(false)` 패턴
- 재사용 제안: id를 모르는 `useAsyncTask`로 공용화
- 근거: DAO proposal detail 등 여러 위치에 유사 흐름 존재

## 재사용이 어려운 자산
- 자산: `runCurrentPostAction` 전체
- 부적합 사유: `fetchedData.postId`, DAO refresh event, success message, detail refetch 정책을 포함해 도메인 결합이 강함

## 신규 자산 필요성
- 필요 항목: `src/hooks/use-async-task/useAsyncTask.ts`
- 필요 이유: 비동기 task 실행과 local loading 상태 관리를 도메인 무관하게 재사용하기 위함
