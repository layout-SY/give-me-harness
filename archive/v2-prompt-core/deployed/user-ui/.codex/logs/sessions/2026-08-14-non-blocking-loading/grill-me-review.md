# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 원인 | 요청이 진행되는 동안 어떤 요소가 입력 대상이 되는가? | 투명한 100% 크기 `.loading-component`가 높은 z-index로 입력 영역을 덮는다. | `loading.css`, `loading.custom.css` | 비동기 API 자체와 UI hit-testing을 분리한다. |
| 범위 | 같은 동작을 공유하는 화면은 어디인가? | 시민참여 목록 5개 화면이다. | `Loading` import/caller 검색 | 공용 seam 한 곳에서 수정한다. |
| 상호작용 | 로딩 표시 자체가 클릭을 받아야 하는가? | 현재 spinner만 렌더하며 클릭 계약이 없다. | `loading.tsx` | pointer 입력을 하위 UI로 통과시킨다. |
| 회귀 | 테스트 코드를 유지할 수 있는가? | 조사 시간이 5분을 넘어 사용자 지시에 따라 폐기했다. | 사용자 최신 지시 | 일회성 CSSOM 실행과 정적 검증을 기록한다. |
| 탭 완결성 | 설문 항목 추가만으로 선택 흐름이 완성되는가? | 아니다. route map과 설문 화면의 활성 탭 callback도 필요하다. | `ServiceTabs`, `useCitizenRouteState`, `SurveyListPage`, `CitizenListRoutes` | 네 경계를 함께 연결한다. |
| 재사용 | 설문 전용 탭을 새로 만들어야 하는가? | 아니다. 기존 제어형 `src/shared/ui/tabs`가 요구를 충족한다. | `tabs.tsx`, `tabs.css` | 기존 어댑터를 재사용한다. |

## 결론

공용 overlay의 포인터 이벤트만 제거하는 변경은 문제 원인과 일치하며 시각 및 데이터 요청 계약을 변경하지 않는다. 설문조사 탭은 기존 탭·route 계약을 확장해 선택, 이동, 활성 상태를 모두 충족한다.
