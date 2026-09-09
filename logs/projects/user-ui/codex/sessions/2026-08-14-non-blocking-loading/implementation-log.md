# 구현 로그

## 승인된 범위

공용 로딩 overlay가 API 대기 중 하위 UI 입력을 막지 않도록 최소 CSS 수정 후 검증한다.
시민참여 서비스 탭에 설문조사를 추가하고 기존 설문 목록 navigation을 연결한다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `src/shared/ui/loading/loading.css` | `.loading-component`에 `pointer-events: none` 추가 | spinner 표시는 유지하면서 pointer hit target에서 제외 |
| `src/shared/ui/loading/loading.test.tsx` | CSSOM 회귀 테스트를 작성했다가 삭제 | 사용자 지정 5분 제한 준수 |
| `src/features/citizen-participation/ui/layout/ServiceTabs.tsx` | `survey` value와 `설문조사` 항목 추가 | 공용 서비스 탭에서 설문 선택 가능 |
| `src/features/citizen-participation/integration/useCitizenRouteState.ts` | `survey`를 기존 surveys route에 매핑 | 탭 선택 시 `/surveys` 이동 |
| `src/features/citizen-participation/ui/survey/SurveyListPage.tsx` | 설문 활성 ServiceTabs와 callback prop 추가 | 설문 화면에서 활성 탭 유지 |
| `src/features/citizen-participation/integration/CitizenListRoutes.tsx` | `navigation.goToService` 전달 | 설문 화면의 다른 서비스 탭 이동 연결 |

## 결정 사항

- 호출부 5곳을 각각 변경하지 않고 공용 로딩 seam을 수정했다.
- 시각 속성, z-index, 크기, spinner 마크업은 변경하지 않았다.
- Vitest CSS import가 빈 문자열로 변환되는 테스트 하네스 문제를 확인했으나 설정 변경은 범위에서 제외했다.
- 신규 route를 만들지 않고 기존 `citizenParticipationRoutes.surveys`를 재사용했다.
- 현지화 인프라가 없어 인접 UI와 같은 한국어 literal을 유지했다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| 실제 CSS 기반 jsdom CSSOM 확인 | PASS: `loading overlay pointer-events: none` |
| `npm run build` | PASS: TypeScript 및 Vite production build 완료, 기존 500kB 초과 chunk 경고 유지 |
| `npm run lint` | PASS |
| `npx vitest run "src/shared/ui/tabs/tabs.test.tsx" "src/app/routing.test.ts"` | PASS: 2 files, 2 tests |
| production bundle 문자열 확인 | PASS: `설문조사`와 `/surveys` 포함 |

## Watcher 인계

- 공용 로딩이 pointer hit target에서 제외되는지 확인한다.
- 기존 spinner 표시와 z-index 계약이 유지되는지 확인한다.
- 테스트 코드가 남아 있지 않은지 확인한다.
- 설문 탭 선택이 기존 surveys route로 매핑되고 설문 목록에서 활성 상태를 유지하는지 확인한다.
