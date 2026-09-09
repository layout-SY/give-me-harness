# 계획

## 목표

시민참여 route 조합 책임을 `pages` 레이어로 이동하고 `app → pages → features → shared` 의존 방향을 만든다. 기존 URL, props, API 요청, 상태 전이, UI 마크업과 CSS는 변경하지 않는다.

## 범위

- `features/citizen-participation/integration`의 route wrapper 5개와 route state hook 이동
- `features/citizen-participation/model/presentation.ts`와 직접 테스트를 pages model로 이동
- `features/citizen-participation/index.ts`를 pages가 소비할 feature 공개 API로 재구성
- `pages/citizen-participation/index.ts` 공개 API 추가
- `app/routing.ts`의 시민참여 route import를 pages로 전환
- `shared/mocks`의 app bootstrap을 `app/mocks`로 이동하고 feature mock 전용 공개 API를 추가

## 제외 사항

- `entities` 레이어 도입
- 시민참여 API, query/mutation 구현, feature-local mock handler/fixture, layout/parts/report 이동
- auth 및 meeting page 경계 변경
- production UI 마크업·스타일·접근성 계약 변경
- 사용자/다른 세션 변경인 `src/features/auth/hook/useSignInMutation.ts`, `src/shared/api/common/dto.ts`, `.opencode/settings.json`

## 제약 조건

- route component 이름 13개와 route table 순서를 유지한다.
- feature가 pages를 import하거나 re-export하지 않는다.
- pages가 feature 내부 deep path 대신 feature public API를 사용한다.
- 새 compatibility shim이나 speculative abstraction을 추가하지 않는다.
- 브라우저 자동화와 시각 QA를 수행하지 않는다.

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 탐색 | Hephaestus + Explore | `refactor`, `programming`, `reference-index` | 이동 codemap과 영향 범위 |
| 구조 이동 | Hephaestus | `policy-refactoring`, `policy-coding-convention` | pages slice 생성과 동작 보존 |
| 공개 API | Hephaestus | `policy-abstraction-strategy`, `programming` | 단방향 layer import |
| 검토 | Watcher 문서 판정 | `policy-review-checklist` | PASS/FAIL 근거 |
| 평가 | Evaluator 문서 기록 | `policy-documentation` | 후속 auth/meeting/entities 분리 |

## 검증

- baseline 및 이동 후 focused Vitest 7 files / 19 tests
- `npm run build`
- `npm run lint`
- stale integration import와 feature model의 UI import 검색
- production bundle 및 route table에서 기존 시민참여 route 유지 확인
- production preview에서 대표 시민참여 URL의 SPA 응답 확인

## 위험 요소 및 결정 사항

- route test는 path 배열을 검증하지만 모든 route component를 실제 렌더하지 않는다. build의 module resolution과 App test를 함께 사용한다.
- page UI 파일 자체 이동은 import 폭발과 production UI 소유권 변경을 키우므로 이번 단계에서 제외한다.
- 구현 후 `shared/mocks/browser.ts`가 feature mock handler를 import하는 상향 의존을 발견해 app bootstrap만 `app/mocks`로 이동했다. feature handler와 fixture는 기존 feature 소유권을 유지한다.
- Plan agent는 외부 API 크레딧 부족으로 실행되지 않아 Codegraph와 5개 Explore 결과로 직접 계획을 확정했다.

## 승인

- 상태: approved
- 근거: 사용자의 `오케이. 리팩토링 작업 시작.`
