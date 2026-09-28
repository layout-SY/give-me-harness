# Logic 타입·lint 정리 계획

- 역할: `logic` / 산출물 책임: `owner`
- 요청과 승인: UI handoff의 2차 인계에 있는 Logic 오류 정리. 사용자의 `그럼 너가 먼저 시작해`로 구현 승인, `명령 실행 승인`으로 작업 브랜치 생성 완료.
- 작업 위치: `/private/tmp/asan-metaverse-admin-ui-logic-type-lint-7ca0171b`
- 브랜치: `task/logic-type-lint`, 시작 HEAD `25c3ade2bcb26b72189945fd25921fcbb4b0e4b8`
- 직접 부모 및 병합 대상: `task/news-management-ui`. 상위는 `sy-main`. 사용자의 최신 교정이 handoff의 이전 분기·병합 제안보다 우선한다.
- 요청 명확성: `clear`, `can_proceed: true`. 역할·대상·순서·승인과 완료 기준이 확인됐다.

## 작업과 검증

1. Logic worktree의 `shared/lib`에서 debounce·throttle의 인자 추론, JWT 라이브러리의 기존 payload 타입, useApi의 cleanup 참조를 정리한다. 공개 호출 방식과 실행 동작을 유지한다.
2. `entities/event`의 enum 5개를 기존 news의 const 객체·동명 타입 패턴으로 변경하고 DAO의 미사용 import 2개를 제거한다.
3. `entities/*/api`에서 이미 명시된 응답 계약을 Axios interceptor 이후 반환 타입에 연결한다. 아이템 카테고리의 요청 필드 매핑은 원본 payload를 유지하며 명시적으로 작성한다.
4. 서버 응답·업로드 필드·이벤트 callback 인자를 확인할 수 없는 항목은 임의로 좁히지 않는다. 남은 경로와 필요한 근거를 기록한다.
5. 기존 Node 테스트 배치에 필요한 동작 확인을 추가하고, 전체 테스트·타입 검사·lint·build로 개선 및 잔여 오류를 확인한다. UI 담당 파일은 수정하지 않는다.
6. 실제 변경, 검증, 미완료 항목과 UI와의 계약 접점을 final-summary와 handoff에 남긴다. 커밋·병합은 결과를 구체적으로 보고한 후 별도 Git 승인을 따른다.

## 예상 diff와 경계

공용 hook·util, event DTO, DAO import, 기존 응답 타입이 있는 API 및 카테고리 요청 매핑, 필요한 테스트가 대상이다. UI의 `useFetchAdapter`와 `select-users`는 공용 계약의 소비자이므로 읽고 호환성을 확인한다. API 응답을 일괄적으로 추정하거나 lint 규칙을 완화하는 대안은 채택하지 않는다. 실서버 호출과 시각 QA는 수행하지 않는다.
