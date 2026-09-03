# 탐색

## 사용자 제시 문제

- 제안 작성 필드에 입력해도 값이 UI에 표시되지 않는다.
- 여러 문자를 입력해 제출하면 마지막 문자 하나만 저장되는 것으로 보인다.
- 생성 후 상세로 이동하지만 URL ID가 항상 `proposal-created`다.

## 현재 코드 흐름

- `ProposalWriteRoute`는 `values={form.watch()}`와 `form.setValue(field, value)`를 연결한다.
- `ProposalWritePage`는 모든 input/textarea에 controlled `value`와 `onChange`를 제공한다.
- React Hook Form 공식 문서는 외부 controlled 렌더 값의 반응형 구독에 `useWatch({ control })`을 제공한다.
- 기존 route 테스트는 필드마다 완성 문자열을 한 번에 dispatch해 실제 타이핑 누적을 검증하지 않는다.
- route의 `onSuccess`는 응답 `{ id }`를 그대로 `goToDetail("proposal", id)`에 전달한다.
- MSW proposal POST는 ID를 `proposal-created`로 고정하고 같은 ID로 `contentItems`에 저장한다.

## 추가 발견

- `useCitizenParticipationMutations.ts:91-96`의 discussion `onSuccess`에 두 번째 invalidation이 잘못 배치돼 Vite parser가 실패한다.
- 이 구문 오류 때문에 현재 proposal route test suite가 0개 테스트로 중단된다.

## 가설 판정

| 가설 | 현재 상태 | 근거 또는 다음 검증 |
| --- | --- | --- |
| form 값 구독 누락 | 유력, 미확정 | 문자 단위 RED 테스트로 확인 필요 |
| HeroUI event 계약 오류 | 미확정 | 구독 수정 전후 event/DOM 값으로 구분 |
| route/form reset | 가능성 낮음 | 현재 경로에 reset 호출 없음 |
| 고정 생성 ID | 확정 | MSW source에 literal `proposal-created` 존재 |

## 구현 후 판정

- StrictMode jsdom에서는 기존 `watch()`도 문자 단위 입력을 통과해 브라우저 증상을 그대로 재현하지 못했다.
- 사용자 런타임 관찰과 React Hook Form 공식 controlled subscription 권고에 따라 `useWatch({ control })`로 렌더 구독을 명시했다.
- HeroUI v3의 `onChange`는 전체 event value를 전달하므로 shared UI adapter는 변경하지 않았다.
- fixed ID 문제는 두 번 생성 시 동일 ID가 반환되는 RED 테스트로 재현됐다.

## 제약

- production UI 파일은 수정하지 않는다.
- 프로젝트 정책에 따라 브라우저 자동화와 시각 QA는 수행하지 않는다.
- 애플리케이션 수정은 사용자 승인 뒤 진행한다.
