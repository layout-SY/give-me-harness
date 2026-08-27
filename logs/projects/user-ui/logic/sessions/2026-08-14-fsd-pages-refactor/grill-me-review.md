# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 목표 | 변경 후 route 조합 책임은 어느 레이어가 소유하는가? | pages가 소유한다. | `src/pages/citizen-participation/ui/`, `src/app/routing.ts` | app은 pages 공개 API만 소비해야 한다. |
| 의존 방향 | 하위 레이어가 상위 레이어를 import하는 경로가 남아 있는가? | 검사 범위에서 없다. | 상향 import 검사 통과 | `app → pages → features → shared`를 유지한다. |
| 동작 보존 | 기존 시민참여 route와 표시 변환이 유지되는가? | 유지된다. | routing test, presentation test, build, preview HTTP 200 | URL·API·props 계약을 바꾸지 않는다. |
| 공개 API | pages가 feature 내부 경로를 직접 소비하는가? | 소비하지 않는다. | pages import와 feature `index.ts` | feature public API를 경계로 사용한다. |
| mock 경계 | MSW 앱 bootstrap의 소유 위치가 적절한가? | app이 소유한다. | `src/app/mocks`, `src/main.tsx` | feature handler는 전용 testing API로 노출한다. |
| 범위 | production UI 또는 unrelated 파일을 수정했는가? | 수정하지 않았다. | 변경 경로와 git status 대조 | 별도 세션 변경은 보존한다. |

## 결론

중립 질문 기준으로 승인된 구조 목표와 동작 보존 조건을 충족한다. 전체 suite의 auth·meeting 실패와 governance ignore 실패는 이번 시민참여 변경 경로 밖이며 별도 조치가 필요하다.
