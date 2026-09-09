# 탐색

## 요청

`proposal.api.ts` 29–32행 `Unsafe assignment of an error typed value`를 고치고, 같은 오류가 반복되는 근본 원인을 설명하라고 했다.

## 대상 관련 사실

- CLI `npx eslint proposal.api.ts`는 통과했다. ReadLints/IDE는 `request.background`/`content`/`expectedEffect`/`referenceCase`만 오류로 보고 `title`은 통과했다.
- 옛 요청 DTO는 `{ title, body, detail, effect, reference? }`였다. `title`만 있는 유형으로 읽히면 새 필드 접근이 `error`가 된다.
- `@typescript-eslint`는 `parserOptions.projectService: true`로 프로젝트 전체 프로그램을 쓴다. `error` 유형은 모듈 순환으로 심볼이 아직 끝나지 않았을 때 들어간다.
- `index.ts` barrel은 UI·훅·parser·DTO를 한 파일에서 재export한다. pages와 테스트가 barrel에서 훅/parser를 가져오면 생성 API까지 같은 그래프에 묶인다.
- 같은 증상은 직전에 `VoteDetailRoute`의 barrel import에서도 났다.

## 불러온 스킬

- `policy/coding-convention`, `policy/type-definition`, `policy/documentation`, `policy/portfolio`, `policy/harness`

## `src/shared/ui/`의 재사용 가능 자산

없음. 타입/import 수정이다.

## 제약 조건 및 미확인 사항

- `useVoteMutation`의 `.then(parseVoteResponse)`는 같은 parser 순환이 IDE에 남을 수 있다. 이번 오류 위치는 생성 POST다.

## 결론

할당문 단언이 아니라, 생성 DTO를 순환 그래프 밖 모듈로 두고 barrel 소비를 깊은 경로로 바꿔 `CreateProposalRequestDto`가 완성된 유형으로 읽히게 한다.
