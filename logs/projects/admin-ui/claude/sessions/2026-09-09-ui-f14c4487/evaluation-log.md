# 평가 로그

## 현재 판정과의 경계

여기서는 현재 변경의 PASS/FAIL을 다시 판정하지 않는다.

## 장기 관찰 사항

- 공지 진입점이 둘로 갈라져 있다. 기존 `/cp/boards/notices/:noticeId/edit`는 mock 기반 cp-board 계약이고, 새 화면은 news API 계약이다. 통합 방침을 정하지 않으면 같은 데이터에 대해 서로 다른 필드를 저장하는 두 폼이 남는다.
- `src/shared/ui/toggle-switch`는 접근 가능한 이름을 받을 수 없어 관리 화면에서 사실상 쓰기 어렵다. 현재 프로젝트에서 사용처가 없다.
- 목록 화면마다 `Dropdown`의 index 계약과 값 기반 상태 사이의 변환 코드가 반복된다. cp-board는 controller에, cp-news는 View에 두었다.
- news 목록 API가 상태별 전체 집계를 제공하지 않아 다른 관리 화면과 달리 KPI 영역을 구성할 수 없다.

## 이 문제가 중요한 이유

진입점 이원화는 운영자가 어느 화면에서 수정하느냐에 따라 저장되는 필드가 달라지는 데이터 정합성 문제로 이어진다. 나머지는 화면이 늘어날수록 접근성 결함과 변환 코드가 복제되는 구조적 비용이다.

## 재사용 가능 자산

- `src/pages/cp-news/model/*.types.ts`의 controller 계약은 다른 목록·폼 페이지에서도 쓸 수 있는 구조(search·table·error, fields·delete·load)를 따른다.
- 목록 표기 상수와 필터 항목 생성 패턴은 `cp-board`와 동일해 다음 도메인 화면에서 그대로 응용할 수 있다.

## 기술 부채

- 프로젝트 전체 타입 검사에 기존 오류 14건(`erasableSyntaxOnly` 위반, 미사용 선언)이 남아 있다. 이번 변경과 무관하지만 `npm run build`를 검증 기준으로 쓰기 어렵게 만든다.
- 전체 lint의 기존 68 errors / 5 warnings도 같은 이유로 회귀 판정을 흐린다.
- news MSW handler가 브라우저 registry에 없어 개발 환경에서 화면을 mock으로 확인할 수 없다.

## 추상화·아키텍처·의존성 방향

페이지가 `entities/news`의 타입과 hook에만 의존하고, View는 controller 인터페이스에만 의존한다. 의존성 방향은 FSD 경계와 일치한다. 삭제 팝업을 `features/`로 올리지 않은 것은 사용처가 하나이기 때문이며, 두 번째 사용처가 생기면 승격을 검토할 수 있다.

## 프로세스 개선 사항

- UI가 계약을 먼저 정의하고 Logic이 구현하는 인계 순서는 이번에도 잘 작동했다. 다만 UI 단독으로는 화면을 렌더해 볼 수 없어 검증이 정적 검사에 한정된다. 계약 확정 후 Logic 통합까지의 간격을 짧게 유지하는 편이 좋다.
- shared 컴포넌트의 결함(ToggleSwitch)을 발견해도 scope 밖이라 우회해야 했다. 이런 발견을 backlog로 남기는 경로가 필요하다.

## 권고 사항

1. Logic 통합 직후 두 공지 진입점의 통합·redirect 방침을 사용자와 확정한다.
2. `ToggleSwitch`에 `ariaLabel`/`id` 전달을 추가하는 별도 scope를 검토한다.
3. news MSW handler의 브라우저 registry 등록 여부를 Logic 담당이 결정한다.

## 개선 선택지와 권장 backlog

| 항목 | 선택지 | 권장 |
| --- | --- | --- |
| 공지 진입점 | ① 기존 유지 ② 새 화면으로 redirect ③ 기존 제거 | ② — 숫자 ID 호환을 확인한 뒤 redirect |
| ToggleSwitch | ① 방치 ② 접근성 props 추가 ③ 제거 | ② |
| Dropdown 변환 | ① 화면마다 반복 ② 값 기반 어댑터 추가 | ① 유지, 세 번째 사용처가 생기면 ② 검토 |

## 다음 제안 단계

Logic 담당의 controller 구현 → 라우트·메뉴 연결(UI) → 등록·수정·삭제 흐름의 통합 검증 → 기존 진입점 정리.
