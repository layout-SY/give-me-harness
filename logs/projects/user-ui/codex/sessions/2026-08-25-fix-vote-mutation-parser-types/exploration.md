# 탐색

## 요청

`useCitizenParticipationMutations.ts` 51–54행 `Unsafe argument of type error typed`를 고치고 검증한 뒤 짧게 설명하라고 했다.

## 대상 관련 사실

- 오류는 `.then(parseVoteResponse)`에 있다. `parseVoteResponse`가 `error` 유형으로 읽힌다.
- 생성 mutation은 같은 이유로 parser `.then`을 빼고 `postProposal` 안에서 Location을 파싱했다.
- `parseVoteResponse`는 `citizenParticipation.parser`에 있고, 이 모듈은 모든 DTO 스키마를 한곳에 모은다. mutations는 client(모든 API)와 parser를 같이 가져와 순환 그래프가 된다.
- 토론 mutation은 parser가 아니라 `discussion.dto`의 스키마를 직접 `parse`한다.

## 불러온 스킬

- `policy/coding-convention`, `policy/type-definition`, `policy/documentation`, `policy/portfolio`, `policy/harness`

## `src/shared/ui/`의 재사용 가능 자산

없음.

## 제약 조건 및 미확인 사항

- POST 성공 JSON은 기존 `{ id, completed, choice }`를 유지한다.

## 결론

훅에서 god parser를 `.then`하지 않고, `vote.api.ts`가 `voteResponseSchema`로 파싱한다.
