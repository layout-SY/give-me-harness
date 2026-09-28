# 탐색 결과

남은 39건은 API의 any 30건, 빈 업로드 interface 4건, 이벤트 callback Function 5건이다. 현 소스·기존 테스트·Git 이력을 조사했다. 전체 서버 명세와 활성 호출부가 없는 타입을 새 필드로 추정할 필요 없이 unknown 반환 경계로 제한할 수 있다.

## 적용 스킬

중앙 snapshot의 task-role-routing, git-branch-strategy, skill-index, coding-convention, type-definition, data-fetch-layer, recipe/data-dto, implementation-quality, abstraction-strategy, documentation, reference/custom-hooks/use-pub-sub를 읽었다.

## 재사용 근거

- 이벤트 attendance·roulette DTO에 목록 전체·상세 전체·보상 항목 타입이 있다. attendance 개발 fixture도 기존 항목 DTO 배열이다.
- admin 상세, item 상세, sales summary에 기존 DTO가 있다. 목록 항목 DTO만 있는 경우 전체 envelope와 pagination을 새로 단정하지 않는다.
- `dashboard.dto.ts`는 비어 있고 dashboard API 호출부는 없다. 기기별 합산 메서드만 세 개의 count 필드를 직접 사용한다.
- `axios-instance.ts`의 response interceptor는 res.data를 반환한다. 인접 item-category·profile API가 Axios 두 번째 제네릭에 `{ data: DTO }`를 지정하는 패턴이다.
- `dao/api/proposal/proposal.api.ts`의 multipart 업로드와 `features/image-manager/ui/hooks/useImageUpload.tsx`는 FormData를 사용한다. 필드명은 각 기능에 맡긴다.
- PubSub 5개 이벤트의 활성 발행·구독은 없다. 사용자 선택 UI에는 주석 처리된 구독만 있다. domain import를 shared에 추가하거나 미확인 signature를 추정하지 않는다.
- 기존 `tests/item-category-contract.test.mjs`는 tsx의 tsImport와 Node test runner로 전송·반환 보존을 검사한다. 새 프레임워크 없이 같은 방식과 설치된 TypeScript API를 사용할 수 있다.

## 결정

확인된 DTO 연결과 미확인 데이터의 unknown 반환을 구분한다. unknown 값의 필드 사용 및 미확인 콜백의 인자 전달이 타입 검사에서 거부되는지 확인한다. lint disable, 암묵적 any, as 단언으로 검사만 숨기지 않는다. UI 소스와 요청 endpoint·payload·응답 데이터의 런타임 전달은 유지한다.
