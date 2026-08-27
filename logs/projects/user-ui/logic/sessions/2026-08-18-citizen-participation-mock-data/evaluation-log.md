# 평가 로그

## 현재 판정과의 경계

여기서는 Watcher PASS를 다시 평가하지 않는다. 아래는 장기 backend 연동과 유지보수 관점의 관찰 사항이다.

## 장기 관찰 사항

- 현재 generic content DTO의 optional metadata는 mock 기반 UI 연결에 적합하지만 실제 backend 계약이 확정되면 content type별 discriminated response로 분리할 수 있다.
- 개발 환경 MSW 기본 활성화는 로컬 진입 비용을 낮추며 `VITE_ENABLE_MSW=false`로 실제 API 개발을 지원한다.
- content별 comment fixture는 ID 기반이며 mutation 후 fixture state 변경까지는 모델링하지 않는다.

## 목록에 등록할 재사용 가능 자산

- 신규 공용 UI나 shared hook을 만들지 않았으므로 재사용 자산 목록 추가 대상은 없다.
- `src/features/citizen-participation/testing.ts`는 기존 feature test/mocking 공개 경계를 계속 사용한다.

## 기술 부채

- `presentation.ts` 230 pure LOC와 `presentation.test.ts` 215 pure LOC는 경고 구간이다.
- 실제 backend가 type-specific metadata를 다른 endpoint로 제공하면 DTO와 query를 재구성해야 한다.
- MSW mutation은 성공 응답만 반환하며 후속 목록/detail state를 변경하지 않는다.

## 프로세스 개선 사항

- UI 임시값 조사는 component default 존재 여부와 production caller의 prop 공급 여부를 분리해 판단한다.
- route render test는 Query cache가 아니라 DOM mutation을 완료 신호로 사용해 React commit 타이밍 flake를 방지한다.

## 권고 사항

- 실제 backend OpenAPI가 확정되면 optional generic metadata를 content type별 DTO로 마이그레이션한다.
- proposal 작성과 comment/vote mutation의 optimistic/refetch 흐름은 별도 승인 작업으로 구현한다.
