# 계획

## 목표

외부 API 요청 대기 중 공용 로딩 표시가 다른 UI의 포인터 입력을 막지 않도록 한다.
시민참여 `ServiceTabs`에 설문조사를 추가하고 기존 설문 목록 route와 연결한다.

## 범위

- `src/shared/ui/loading/loading.css`의 입력 차단 동작 수정
- `ServiceTabValue`, 서비스 route map, 설문 목록의 활성 탭과 callback 연결
- 실제 CSS 계산값을 이용한 일회성 동작 확인
- `npm run build`, `npm run lint` 정적 검증

## 제외 사항

- API 요청 구현과 TanStack Query 상태 전이 변경
- 로딩 컴포넌트의 시각 디자인 변경
- 신규 설문 route 또는 API 추가
- 브라우저 자동화, 이미지 캡처, 시각 QA
- 5분을 초과한 테스트 코드 유지

## 제약 조건

- 기존 `Loading` 호출부 5곳과 디자인 토큰을 유지한다.
- 기존 `src/shared/ui/tabs` 어댑터와 `/surveys` route를 재사용한다.
- 사용자의 지시에 따라 테스트 코드 작업이 5분을 넘으면 해당 코드를 폐기한다.
- unrelated worktree 변경을 수정하거나 되돌리지 않는다.

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 탐색 | Hephaestus | `debugging`, `reference-components` | 입력 차단 원인과 영향 범위 확인 |
| 구현 | Hephaestus | `project-ui`, `policy-styles`, `programming` | 시각 변화 없는 최소 CSS 수정 |
| 설문 탭 연결 | Hephaestus | `policy-publishing`, `policy-type-definition`, `recipe-i18n` | typed 탭 선택과 `/surveys` 이동 |
| 검토 | Watcher 문서 판정 | `policy-review-checklist` | 현재 변경 PASS/FAIL 기록 |
| 평가 | Evaluator 문서 기록 | `policy-documentation` | 장기 개선 사항 분리 |

## 검증

- 실제 `loading.css`를 jsdom CSSOM에 주입해 `pointer-events` 계산값 확인
- `npm run build`
- `npm run lint`
- `npx vitest run "src/shared/ui/tabs/tabs.test.tsx" "src/app/routing.test.ts"`

## 위험 요소 및 결정 사항

- `pointer-events: none`은 로딩 표시 자체의 클릭을 허용하지 않는다. 현재 컴포넌트는 spinner만 렌더하며 상호작용 계약이 없으므로 허용한다.
- jsdom은 실제 브라우저 hit-testing을 제공하지 않는다. 프로젝트 규칙상 브라우저 자동화는 수행하지 않고 CSSOM 계약과 정적 검증으로 제한한다.
- 현지화 인프라가 없어 기존 시민참여 UI와 같은 한국어 literal을 사용하며 새 의존성을 도입하지 않는다.

## 승인

- 상태: approved
- 근거: 사용자의 `작업 이어서 진행하되` 지시
- 추가 조건: 테스트 코드 작업이 5분 이상이면 해당 테스트 코드를 폐기
