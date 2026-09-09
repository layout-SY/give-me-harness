# 탐색

## 요청

사용자는 `CitizenParticipationDetailRoutes.tsx` 68–71행의 `Unsafe assignment of an error typed value`를 고치고 검증한 뒤 짧게 설명하라고 했다.

## 대상 관련 사실

- ReadLints는 13건이었다. 시작점은 L50 `useVoteDetailQuery` 호출이 해석되지 않는 유형이라는 오류였다. `persistedChoice` 할당은 그 결과의 `.data`를 읽어서 난 후속 오류다.
- 훅은 `~/features/citizen-participation` barrel에서 가져왔다. 같은 오류는 이전에 `CitizenAuxiliaryRoutes`에서 barrel 순환으로 확인됐다.
- `CitizenListRoutes`와 `CitizenAuxiliaryRoutes`는 이미 `hook/useCitizenParticipationQueries` 깊은 경로를 쓴다.
- `src/shared/ui/`는 이번 타입/import 수정과 무관하다.

## 불러온 스킬

- `policy/coding-convention`, `policy/type-definition`, `policy/documentation`, `policy/portfolio`, `policy/harness`

## `src/shared/ui/`의 재사용 가능 자산

없음. UI 컴포넌트를 추가하거나 바꾸지 않는다.

## 제약 조건 및 미확인 사항

- 훅 구현의 `QueryKey` generic은 이미 있다. 문제는 사용처 import다.

## 결론

feature barrel 대신 훅·페이지 깊은 경로를 쓰면 `useVoteDetailQuery` 반환 타입이 복구되고 68–71행 할당 오류도 사라진다.
