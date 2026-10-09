# UI와 Logic을 연결하는 controller 계약

## 책임과 적용 범위

UI와 API를 연결하는 작업에서는 Logic이 UI 없는 controller를 구현하거나 기존 controller를 확장한다. controller는 API 응답을 UI에 제공하는 계약과 UI 입력·동작을 API 요청으로 연결하는 계약을 정의하는 adapter이자 interface다. 실제 화면이 아직 없어도 Logic이 먼저 확인된 요구와 DTO를 바탕으로 계약을 제공할 수 있다.

현재 프로젝트에서 같은 책임을 수행하는 화면 hook이 있으면 재사용·확장하고 이름만 다른 전달용 계층을 추가하지 않는다. 먼저 같은 프로젝트의 다른 도메인 controller, 공개 타입, mapper, query·mutation과 실제 UI 사용처를 함께 조사한다. 파일명이나 미연결 예제만으로 표준을 판단하지 않는다.

## 선행 구현에 따른 계약 기준

아래 화살표는 데이터 이동 방향이 아니라 **어느 구현이 어느 계약에 맞추는지**를 나타낸다. 선행 구현과 사용자 확인 근거를 `plan.md` 또는 `handoff.md`에 기록한다. UI 자산 선정 문서를 작성하는 작업이면 그 문서에서도 연결한다.

| 선행 구현 | 계약 제공자 | 맞추는 방향 | 구현 기준 |
| --- | --- | --- | --- |
| Logic이 먼저 구현됨 | Logic의 controller | `controller <- UI` | Logic이 요청·응답 DTO와 확인된 요구를 근거로 controller의 데이터·상태·입력·동작 계약을 제공하고 UI가 해당 계약에 맞춘다. |
| UI가 먼저 구현됨 | 기존 UI의 props·입력·callback 계약 | `controller -> UI` | UI가 제공한 계약이 controller 형태가 아니어도 Logic이 해당 계약에 맞춰 controller를 구현한다. UI에 controller 형태의 계약을 먼저 다시 만들도록 요구하지 않는다. |

어느 쪽이 먼저인지, 실제 사용 중인 계약이 무엇인지 불분명하면 사용자 요청·현재 코드·handoff를 확인하고 기준을 질문한다. 파일 생성 시점이나 역할 이름만으로 계약 제공자를 추정하지 않는다. 양쪽이 병렬로 시작하면 연결 계약과 적용 순서를 먼저 합의한다.

요청·응답 DTO는 Logic이 구현하므로 controller 계약의 API 측 정확성은 실제 DTO·parser·전송 근거로 검증한다. 이것이 기존 UI 계약을 자동으로 덮어쓸 권한은 아니다. `controller -> UI`로 연결할 때 UI가 요구·전달하는 항목과 controller가 제공·수용할 항목이 일치하지 않으면 **반드시 사용자에게 질문하고 해당 연결 결정을 기다린다.**

- 이름·타입·필수 여부·nullable·기본값, 값 범위·단위·날짜 표현, ID 의미와 출처, 이벤트 payload·결과, 로딩·빈 상태·오류·성공의 의미를 대조한다.
- UI 항목과 경로, controller·DTO 항목과 경로, 차이와 실제 API 근거를 제시한다. controller의 매핑으로 해결할 수 있는지, UI 계약 변경이 필요한지, API 요구 확인이 필요한지와 각 영향을 설명한다.
- 응답에 없는 필드를 임의 생성하거나 UI 입력을 누락·강제 변환·임의 기본값으로 보충하지 않는다. UI나 DTO를 조용히 바꾸거나 타입 단언·mock으로 차이를 숨기지 않는다.
- 답변 전에는 해당 불일치에 의존하는 구현을 보류한다. 사용자가 확정한 매핑·UI 변경·계약 결정을 기록한 뒤 반영하며 이미 확정한 동일 결정은 반복 질문하지 않는다.

Logic 선행에서도 UI 요구와 제공된 controller 계약이 충돌하면 기존 추측 금지 규칙에 따라 확인한다. “선행 계약에 맞춘다”는 규칙으로 사용자 요구를 버리지 않는다.

## 양방향 계약과 계층

| 방향 | controller가 정의·조율하는 계약 | 기존 계층에 유지할 책임 |
| --- | --- | --- |
| API 응답 → UI | 검증된 데이터의 표시 모델, 목록·상세·페이지 정보, 로딩·갱신·빈 상태·오류·처리 결과, 가능한 사용자 동작 | 응답 DTO·런타임 검증은 API/parser, 캐시·서버 비동기 상태는 query·mutation |
| UI 입력·동작 → API | 입력 값·선택·필터·페이지·ID, action/callback 인자와 결과, 제출 가능 여부·검증 오류·중복 제출 방지 | 업무 검증·요청 mapper는 도메인, HTTP·인증·직렬화·signal은 API factory/client, 캐시 갱신은 mutation |

응답은 `API/parser → query·도메인 hook → controller의 UI 계약 → View`, 요청은 `UI 값·동작 → controller → 도메인 검증·요청 mapper → query/mutation → API factory/client`로 연결한다. controller는 기존 hook과 순수 mapper를 조합하고 transport나 parser를 다시 구현하지 않는다. UI 이벤트가 DTO와 다르면 명시적인 mapper로 허용 필드만 옮기며 의미가 같은 필드는 불필요하게 복사·재명명하지 않는다.

- controller는 JSX, 마크업, CSS, 아이콘·모달 콘텐츠 같은 렌더링 결과를 만들지 않는다. 오류·확인·완료 화면에는 UI가 표현할 데이터·상태·callback을 제공한다. 전역 오류 reporter와 같은 오류를 중복 표시하지 않는다.
- 공개 계약은 UI와 Logic이 참조할 수 있는 기존 `model/*.types.ts` 등 적절한 경계에 Type Alias로 둔다. controller가 렌더링 컴포넌트의 구현을 import하지 않도록 한다. `interface`라는 역할 설명이 TypeScript `interface`나 class 사용을 요구하는 것은 아니다.
- controller hook과 mapper는 arrow function으로 작성하고 기존 `hook/`·`model/` 위치 및 export 관행을 따른다. 한 계약을 맞추기 위해 모든 도메인의 파일을 일괄 이동·개명하거나 전역 controller registry를 만들지 않는다.
- UI에는 합의한 데이터·상태·동작을 제공한다. 전체 Axios 응답·`ApiResult`·query/mutation 객체를 그대로 넘기는 것으로 UI 계약 정의를 대신하지 않는다. 기존 UI가 요구하는 form 연동 계약은 확인해 연결하고 임의로 바꾸지 않는다.
- 서버 데이터·loading·error를 controller의 별도 state로 복제하지 않는다. 입력 draft·선택·확인 상태는 필요한 소유자에 두고, 서버 갱신 시 미저장 입력을 덮어쓰지 않는다. 현재 컴파일러·구독 방식·실제 렌더링 비용을 근거로 최적화한다.
- page/container는 라우트 인자·연결 수명과 controller 호출·View 조립을 담당한다. API 요청 매핑·응답 가공·업무 규칙은 controller 또는 기존 도메인 mapper에 두며 route의 JSX 콜백에 숨기지 않는다.

## 기존 도메인에서 확인한 패턴

다음은 조사한 구현의 참고 경로다. 소비자 세션은 자기 프로젝트의 경로만 확인하며 현재 연결 상태와 계약을 다시 읽는다. 기존 파일 전체를 새 표준의 적합 사례로 간주하지 않는다.

| 프로젝트·도메인 | 조사 경로 | 재사용할 구조 |
| --- | --- | --- |
| admin-ui · 공지사항 | `src/pages/cp-news/hook/use-cp-news-form-controller.ts`, `model/cp-news-form.types.ts`, `lib/cp-news-form.model.ts`, `ui/cp-news-form-page.tsx` | query·mutation 조합, `fields/delete/load`별 값·상태·callback, 응답→폼 mapper와 생성·수정 payload mapper, controller를 View에 전달하는 얇은 page |
| admin-ui · 출석 이벤트 | `src/pages/event-attendance/hook/use-event-attendance-detail-controller.ts`, `model/event-attendance-detail.types.ts`, `ui/event-attendance-detail-page.tsx` | 도메인별 hook 조합, 탭·입력·저장 계약, ID별 편집 수명 분리, 요청 중복·취소 경계 |
| user-ui · 문의 | `src/features/inquiry/hook/useInquiryListController.ts`, `useInquiryDetailController.ts`, `useInquiryWriteController.ts`, `../model/forms/inquiryForm.ts` | query·mutation 재사용, 목록·오류·제출 상태, 검증된 폼 값의 명시적 요청 변환과 중복 제출 방지 |
| user-ui · 토론 | `src/pages/citizen-participation/model/useDiscussionDetailController.ts`, `presentation.ts` | 응답 표시 mapper와 UI 선택 값→도메인 요청 값 매핑, `pageProps`의 데이터·callback 조립 |

기존 admin-ui의 일부 `.tsx` controller는 알림 콘텐츠 JSX를 생성하고, user-ui의 `src/pages/manage/ui/InquiryRoutes.tsx`에는 표시 변환·폼 계약 조립이 남아 있다. 이 부분은 위의 UI 없는 controller 기준과 구분한다. 기존 코드라는 이유로 복제하거나 이번 연결 범위 밖까지 일괄 수정하지 않는다. 기존 `interface`·추론 반환 타입을 모두 바꾸는 작업도 자동으로 포함하지 않는다.

## 계획·인계와 검증

계획과 handoff에는 선행 구현·계약 제공자·맞추는 방향, 기준 UI/controller·DTO 경로, 응답→UI와 UI→요청 매핑, controller 공개 타입·구현 위치, 불일치·사용자 질문·답변과 남은 작업을 남긴다. API가 없는 UI 요구를 임의로 새 endpoint나 DTO로 채우지 않는다.

화면 없이 계약을 검증한다. 기존 테스트 도구로 mapper의 필드·nullable·enum 변환, controller 반환 값·동작, action 호출 시 실제 요청 필드와 오류 결과를 확인한다. 해당 기능의 빈 응답·실패·ID 미선택·중복 제출·ID 변경·늦은 응답·취소 중 의미 있는 경계를 포함한다. Query 캐시·상태를 중복 생성하거나 미확정 계약을 fixture로 확정하지 않는다.

user-ui의 `src/features/inquiry/hook/useInquiryControllers.test.tsx`는 UI 마크업 없이 hook을 실행하고 MSW로 요청·응답을 검증하는 기존 예다. 테스트 도구와 명령은 대상 프로젝트의 실제 설정을 따르며 이 예를 위해 다른 프로젝트에 새 테스트 라이브러리를 자동 설치하지 않는다.

완료 시에는 양방향 계약과 실제 구현이 일치하고 UI 없는 controller가 연결되어 있어야 한다. UI 선행의 항목 불일치는 사용자 답변과 반영 결과가 있어야 하며, 미해결 불일치를 남긴 채 API 연결 완료로 보고하지 않는다.
