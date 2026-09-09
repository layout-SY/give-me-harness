# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 역할 경계 | View 파일에 API 호출·검증·상태 전이가 들어갔는가 | 없다 | 세 View 모두 `~/entities/news`의 hook을 import하지 않고 타입만 사용한다 | UI 경계 유지 |
| 서버 값 보존 | 목록 집계·순서를 화면에서 다시 계산하는가 | 하지 않는다 | `itemCount`·`pageCount`·`pinnedItemCount`를 controller 값 그대로 `Table`과 설명 문구에 전달한다 | 서버 값 그대로 표시 |
| 실패 표현 | 조회 실패가 빈 목록으로 보일 수 있는가 | 아니다 | `error.isVisible`이면 표 대신 오류 문구와 다시 조회 버튼을 렌더한다 | 실패와 빈 결과 분리 |
| 검색 계약 | `by`와 `keyword`가 한쪽만 남을 수 있는가 | View에서는 발생하지 않는다 | 검색 범위 드롭다운에 "전체"가 없고 해제 시 기존 값을 유지한다. 빈 키워드 처리는 controller 책임으로 명시했다 | 쌍 유지, 전송 판단은 Logic |
| 미지원 필드 | news 계약에 없는 입력을 저장 가능한 것처럼 보여주는가 | 아니다 | 노출 기간·메인 노출·작성자 입력을 넣지 않았다 | 미지원 필드 미표시 |
| 접근성 | 조작 요소에 접근 가능한 이름이 있는가 | 있다 | 필터는 `FilterBar`의 `label`+`htmlFor`, 칩 그룹은 `ariaLabel`, 오류 문구는 `role="alert"` | 칩 그룹 채택 |
| 재사용 | 새 공용 추상화를 만들었는가 | 만들지 않았다 | shared 승격 없이 기존 컴포넌트를 조합했고 삭제 팝업은 로컬에 두었다 | 로컬 구현 우선 |
| 상태 색 | 상태 배지 색이 실제 지원 값인가 | 그렇다 | `StatusBadgeColor` 정의를 확인해 `gray/green/red` 초안을 `neutral/positive/warning`으로 교정했다 | 타입 정의 확인 후 교정 |
| 삭제 위험 | 삭제가 확인 없이 실행될 수 있는가 | 아니다 | 삭제 버튼은 팝업만 열고 확정은 `onConfirmDelete`가 담당하며 처리 중 버튼을 잠근다 | 확인 팝업 유지 |
| 범위 | 승인되지 않은 파일을 수정했는가 | 하지 않았다 | 변경은 모두 `src/pages/cp-news` 아래에 있다 | scope 준수 |

## 결론

UI 역할 경계, 서버 값 보존, 실패 표현, 접근성, scope 준수 항목에서 수정이 필요한 문제를 찾지 못했다. 남은 제한은 controller 부재로 인한 실제 렌더 미확인이며, 이는 Logic 통합 단계에서 확인해야 한다.
