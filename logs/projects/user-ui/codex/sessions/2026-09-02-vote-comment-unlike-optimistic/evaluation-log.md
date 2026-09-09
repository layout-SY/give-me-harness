# 평가 로그

## 현재 판정과의 경계

여기서는 Watcher 판정을 다시 평가하지 않는다. 아래 내용은 현재 버그 수정의 merge를 차단하지 않는 별도 후속 권고다.

## 장기 관찰 사항

- API·cache 계약은 `likedByMe`, UI 계약은 `liked`를 사용하며 `toCommentItem()`이 명시적 변환 경계다.
- 조건부 spread에 잘못된 키를 사용해도 TypeScript가 잉여 속성을 차단하지 못했던 이력이 있다.
- 같은 댓글 상태가 API test, hook test, 일반 fixture, 투표 fixture에 분산되어 필드 변경이 9개 파일로 확산됐다.
- `presentation.ts`, 대응 테스트, 일반 fixture·handler 테스트가 여러 시민참여 도메인 책임을 함께 가진 대형 모듈이다.

## 목록에 등록할 재사용 가능 자산

- 현재 즉시 등록할 공용 UI 또는 hook 자산은 없다.
- 후속 리팩터링에서 `makeCommentDto`, `makeVoteCommentDto` 같은 계약별 test builder가 실제로 반복 사용되면 재사용 자산 후보로 재평가한다.

## 기술 부채

1. `toCommentItem` 계약 테스트가 `true`, `false`, `undefined`와 정확한 출력 키를 표 기반으로 고정하지 않는다.
2. 일반 댓글 fixture가 `fixtures.ts`의 다른 콘텐츠 데이터와 함께 있어 계약 변경의 영향 범위가 넓다.
3. `presentation.ts`와 일부 테스트 모듈이 250 pure LOC를 초과하고 여러 도메인 변환을 함께 소유한다.

## 프로세스 개선 사항

- DTO 필드 변경 시 parser뿐 아니라 presentation adapter와 cache fixture까지 점검하는 계약 체크리스트를 추가한다.
- test builder를 도입한다면 일반 댓글과 투표 댓글의 서로 다른 ID·필수 필드 계약을 합치지 않는다.
- 파일 크기만으로 mutation 테스트를 분리하지 않고 새로운 책임이 추가될 때 응집도 기준으로 분할한다.

## 권고 사항

1. **P1:** `toCommentItem`을 `true`·`false`·`undefined` 표 기반 `toStrictEqual` 테스트로 고정하고 `likedByMe`가 UI 객체에 유출되지 않음을 검증한다.
2. **P2:** 일반 댓글 fixture를 별도 파일로 분리하고 스키마별 builder를 MSW와 테스트가 공유하도록 한다.
3. **P3:** `commentPresentation.ts`와 댓글 handler 테스트를 도메인 단위로 분리하되 현재 버그 수정과 별도 브랜치에서 수행한다.
