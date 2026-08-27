# 탐색

## 요청

현재 프로젝트의 공용 UI를 한 화면에서 확인하고 직접 조작할 수 있는 페이지를 추가하며, 활성 전역 스타일을 모바일 레이아웃 기준으로 정비한다.

## 대상 관련 사실

- 애플리케이션은 `src/main.tsx`에서 `src/index.css`와 `App`을 로드한다.
- `src/App.tsx`는 라우터 없이 `MeetingPage`를 직접 렌더링하며 `Dialog`, `ImageModal`, `ImageUploadPopup`, `ReasonPromptHost`를 전역 호스트로 함께 마운트한다.
- `package.json`에는 라우팅 라이브러리가 없지만, 사용자가 `react-router-dom` 기반 라우팅 설정을 명시적으로 요청했다.
- 2026-08-07 기준 npm registry의 `react-router-dom` 최신 버전은 `7.18.2`이며 peer dependency는 React/React DOM `>=18`이다. 현재 React `19.2.8`과 호환된다.
- React Router v7의 declarative mode는 `BrowserRouter` 아래 `Routes`/`Route`를 구성하고 `Link`/`NavLink`로 SPA 이동을 제공한다.
- 활성 전역 스타일은 `src/index.css`이다. `src/shared/assets/css/main.css`와 그 하위 reset/responsive 파일은 현재 import되지 않으며, 전역 포커스 제거와 데스크톱 고정 폭 등 이번 목표에 맞지 않는 규칙을 포함한다.
- `index.html`에는 `width=device-width, initial-scale=1.0` viewport 메타가 이미 있다.
- `DESIGN.md`는 375px 무가로 스크롤, 44px 터치 대상, `100svh` 기반 모바일 안정성, 포커스 표시, 공용 기본 요소의 필수 상태를 계약으로 정의한다.
- `DESIGN.md`의 기존 기술 부채에는 상시 공용 기본 요소 쇼케이스가 없다는 항목이 있으며, 이번 요청은 해당 해소 조건에 해당한다.

## 불러온 스킬

- `skill-index`, `frontend`, `programming`
- `reference-components`
- `policy-harness`, `policy-documentation`, `policy-styles`, `policy-publishing`
- `policy-coding-convention`, `policy-review-checklist`
- Frontend references: `design/README.md`, `perfection/README.md`
- TypeScript reference: `references/typescript/README.md`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| Button, IconButton | 직접 시연 | 기본/변형/로딩/비활성 및 클릭 결과를 확인할 수 있다. |
| TextInput, TextArea | 직접 시연 | 제어 상태, clear, password 표시, 오류, 읽기 전용/비활성을 확인한다. |
| Dropdown, ToggleSwitch | 직접 시연 | 선택/선택 해제 및 checked 상태 변화를 결과 패널에 표시한다. |
| Pagination, DateRangePicker | 직접 시연 | 페이지 이동, 10페이지 창, 날짜 범위/경계/비활성 날짜를 확인한다. |
| StatusBadge, CategoryBadge, AuthorBadge | 직접 시연 | 모든 tone/variant와 빈 값 fallback을 표시한다. |
| Loading, NoResults, FadeInComponent | 직접 시연 | 로딩/빈 상태와 모션 감소 대응을 확인한다. |
| CustomModal, SideModal, Popup | 런처로 시연 | 열기, 닫기, backdrop/Escape, 접근 가능한 이름을 확인한다. |
| Dialog + useDialog | 전역 호스트를 통해 시연 | alert callback, confirm true/false 결과를 확인한다. |
| ImageModal | 전역 호스트를 통해 시연 | 같은 오리진 샘플 자산 열기와 닫기 동작을 확인한다. |
| ImageUploadPopup | 전역 호스트를 통해 시연 | 열기, 파일 형식 검증, 취소 및 callback 결과를 확인한다. |
| ReasonPrompt, ReasonPromptHost | 직접/호스트 시연 | 길이 검증, trim 제출, 취소, 반복 호출을 확인한다. |
| SearchStateBar, TableSortFilter | 직접 시연 | 탭, 검색 기준, 키워드 clear/submit, 정렬/reset을 확인한다. |
| Table | 직접 시연 | 모든 accessor 유형, custom/action cell, loading/empty/pagination을 확인한다. |
| useFetchAdapter | 직접 렌더링 제외 | 데이터 요청 훅이며 별도 API 없이 시각적으로 시연할 대상이 아니다. 제외 사유를 페이지에 기록한다. |
| resolveRowNumber | Table 시연에 포함 | 순수 유틸리티이므로 numbering column 결과로 간접 검증한다. |
| 타입, store, 빈 form barrel | 직접 렌더링 제외 | 컴파일타임/상태 계약 또는 export가 없는 모듈이다. 제외 사유를 페이지에 기록한다. |

## 제약 조건 및 미확인 사항

- `BrowserRouter`는 `src/main.tsx`에서 애플리케이션 전체에 한 번 제공하고, `src/App.tsx`가 `/`, `/ui-showcase`, `*` 라우트를 소유해야 한다.
- 공용 overlay 호스트는 중복 마운트하지 않고 기존 `App.tsx`의 단일 인스턴스를 재사용해야 한다.
- HeroUI/React Aria 컴포넌트는 현재 별도 provider 없이 사용되는 프로젝트 구조를 유지한다.
- `ImageModal` 시연에는 같은 오리진의 비민감 샘플 이미지 자산을 새로 추가해야 한다.
- 저장소 규칙에 따라 테스트 코드와 화면 캡처를 만들지 않고 `npm run build`와 `npm run lint`로 검증한다.

## 결론

`react-router-dom` v7 declarative mode로 `/`와 `/ui-showcase`를 구성하고, 25개의 렌더 가능한 공용 UI 표면과 `useDialog` 상호작용 API를 상태별 섹션으로 나누어 시연한다. 활성 `src/index.css`에는 모바일 안전 전역 baseline만 추가하고, 접근성/고정 폭 문제가 있는 고립된 legacy `main.css`는 import하지 않는다.
