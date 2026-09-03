# 탐색

## 요청

외부 API 통신 중 다른 UI 작업이 막히는 원인을 찾고 비동기 요청 대기 중에도 상호작용할 수 있게 한다.
추가 요청으로 시민참여 서비스 탭에 `설문조사`를 포함한다.

## 대상 관련 사실

- `src/shared/api/api-client.ts`의 Axios 메서드와 회의 API의 `fetch`는 모두 Promise 기반 비동기다.
- `src/shared/ui/loading/loading.css`는 투명한 absolute 100% overlay를 만든다.
- `src/shared/ui/loading/loading.custom.css`는 overlay에 `z-index: 900`을 적용한다.
- 기존 CSS에는 포인터 입력 통과 규칙이 없어 overlay가 하위 UI의 pointer hit target을 가린다.
- `ProposalListPage`, `VoteListPage`, `DiscussionListPage`, `PolicyListPage`, `SurveyListPage`가 API 초기 대기 중 `Loading`을 렌더한다.
- `ServiceTabs`는 `all`, `proposal`, `vote`, `discussion`, `policy`만 제공했지만 기존 `citizenParticipationRoutes.surveys`와 `SurveyListRoute`가 이미 존재했다.
- 기존 설문 목록에는 `ServiceTabs`와 `onServiceTabChange` callback이 없어서 탭 항목만 추가하면 설문 화면에서 활성 탭을 유지할 수 없었다.

## 불러온 스킬

- `debugging`
- `frontend`
- `project-ui`
- `policy-styles`
- `policy-documentation`
- `policy-harness`
- `reference-components`
- `programming`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| `src/shared/ui/loading` | 재사용 및 공용 seam 수정 | 5개 목록 화면이 동일 컴포넌트를 사용하므로 호출부별 수정이 불필요하다. |
| `src/shared/ui/button` | 변경하지 않음 | 개별 제출 버튼의 pending 상태만 담당하며 전체 화면 차단 원인이 아니다. |
| `src/shared/ui/dialog` | 변경하지 않음 | 오류 대화 상자만 담당하며 정상 pending overlay와 무관하다. |
| `src/shared/ui/tabs` | 재사용 | 제어형 value/onChange와 접근 가능한 label 계약이 이미 존재한다. |

## 제약 조건 및 미확인 사항

- 사용자에게서 구체적인 재현 페이지는 제공되지 않았으나 코드상 동일 현상은 시민참여 목록 5개 화면에 공통이다.
- 실제 브라우저 hit-testing은 프로젝트 규칙상 자동화하지 않는다.
- CSS 회귀 테스트는 Vitest의 CSS import 비활성화 설정 때문에 조사 시간이 5분을 넘었고, 사용자 지시에 따라 테스트 파일을 폐기했다.

## 결론

네트워크 호출은 비동기이며, UI 차단의 직접 원인은 투명한 전체 크기 로딩 overlay의 포인터 이벤트 수신이다. 공용 `.loading-component`에 `pointer-events: none`을 적용하는 것이 가장 작은 root fix다.
설문 탭은 기존 typed value와 route map을 확장하고 `SurveyListPage`에서 같은 탭을 렌더하는 방식이 완전한 최소 변경이다.
