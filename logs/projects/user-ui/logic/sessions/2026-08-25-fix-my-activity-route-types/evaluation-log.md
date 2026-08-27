# 평가 로그

Watcher 판정(PASS)과 별개로, 다음 작업에서 반복될 수 있는 구조만 적는다.

## 장기 관찰 사항

- pages가 `~/features/citizen-participation` barrel에서 훅과 페이지를 같이 가져오면, 편집기 projectService가 훅 export를 오류 유형으로 만들 수 있다
- `useQuery`에 `UseQueryResult<z.infer<ZodObject>>`를 명시하면 queryKey `as const` 튜플과 겹쳐 타입 인스턴스화가 실패하기 쉽다
- presentation이 UI 페이지의 props 타입을 다시 import하면, 라우트가 같은 페이지를 값으로 import할 때 매퍼 함수가 오류 유형이 된다

## 재사용 가능 자산

- 제안 목록 data 형태는 `GetProposalListResponseDto` 수동 타입으로 고정되어 있다
- 제안 내 활동 카드 매퍼는 `proposalActivityPresentation.ts`에 있다

## 기술 부채

- `CitizenMainRoute`, detail/report 라우트는 여전히 feature barrel을 사용한다
- 제안 상태 라벨이 presentation과 activity 매퍼에 중복된다
- `toProposalListPageCount`는 ListRoutes에서 쓰이지 않고 테스트만 사용한다

## 프로세스 개선 사항

- 새 훅을 feature barrel에 추가한 뒤 pages에서 바로 재export를 쓰면, CLI eslint는 통과하고 편집기만 실패할 수 있다. pages는 훅 파일을 직접 import하는 쪽이 안전하다

## Watcher와의 구분

현재 작업의 lint/build 목표는 충족했다. 위의 barrel·라벨 중복은 이번 수정의 실패가 아니라 남은 구조다.
