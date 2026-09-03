<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/common/skills/reference/components/COMMON_COMPONENTS.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 공용 컴포넌트 카탈로그

아래의 모든 항목은 `src/shared/ui/` 아래에 실제로 존재합니다. 계약을 변경하기 전에 구현과 해당 컴포넌트의 로컬 CSS를 확인합니다.

| 자산 | 경로 | 책임 / 계약 |
| --- | --- | --- |
| 작성자 배지 | `author/` | 작성자 식별 정보를 간결하게 표시 |
| Button | `button/` | 의미 기반 `variant`와 `pending`/`disabled` 상태를 제공하는 HeroUI 동작 어댑터 |
| 카테고리 배지 | `category/` | 도메인에 종속되지 않는 카테고리 표시 |
| 날짜 범위 선택기 | `date-range-picker/` | HeroUI/React Aria 어댑터이며 `YYYY-MM-DD` 문자열만 입력받고 반환 |
| Dialog | `dialog/` | Zustand 기반 알림/확인 화면과 `useDialog` API |
| Dropdown | `dropdown/` | 인덱스 기반 HeroUI Select 어댑터이며 `(type, index)`를 반환 |
| 페이드인 | `fade-in/` | 필수 동작과 무관한 `opacity`/`transform` 등장 효과 |
| 폼 | `form/` | 공용 폼 어댑터를 위해 예약된 공개 진입점 |
| 아이콘 버튼 | `icon-button/` | 접근성을 갖춘 아이콘 전용 동작 어댑터 |
| 이미지 모달 | `image-modal/` | 게시/구독 방식의 이미지 미리보기 화면 |
| 이미지 업로드 | `image-upload/` | 게시/구독 방식의 파일 선택 팝업이며 실제 업로드 실행은 호출자가 담당 |
| Loading | `loading/` | 로딩 표시기/오버레이 |
| `CustomModal` | `modal/` | HeroUI 중앙 정렬 모달 어댑터 |
| 결과 없음 | `no-results/` | 목록이 비었을 때 안내 표시 |
| Pagination | `pagination/` | 페이지 이동 제어 |
| Popup | `popup/` | 가벼운 오버레이 틀 |
| 사유 입력 | `reason-prompt/` | 사유 입력 영역과 콜백 흐름 |
| 검색 상태 표시줄 | `search-state-bar/` | 탭, 키워드/검색 기준 제어, 생성 동작 |
| 사이드 모달 | `side-modal/` | 측면 상세/수정 화면을 위한 HeroUI 패널 어댑터 |
| 상태 배지 | `status/` | 도메인에 종속되지 않는 상태 표시 |
| Table | `table/` | 타입이 지정된 열, 표, 셀, 페이지네이션과 `useFetchAdapter` 제공 |
| 여러 줄 입력 | `text-area/` | `disabled`/`focus` 상태를 지원하는 여러 줄 입력 |
| 텍스트 입력 | `text-input/` | 키보드로 조작 가능한 지우기/비밀번호 제어를 제공하는 HeroUI 입력 어댑터 |
| 토글 스위치 | `toggle-switch/` | HeroUI 불리언 제어 어댑터 |

## 선택 규칙

- 기능 전용 비즈니스 로직은 `src/shared/ui` 밖에 둡니다.
- `@heroui/react` 가져오기는 공용 어댑터 내부에서만 사용합니다.
- 표준 페이지네이션 목록에는 `table/hooks/useFetchAdapter.ts`를 사용합니다.
- 부모/자식 구성이 상호작용을 소유할 수 없는 경우에만 게시/구독 방식을 사용합니다.
- 사용자에게 노출되는 문구는 현재 한국어입니다. 존재하지 않는 i18n 계약을 도입하지 않습니다.
