# 계획

## 목표

- `/ui-showcase`에서 `src/shared/ui`의 모든 렌더 가능한 공용 컴포넌트를 상태별로 확인하고 직접 조작할 수 있게 한다.
- 클릭, 입력, 선택, 페이지 이동, modal/dialog/popup, 파일 선택 등 동작 결과를 화면에서 즉시 확인할 수 있게 한다.
- 활성 전역 스타일을 320px 이상 모바일 viewport에서 안정적으로 동작하도록 정비하고 기존 회의 화면의 디자인 계약을 보존한다.

## 범위

1. `package.json`, `package-lock.json`
   - React 19와 호환되는 `react-router-dom@^7.18.2`를 npm으로 설치한다.
2. `src/main.tsx`, `src/App.tsx`
   - `main.tsx`에서 `BrowserRouter`를 한 번 제공한다.
   - `App.tsx`에서 `/`는 `MeetingPage`, `/ui-showcase`는 카탈로그 페이지로 선언한다.
   - 알 수 없는 경로는 `<Navigate to="/" replace />`로 복구하고, 카탈로그 내부 이동은 `Link`를 사용한다.
   - 기존 전역 overlay 호스트는 `Routes` 바깥에서 한 번만 마운트한다.
3. `src/features/shared-ui-showcase/`
   - `SharedUiShowcasePage`와 controls/forms, badges/feedback, navigation/data, overlays 섹션으로 모듈을 분리한다.
   - 제어형 state와 이벤트 결과 패널로 모든 상호작용의 성공 여부를 가시화한다.
   - Table은 accessor/custom/action/loading/empty/pagination을 포함한 typed fixture로 시연한다.
   - 비시각 export(`useFetchAdapter`, 타입/store, 빈 form barrel)는 제외 사유와 간접 검증 위치를 표시한다.
   - ImageModal용 같은 오리진 샘플 SVG 자산을 추가한다.
4. `src/index.css`
   - `box-sizing`, 문서/root 크기, 모바일 안전 최소 폭, 가로 overflow 방지, 글꼴 상속, 반응형 미디어, `focus-visible`, 긴 문자열 줄바꿈을 활성 전역 baseline으로 정의한다.
   - `100dvh`/`100svh` fallback을 사용하고 전역 고정 높이와 전체 focus outline 제거는 도입하지 않는다.
5. `src/features/shared-ui-showcase/ui/shared-ui-showcase.css`
   - 모바일 우선 단일 열, 44px 터치 대상, 스크롤 가능한 wide table 영역, 768px 이상 점진적 다열 배치를 적용한다.
   - `DESIGN.md` 토큰과 4px 간격 체계만 사용한다.
6. `DESIGN.md`
   - 공용 기본 요소 쇼케이스의 경로, 상태 harness, responsive 규칙을 Section 5에 기록한다.
   - “상시 라우트가 없음” 기술 부채를 해소된 상태로 갱신한다.
7. 세션 문서
   - 구현 후 `implementation-log.md`, `grill-me-review.md`, `review-log.md`, `evaluation-log.md`, `final-summary.md`를 템플릿에 맞춰 작성한다.

## 제외 사항

- Storybook 또는 별도 디자인 시스템 도구 도입
- 공용 컴포넌트 자체 API의 리팩터링
- 회의 API, Agora RTC, 인증 흐름 변경
- 현재 import되지 않는 `src/shared/assets/css/main.css` 및 legacy reset 전체 활성화
- 실제 외부 이미지, 비밀값, API 호출을 사용하는 시연

## 제약 조건

- 승인 전 애플리케이션 소스나 패키지 파일을 수정하지 않는다.
- `react-router-dom`은 v7 declarative mode만 사용하며 data router/framework mode로 범위를 확장하지 않는다.
- `DESIGN.md`의 색상, 타이포그래피, 4px 간격, 표면/모서리, 접근성 계약을 따른다.
- `any`, type assertion, non-null assertion, default export 신규 도입을 피하고 기존 import 별칭/폴더 경계를 따른다.
- 파일은 단일 책임으로 나누고 순수 코드 250 LOC를 넘기지 않는다.
- 공용 overlay host는 중복 마운트하지 않는다.
- 모든 interactive example은 접근 가능한 이름, 키보드 조작, 식별 가능한 포커스를 제공한다.

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 카탈로그 구조/fixture | Planner + Generator | `reference-components`, `policy-type-definition`, `policy-coding-convention` | 25개 렌더 표면과 비시각 export의 누락 없는 coverage matrix |
| 애플리케이션 라우팅 | Generator | `programming`, `policy-coding-convention` | BrowserRouter 기반 `/`, `/ui-showcase`, fallback 라우트 |
| 모바일 레이아웃/전역 CSS | Publisher | `frontend`, `policy-styles`, `policy-publishing` | 320/375px 무가로 overflow와 44px touch target |
| 제어 상태/overlay 동작 | Generator | `policy-hook-extraction`, `policy-validation` | 클릭·입력·선택·열기/닫기 결과가 화면에 표시됨 |
| 검토 | Watcher | `policy-review-checklist`, `review-work`, `visual-qa` | 현재 변경에 대한 PASS/FAIL 및 실제 브라우저 근거 |
| 장기 평가 | Evaluator | `policy-documentation`, `policy-portfolio` | 기술 부채와 재사용 자산을 현재 판정과 분리해 기록 |

## 검증

- 변경한 `.ts`/`.tsx` 파일별 `lsp_diagnostics`
- `npm run lint`
- `npm run build`
- 저장소 규칙에 따라 테스트 파일과 화면 캡처는 추가하지 않는다.
- 구현 후 Watcher와 Evaluator 문서화

## 위험 요소 및 결정 사항

- **결정**: 사용자 요청에 따라 `react-router-dom@^7.18.2`를 도입하고 v7 declarative mode를 사용한다.
- **결정**: `BrowserRouter` 소유권은 `main.tsx`, route table과 전역 overlay host 소유권은 `App.tsx`에 둔다.
- **결정**: legacy `main.css`는 접근성 및 desktop 고정 폭 회귀 가능성이 있어 import하지 않고 활성 `index.css`만 정비한다.
- **위험**: native dialog/file input/React Aria calendar는 브라우저별 차이가 있으므로 실제 Chrome mobile viewport와 키보드로 확인한다.
- **위험**: 직접 URL 접근은 배포 서버의 SPA fallback에 의존한다. Vite dev/preview에서 검증하며 배포 인프라 설정 변경은 이번 범위에서 제외한다.
- **위험**: 모든 상태를 한 파일에 넣으면 250 LOC를 초과하므로 섹션/fixture/state 책임을 분리한다.

## 승인

- 상태: approved
- 승인 근거: 사용자 독립 문장 `작업 진행.`
- 필수 문구: `이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?`
