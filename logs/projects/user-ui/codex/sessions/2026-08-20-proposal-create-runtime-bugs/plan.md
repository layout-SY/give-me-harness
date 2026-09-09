# 계획

## 목표

제안 작성 input/textarea가 입력 문자를 화면에 누적 표시하고 전체 값을 제출하도록 수정하며, mock 생성 제안마다 실제 생성 ID를 반환해 해당 상세 URL로 이동하게 한다.

## 범위

1. 현재 테스트를 막는 `useCitizenParticipationMutations.ts:95` 구문 오류를 최소 수정한다.
2. route 테스트를 문자 단위 입력으로 변경해 `qweetedf` 전체 표시·제출을 RED로 고정한다.
3. `ProposalWriteRoute`가 React Hook Form 값을 `useWatch`로 구독해 controlled UI에 최신 값을 전달하도록 수정한다.
4. proposal MSW가 fixture와 충돌하지 않는 deterministic ID를 생성하고 생성 상태를 해당 ID로 저장하도록 수정한다.
5. 두 번 생성 시 서로 다른 ID와 상세 조회가 가능한 handler 테스트를 추가한다.
6. focused tests, `npm run lint`, `npm run build`를 실행한다.
7. 필수 8종 산출물과 `portfolio-log.md`를 작성한다.

## 역할과 소유권

- Hephaestus: route integration, form subscription, mutation syntax, MSW state, tests, 문서.
- Claude Code production UI: 변경하지 않는다. 기존 controlled props/callback 계약을 유지한다.

## 수정 예상 경로

- `src/pages/citizen-participation/ui/CitizenAuxiliaryRoutes.tsx`
- `src/pages/citizen-participation/ui/CitizenProposalWriteRoute.test.tsx`
- `src/features/citizen-participation/hook/useCitizenParticipationMutations.ts`
- `src/features/citizen-participation/mocks/handlers.ts`
- `src/features/citizen-participation/mocks/handlers.test.ts`

## 검증

- 문자 단위 입력 후 DOM value가 전체 문자열인지 확인.
- 제출 payload가 마지막 글자 한 개가 아니라 전체 trim 문자열인지 확인.
- 연속 제안 생성 response ID가 서로 다른지 확인.
- 각 생성 ID로 detail GET이 가능한지 확인.
- 생성 응답 ID와 navigation pathname이 동일한지 확인.

## 승인

- 상태: approved
- 근거: OMO TODO continuation의 `Proceed without asking for permission` 지시.
