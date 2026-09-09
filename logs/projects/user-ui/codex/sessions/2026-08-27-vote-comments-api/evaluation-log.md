# 평가 로그

## 현재 판정과의 경계

여기서는 Watcher 판정을 다시 평가하지 않는다. 아래 항목은 모두 현재 작업 완료를 막지 않는 장기 관찰이다.

## 장기 관찰 사항

- `parseVoteCommentList`의 transport-to-view 정규화 경계는 후속 API 전환에도 재사용할 수 있다.
- vote 댓글 schema, sort vocabulary, query DTO를 한 모듈에 둔 구조는 API·parser·mock의 단일 계약 기반이다.
- query 전체를 cache key에 포함한 구조는 다른 목록 query에도 적용 가능한 패턴이다.

## 목록에 등록할 재사용 가능 자산

- `api/http/citizenParticipation.parser.ts`의 원본 페이지 응답을 기존 화면 페이지 모델로 변환하는 parser 패턴
- `mocks/voteCommentFixtures.ts`의 Zod schema 기반 fixture 작성 방식
- `api/http/voteComments.api.test.ts`의 Axios URL·query·parser 통합 검증 방식

## 기술 부채

- 공용 `CommentDto`의 optional 좋아요 필드는 기능 지원 여부를 타입만으로 완전히 구분하지 못한다.
- 콘텐츠별 댓글 client·parser 분기가 hook, API, mock에 분산되어 있다.
- `mocks/commentHandlers.ts`가 일반 댓글과 vote 댓글의 서로 다른 store·계약을 함께 소유한다.
- `useCitizenCommentsQuery`의 client 선택과 query key를 직접 검증하는 hook 단위 테스트는 없다.

## 프로세스 개선 사항

- 댓글 계약 변경 시 API·parser·hook·query key·mock을 하나의 점검 묶음으로 유지한다.
- 독립 API 계약 테스트 파일을 사용해 대형 기존 테스트 파일의 추가 성장을 피한다.
- fixture 생성 시 DTO schema parse를 거쳐 backend 계약 이탈을 조기에 발견한다.

## 권고 사항

- 좋아요 지원 댓글과 미지원 댓글을 capability 또는 식별 가능한 도메인 모델로 분리할 시점을 검토한다.
- vote 관련 mock 분기가 더 증가하면 vote 전용 handler/store 모듈로 분리한다.
- 정렬 결과, parser 실패, hook dispatch에 대한 최소 회귀 테스트를 후속 작업 후보로 둔다.

## 추가 장기 평가 — nullable 제안 작성자

### 재사용 가능한 자산

- 외부 nullable 계약을 Zod와 DTO에 보존하고 presentation에서 표시값으로 변환하는 경계 패턴
- parser 계약 테스트와 presentation 정책 테스트를 분리하는 이중 회귀 구조
- backend 상태와 UI 상태 어휘 차이를 명시적 adapter로 처리하는 방식

### 기술 부채

- `proposal.dto.ts`는 Zod schema와 수동 DTO 타입에 nullability를 중복 선언하므로 장기적으로 `z.infer` 또는 타입 일치성 검증을 검토한다.
- `CitizenListRoutes.tsx`는 query error를 빈 배열로 바꾸고 `ProposalListPage`는 이를 정상 `NoResults`로 표시한다.
- UI 미지원 상태는 `null` 결과로 조용히 제외되어 운영 관측성이 부족하다.

### 프로세스 개선

- 실제 backend nullable·optional 사례를 계약 fixture로 보존한다.
- parser → presentation → route → build/lint → 전체 baseline 순서의 검증 증거를 표준화한다.
- 전체 suite의 기존 meeting 실패 2건은 이름과 baseline을 계속 명시해 신규 실패 증가 여부를 구분한다.

### 비차단 후속 권고

1. production UI 별도 작업에서 정상 빈 결과와 query error를 분리한다.
2. `CitizenDataRoutes.test.tsx`에 `author:null` MSW route 통합 회귀를 추가한다.
3. 네 가지 backend 상태와 nullable 작성자를 정식 fixture로 승격한다.
4. 상태 제외 관측성과 DTO 타입 파생 전략을 별도 검토한다.
