# Handoff — 시민참여 사용자 Mobile UI → Hephaestus

> 작성일: 2026-08-14
> 세션: 2026-08-14-citizen-participation-mobile-ui
> 작성자: Claude Code (production UI)
> 상태: `UI_COMPLETE`. 기능 연결 대기.

---

## 0. 요약

`시민참여v_4.8.pdf`의 사용자 Mobile 13화면(p2~p14)과 신고 팝업(p38)을 production UI로 퍼블리싱했습니다.
모든 페이지는 **제어형 props/callback**으로만 구성되어 있으며, API 호출·상태 전이·검증·라우팅 배선은 포함하지 않았습니다.

Claude Code가 생성한 파일은 아래 2개 경로뿐입니다. 그 외 경로는 수정하지 않았습니다.

- `src/shared/ui/tabs/` (신규 공용 자산)
- `src/features/citizen-participation/ui/` (신규 UI 세그먼트)

---

## 1. Hephaestus 작업 항목

### 1-1. 라우트 등록 — `src/App.tsx` (Hephaestus 단독 소유)

기존 `src/shared/config/citizenParticipationRoutes.ts`의 13개 라우트와 PDF 13화면이 **1:1로 정확히 대응**합니다. 라우트 추가·변경은 불필요합니다.

| 라우트 키 | 경로 | 연결할 컴포넌트 |
| --- | --- | --- |
| `main` | `/citizen-participation` | `CitizenMainPage` |
| `proposals` | `/citizen-participation/proposals` | `ProposalListPage` |
| `proposalCreate` | `/citizen-participation/proposals/new` | `ProposalWritePage` |
| `proposalDetail(id)` | `/citizen-participation/proposals/:id` | `ProposalDetailPage` |
| `votes` | `/citizen-participation/votes` | `VoteListPage` |
| `voteDetail(id)` | `/citizen-participation/votes/:id` | `VoteDetailPage` |
| `discussions` | `/citizen-participation/discussions` | `DiscussionListPage` |
| `discussionDetail(id)` | `/citizen-participation/discussions/:id` | `DiscussionDetailPage` |
| `policies` | `/citizen-participation/policies` | `PolicyListPage` |
| `policyDetail(id)` | `/citizen-participation/policies/:id` | `PolicyDetailPage` |
| `surveys` | `/citizen-participation/surveys` | `SurveyListPage` |
| `surveyDetail(id)` | `/citizen-participation/surveys/:id` | `SurveyDetailPage` |
| `myActivity` | `/citizen-participation/me/activity` | `MyActivityPage` |

`ReportPopup`은 라우트가 없습니다. `VoteDetailPage` · `DiscussionDetailPage` · `PolicyDetailPage` 3개 상세 화면에서 오버레이로 렌더합니다.

> `proposalCreate`(`/proposals/new`)와 `proposalDetail`(`/proposals/:id`)의 선언 순서에 주의하십시오. `new`가 `:id`에 먹히지 않도록 정적 경로를 먼저 선언해야 합니다.

### 1-2. feature barrel — `src/features/citizen-participation/index.ts` (Hephaestus 단독 소유)

현재 barrel 파일이 없습니다. `shared-ui-showcase/index.ts`와 동일한 양식으로 생성이 필요합니다.

```ts
export { default as CitizenMainPage } from "./ui/main/CitizenMainPage";
// … 이하 13개 페이지 + ReportPopup
```

### 1-3. ServiceTabs 네비게이션 배선

`ServiceTabs`는 순수 제어형입니다. 자체적으로 `useNavigate`를 호출하지 않습니다.
9개 화면(제안 목록/상세/작성, 투표 목록/상세, 토론 목록/상세, 정책 목록/상세)이 동일한 `onServiceTabChange` prop을 받습니다.

```ts
type ServiceTabValue = "all" | "proposal" | "vote" | "discussion" | "policy";
```

`ServiceTabValue` → 라우트 매핑 배선이 필요합니다. `all` 탭에 대응하는 통합 목록 라우트는 현재 `citizenParticipationRoutes`에 없으므로, `main`으로 보낼지 새 라우트를 만들지 결정이 필요합니다.

### 1-4. 데이터 조회 및 상태

| 항목 | 대상 화면 | 비고 |
| --- | --- | --- |
| 목록 조회 + 페이지네이션 | 제안·투표·토론·정책 목록 | `page` / `pageCount` / `onPageChange` |
| `내 활동 보기` 필터 | 제안·투표·토론·정책 목록 | `myActivityOnly` / `onMyActivityChange` |
| 설문 상태 필터 + 키워드 검색 | 설문 목록 | `statusFilter` / `keyword` / `onSearch` |
| 활동 유형 필터 | 내 활동 | `filter` / `onFilterChange` |
| 로딩 상태 | 목록 전체 | `isLoading` — UI가 `Loading` / `NoResults` 분기 처리 |

기존 `hook/useCitizenParticipationQueries.ts` · `useCitizenParticipationMutations.ts`와 `model/queryKeys.ts`를 사용하십시오.

### 1-5. 폼 및 제출

- **제안 작성**(`ProposalWritePage`): 검증은 기존 `model/forms/proposalForm.ts` 사용. UI는 `values` / `errors` / `isSubmitting`을 받고 `onChange(field, value)` / `onSubmit` / `onCancel`을 호출만 합니다.
- **투표 제출**(`VoteDetailPage`): `selectedChoice` + `onSubmitVote`
- **토론 의견 등록**(`DiscussionDetailPage`): `selectedChoice` + `onSubmitOpinion`
- **신고 접수**(`ReportPopup`): `reason` / `detail` + `onSubmit`

### 1-6. 표시값 가공 (UI에 계산 로직 없음)

| 값 | 현재 UI 취급 | 필요한 util |
| --- | --- | --- |
| D-Day (`D-7`, `D-14`, `D-5`) | 완성된 문자열 `dDayLabel`을 받아 그대로 표시 | 날짜 차이 계산 |
| 찬반 비율 (`agreeRatio` 등) | 0~100 숫자를 받아 `width: %`로 렌더 | `model/voteResult.ts` |
| 날짜 (`2026.03.08`) | 완성된 문자열을 받아 그대로 표시 | `shared/lib/utils/date.util.ts` |
| 기간 (`투표 기간 … ~ …`) | 완성된 문자열 `period`를 받음 | 동일 |
| 활동 요약 (`작성 2 · 참여 5 · 댓글 3`) | 완성된 문자열 `summaryValue`를 받음 | 집계 |

**모든 날짜·비율 문자열은 UI 밖에서 완성해서 넘겨주십시오.** UI는 포맷팅을 수행하지 않습니다.

### 1-7. 신고 팝업 연결

`ReportPopup`은 `VoteDetailPage` · `DiscussionDetailPage` · `PolicyDetailPage`가 노출하는 `onReport(commentId)` 콜백에서 열립니다.
팝업의 open 상태, 대상 댓글 조회(`ReportTarget`), 접수 후 완료 토스트는 UI 밖에서 관리해야 합니다.

---

## 2. Props 계약 전문

### 2-1. 공용 자산 — `src/shared/ui/tabs/`

```ts
export type TabItem<TValue> = { readonly label: string; readonly value: TValue; readonly disabled?: boolean };

interface TabsPropTypes<TValue> {
  readonly items: readonly TabItem<TValue>[];
  readonly value: TValue;
  readonly label: string;                        // aria-label (필수)
  readonly onChange: (value: TValue) => void;
  readonly className?: string;
  readonly variant?: "primary" | "secondary";    // HeroUI tabsVariants
}
```

HeroUI `Tabs` 어댑터입니다. 인덱스 기반 키를 사용하므로 `TValue`가 문자열이 아니어도 됩니다.
도메인 로직이 없는 범용 자산이므로 시민참여 외 기능에서도 재사용 가능합니다.

> **주의**: `Tabs.Indicator`는 반드시 각 `Tab` **내부**에 렌더해야 합니다. `TabList`의 형제로 두면 `<SharedElement> must be rendered inside a <SharedElementTransition>` 런타임 에러가 발생합니다. `src/shared/ui/tabs/tabs.test.tsx`가 이 회귀를 방어합니다.

### 2-2. 공통 레이아웃

```ts
// ServiceTabs
export type ServiceTabValue = "all" | "proposal" | "vote" | "discussion" | "policy";
interface ServiceTabsPropTypes {
  readonly value: ServiceTabValue;
  readonly onChange?: (value: ServiceTabValue) => void;
}
```

### 2-3. p2 — `CitizenMainPage`

```ts
export type MainShortcut = "proposal" | "vote" | "discussion" | "policy" | "survey";
export type MainFeatured = { id: string; status: string; title: string; source: string; date: string };
export type MainNotice = { id: string; title: string; date: string };

interface CitizenMainPagePropTypes {
  readonly featured?: readonly MainFeatured[];
  readonly notices?: readonly MainNotice[];
  readonly isRefreshing?: boolean;
  readonly onShortcutClick?: (shortcut: MainShortcut) => void;
  readonly onFeaturedClick?: (featuredId: string) => void;
  readonly onMyActivityClick?: () => void;
  readonly onRefresh?: () => void;
}
```

`MainShortcut`의 `survey`는 `ServiceTabValue`에 없습니다. 바로가기 5개는 설문을 포함하고 서비스 탭 5개는 `전체`를 포함하는, 서로 다른 집합입니다.

### 2-4. p3 — `ProposalListPage`

```ts
export type ProposalStatus = "received" | "adopted" | "reviewing";  // 접수 / 채택 / 검토중
export type ProposalListItem = { id: string; status: ProposalStatus; title: string; summary: string; author: string; date: string };

interface ProposalListPagePropTypes {
  readonly items?: readonly ProposalListItem[];
  readonly page?: number;
  readonly pageCount?: number;
  readonly isLoading?: boolean;
  readonly myActivityOnly?: boolean;
  readonly onServiceTabChange?: (value: ServiceTabValue) => void;
  readonly onMyActivityChange?: (checked: boolean) => void;
  readonly onItemClick?: (proposalId: string) => void;
  readonly onPageChange?: (page: number) => void;
  readonly onCreateClick?: () => void;
}
```

상태 라벨과 배지 톤 매핑은 UI 내부 상수입니다. API는 `ProposalStatus` 유니온 값만 넘기면 됩니다.

### 2-5. p4 — `ProposalDetailPage`

```ts
export type ProposalDetail = {
  status: string; title: string; author: string; date: string;
  background: string; detail: string; effect: string; reference: string; reviewResult: string;
};

interface ProposalDetailPagePropTypes {
  readonly detail?: ProposalDetail;
  readonly onServiceTabChange?: (value: ServiceTabValue) => void;
  readonly onBackToList?: () => void;
}
```

### 2-6. p5 — `ProposalWritePage`

```ts
export type ProposalFormValues = { title: string; background: string; detail: string; effect: string; reference: string };
export type ProposalFormErrors = Partial<Record<keyof ProposalFormValues, string>>;

interface ProposalWritePagePropTypes {
  readonly values?: ProposalFormValues;
  readonly errors?: ProposalFormErrors;
  readonly isSubmitting?: boolean;
  readonly onServiceTabChange?: (value: ServiceTabValue) => void;
  readonly onChange?: (field: keyof ProposalFormValues, value: string) => void;
  readonly onSubmit?: () => void;
  readonly onCancel?: () => void;
}
```

필수 입력은 제목·배경·상세·기대효과 4개, 참고 사례는 선택입니다(PDF 기준). 필수 표시(`*`)는 UI에 하드코딩되어 있으나 **검증은 수행하지 않습니다**.

### 2-7. p6 — `VoteListPage`

```ts
export type VoteListItem = {
  id: string;
  state: "ongoing" | "closed";
  dDayLabel?: string;      // "D-7"
  title: string; summary?: string; author?: string; opinionCount?: number; date?: string;
  resultText?: string;     // "최종 투표 결과 찬성 89% · 반대 11%"
  agreeRatio?: number; disagreeRatio?: number;  // 0~100
};
```

`state`에 따라 카드 하단이 분기합니다. `ongoing`이면 메타 라인(작성자·의견수·날짜), `closed`면 결과 문구 + 막대입니다.

### 2-8. p7 — `VoteDetailPage`

```ts
export type VoteChoice = "agree" | "disagree";
export type VoteDetail = { state: "ongoing" | "closed"; dDayLabel?: string; title: string; author: string; date: string; agenda: string; period: string };

interface VoteDetailPagePropTypes {
  readonly detail?: VoteDetail;
  readonly comments?: readonly CommentItem[];
  readonly selectedChoice?: VoteChoice | null;
  readonly isSubmitting?: boolean;
  readonly onServiceTabChange?: (value: ServiceTabValue) => void;
  readonly onChoiceChange?: (choice: VoteChoice) => void;
  readonly onSubmitVote?: () => void;
  readonly onReport?: (commentId: string) => void;
  readonly onBackToList?: () => void;
}
```

`detail.state === "closed"`이면 선택지와 제출 버튼이 자동으로 비활성화됩니다.

### 2-9. p8 — `DiscussionListPage`

```ts
export type DiscussionListItem = {
  id: string; state: "ongoing" | "closed"; title: string; summary: string;
  author?: string; opinionCount?: number; date?: string;
  agreeRatio?: number; disagreeRatio?: number; neutralRatio?: number;  // 3분할
};
```

### 2-10. p9 — `DiscussionDetailPage`

```ts
export type DiscussionChoice = "agree" | "disagree" | "neutral";
export type DiscussionDetail = { state: "ongoing" | "closed"; title: string; author: string; date: string; background: string; period: string };

interface DiscussionDetailPagePropTypes {
  readonly detail?: DiscussionDetail;
  readonly comments?: readonly CommentItem[];
  readonly opinionCount?: number;      // 헤더의 "댓글 · 의견 45" 총계
  readonly selectedChoice?: DiscussionChoice | null;
  readonly isSubmitting?: boolean;
  readonly onServiceTabChange?: (value: ServiceTabValue) => void;
  readonly onChoiceChange?: (choice: DiscussionChoice) => void;
  readonly onSubmitOpinion?: () => void;
  readonly onReport?: (commentId: string) => void;
  readonly onBackToList?: () => void;
}
```

`opinionCount`는 전체 의견 수, `comments`는 현재 페이지에 노출할 목록입니다. 두 값이 다를 수 있어 분리했습니다.

### 2-11. p10 — `PolicyListPage`

```ts
export type PolicyListItem = {
  id: string;
  state: "reflected" | "reviewing";   // 반영 완료 / 검토 중
  title: string; summary: string;
  stage: string;                       // "설치 예정" — UI가 "현재 단계: " 접두사를 붙임
};
```

### 2-12. p11 — `PolicyDetailPage`

```ts
export type PolicyDetail = {
  state: "reflected" | "reviewing";
  title: string; author: string; date: string;
  proposalContent: string; department: string; reflectionContent: string;
};
export type StageItem = { label: string; date: string; current?: boolean };

interface PolicyDetailPagePropTypes {
  readonly detail?: PolicyDetail;
  readonly stages?: readonly StageItem[];
  readonly comments?: readonly CommentItem[];
  readonly onServiceTabChange?: (value: ServiceTabValue) => void;
  readonly onReport?: (commentId: string) => void;
  readonly onBackToList?: () => void;
}
```

`StageItem.current === true`인 단계의 타임라인 도트가 `--success` 색으로 강조됩니다. 처리 이력 순서는 배열 순서를 그대로 따릅니다.

### 2-13. p12 — `SurveyListPage`

```ts
export type SurveyStatusValue = "all" | "ongoing" | "scheduled" | "closed";
export type SurveyState = "ongoing" | "scheduled" | "closed";
export type SurveyListItem = { id: string; state: SurveyState; dDayLabel?: string; title: string; summary: string; period: string };

interface SurveyListPagePropTypes {
  readonly items?: readonly SurveyListItem[];
  readonly statusFilter?: SurveyStatusValue;
  readonly keyword?: string;
  readonly sortLabel?: string;     // "최신순"
  readonly totalCount?: number;
  readonly isLoading?: boolean;
  readonly onStatusFilterChange?: (value: SurveyStatusValue) => void;
  readonly onKeywordChange?: (keyword: string) => void;
  readonly onSearch?: () => void;
  readonly onItemClick?: (surveyId: string) => void;
}
```

설문 목록은 **서비스 탭을 사용하지 않습니다**. 상태 필터(`SurveyStatusFilter`)는 shared `Tabs`가 아닌 별도 pill 토글 UI입니다.
카드 배지는 `dDayLabel`이 있으면 D-Day 배지를, 없으면 상태 배지를 표시합니다(PDF p12 동작 그대로).

### 2-14. p13 — `SurveyDetailPage`

```ts
export type SurveyDetail = {
  dDayLabel?: string; title: string; organization: string; registeredAt: string;
  period: string; target: string; duration: string; questionCount: string;
  introduction: string;            // \n 개행 유지 (white-space: pre-line)
  participationNotice: string;
  canParticipate: boolean;         // false면 설문참여 CTA 미노출 (예정/마감)
};

interface SurveyDetailPagePropTypes {
  readonly detail?: SurveyDetail;
  readonly onParticipate?: () => void;
  readonly onBackToList?: () => void;
}
```

`onParticipate`는 외부 링크(Google Forms 등) 이동입니다. UI는 아이콘(`↗`)과 스크린리더 텍스트로 외부 이동임을 표시하지만 **실제 이동은 수행하지 않습니다**.

### 2-15. p14 — `MyActivityPage`

```ts
export type ActivityFilterValue = "all" | "proposal" | "vote" | "discussion" | "policy" | "survey";
export type ActivityItem = { id: string; typeLabel: string; title: string; status: string; date: string };

interface MyActivityPagePropTypes {
  readonly items?: readonly ActivityItem[];
  readonly filter?: ActivityFilterValue;
  readonly summaryLabel?: string;   // "이번 달 활동"
  readonly summaryValue?: string;   // "작성 2 · 참여 5 · 댓글 3"
  readonly rewardNotice?: string;
  readonly onFilterChange?: (value: ActivityFilterValue) => void;
  readonly onItemClick?: (activityId: string) => void;
  readonly onGoMain?: () => void;
  readonly onGoList?: () => void;
}
```

`onItemClick`은 활동 유형에 따라 서로 다른 상세 화면으로 이동해야 합니다. `ActivityItem`에 대상 유형·대상 ID 필드가 필요하면 요청해 주십시오. 현재는 `id` 하나만 노출합니다.

### 2-16. p38 — `ReportPopup`

```ts
export type ReportReason = "abuse" | "spam" | "inappropriate" | "etc";  // 욕설/비방 · 스팸 · 부적절한 내용 · 기타
export type ReportTarget = { kindLabel: string; author: string; excerpt: string };

interface ReportPopupPropTypes {
  readonly open: boolean;
  readonly target: ReportTarget;
  readonly reason?: ReportReason | null;
  readonly detail?: string;
  readonly isSubmitting?: boolean;
  readonly onReasonChange?: (reason: ReportReason) => void;
  readonly onDetailChange?: (detail: string) => void;
  readonly onSubmit?: () => void;
  readonly close: () => void;       // 필수
}
```

`reason === null`이면 `신고 접수` 버튼이 비활성 상태입니다. Escape 키·백드롭 클릭 닫기는 `shared/ui/popup`이 처리합니다.

### 2-17. 공통 타입 — `CommentItem`

```ts
export type CommentItem = {
  id: string; author: string; date: string; body: string;
  stance?: string;      // 토론 전용: "찬성" / "반대" / "중립"
  likeCount?: number;   // 있으면 "♡ 12" 표시
};
```

`onReply`를 넘기면 `답글` 버튼이, `onReport`를 넘기면 `신고` 버튼이 렌더됩니다. 넘기지 않으면 해당 버튼이 나타나지 않습니다.

---

## 3. 중요 주의사항

### 3-1. 기본값은 PDF 예시 데이터입니다

모든 페이지가 PDF 캡처의 예시 데이터를 기본 prop 값으로 갖고 있습니다. 라우트 연결 전 화면 확인용이며, **실제 데이터를 props로 주입하면 전부 대체됩니다**. 제거가 필요하면 알려 주십시오.

### 3-2. `exactOptionalPropertyTypes: true`

이 프로젝트는 해당 옵션이 켜져 있습니다. 선택적 콜백을 그대로 하위에 전달하면 컴파일 에러가 납니다.

```tsx
// 실패
<Button onClick={onBackToList}>

// 통과 — 아래 두 방식 중 하나
<Button onClick={() => onBackToList?.()}>
<Child {...(onReport === undefined ? {} : { onReport })} />
```

### 3-3. 소유권 경계

기능 연결 시 아래 파일들은 **Claude Code 소유**입니다. 직접 수정하지 말고 필요한 계약을 전달해 주십시오.

- `src/features/citizen-participation/ui/**`
- `src/shared/ui/**` (신규 `tabs/` 포함)

props 추가·시그니처 변경이 필요하면 요청해 주시면 UI 쪽에서 반영합니다.

### 3-4. 표시 문자열 포맷팅 금지 원칙

UI는 날짜·비율·D-Day·집계 문자열을 **가공하지 않습니다**. 완성된 표시값을 넘겨주십시오. 이 경계를 UI 안으로 옮기면 계약이 무너집니다.

---

## 4. 검증 상태

| 항목 | 결과 |
| --- | --- |
| `npm run lint` | 통과 |
| `npm run build` | 통과 |
| `npx vitest run src/shared/ui` | 5 파일 6 테스트 통과 |

**미검증 영역**: 라우트가 연결되지 않아 UI가 번들에 포함되지 않았습니다. 타입·린트·공용 `Tabs` 렌더 테스트까지만 확인했으며, 실제 화면 동작은 라우트 연결 후에 확인 가능합니다.

전체 테스트 스위트에서 `src/features/meeting/api/http/meeting.api.test.ts` 2건이 실패하나, Claude Code의 변경 범위 밖입니다(생성 파일은 `citizen-participation/ui/`와 `shared/ui/tabs/` 뿐).

---

## 5. 레이아웃 수치 계약 (참고)

`.cp-screen`에 정의된 토큰입니다. 기능 연결 시 레이아웃을 변경할 필요는 없으나, 값이 궁금할 때 참조하십시오.

| 토큰 | 값 | 용도 |
| --- | --- | --- |
| `--cp-screen-max` | `480px` | 모바일 셸 최대 폭, 중앙 정렬 |
| `--cp-screen-pad` | `16px` | 화면 좌우 패딩 |
| `--cp-section-gap` | `16px` | 섹션 간 세로 간격 |
| `--cp-card-gap` | `12px` | 목록 카드 간 간격 |
| `--cp-card-pad` | `16px` | 카드 내부 패딩 |
| `--cp-card-radius` | `12px` | 카드 모서리 |
| `--cp-inner-gap` | `8px` | 카드 내부 요소 간격 |
| `--cp-btn-h` | `48px` | 액션 버튼 높이 |
| `--cp-field-gap` | `16px` | 폼 필드 그룹 간격 |
| `--cp-label-gap` | `8px` | 라벨 ↔ 필드 간격 |

PDF 안내 문서에서 어긋나 있던 배치(p3·p6·p10 제목/탭 겹침, p8 버튼 줄바꿈, p7 CTA 중복·버튼 폭 불일치, p5 라벨 겹침, p12 검색 버튼 겹침, p4 섹션 고정 높이)는 위 토큰 기준으로 정규화했습니다. `내 활동` / `내 활동 보기` 표기는 `내 활동 보기`로 통일했습니다.
