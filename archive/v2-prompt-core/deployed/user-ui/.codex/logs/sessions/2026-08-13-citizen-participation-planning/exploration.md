# 탐색

## 요청

`/Users/okand/Downloads/시민참여v_4.8.pdf`와 사용자 설명을 근거로 시민참여 모바일 기능의 FSD 구조, Axios API, DTO, TanStack Query, MSW, React Hook Form/Zod, 라우팅 및 Claude Code UI 계약을 승인 전 계획으로 작성한다.

## 대상 관련 사실

- PDF 파일명은 v4.8, 문서 내부 표기는 v4.7이다.
- 이 프로젝트의 분석 범위는 페이지 2–14의 사용자 Mobile 13개 화면과 모바일 신고 팝업 `CP_REPORT_POPUP_MOBILE`로 한정한다. 그 밖의 페이지는 분석·구현·검증 대상에 포함하지 않는다.
- 모바일 화면 ID는 `CP_MAIN_MOBILE`, `CP_PROPOSAL_LIST_MOBILE`, `CP_PROPOSAL_DETAIL_MOBILE`, `CP_PROPOSAL_WRITE_MOBILE`, `CP_VOTE_LIST_MOBILE`, `CP_VOTE_DETAIL_MOBILE`, `CP_DISCUSS_LIST_MOBILE`, `CP_DISCUSS_DETAIL_MOBILE`, `CP_POLICY_LIST_MOBILE`, `CP_POLICY_DETAIL_MOBILE`, `CP_SURVEY_LIST_MOBILE`, `CP_SURVEY_DETAIL_MOBILE`, `CP_MY_ACTIVITY_MOBILE`이다.
- `package.json`에는 Axios와 React Router가 있으나 `@tanstack/react-query`, `react-hook-form`, `zod`, `@hookform/resolvers`, `msw`는 없다.
- `src/App.tsx`에는 `/`, `/ui-showcase`, fallback만 존재한다.
- `src/shared/api/api-client.ts`는 Axios 응답을 `ApiResult<T>`로 정규화한다. `src/shared/lib/hooks/use-api.tsx`는 명령형 요청의 취소·로딩·오류 부수 효과를 담당한다.
- 공식 문서 확인 결과 TanStack Query는 query 함수 의존값을 query key에 포함하고 mutation 성공 후 관련 key를 무효화하는 구성이 적합하다. MSW v2 브라우저 구성은 `setupWorker(...handlers)`와 `http` handler를 사용한다. RHF는 `zodResolver(schema)`로 Zod 스키마를 연결할 수 있다.

## 불러온 스킬

- `policy-documentation`, `policy-harness`
- `policy-data-fetch-layer`, `policy-type-definition`, `policy-validation`
- `recipe-index`, `recipe-data-fetch`, `recipe-data-dto`
- `reference-index`, `reference-components`, `reference-custom-hooks`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| button, icon-button | 재사용 후보 | 목록 이동, 작성, 투표, 좋아요, 댓글, 신고 액션의 공용 경계다. |
| text-input, text-area, form | 재사용 후보 | 제안 작성과 검색 입력에 사용할 수 있으나 RHF props 계약은 Claude Code가 최신 구현을 확인해야 한다. |
| category, status | 재사용 후보 | 제안·투표·토론·정책반영 상태와 유형 표현에 적합하다. |
| pagination | 재사용 후보 | 댓글과 목록 페이지네이션에 적합하나 모바일 표현은 Claude Code가 판단한다. |
| dialog, popup, reason-prompt | 재사용 후보 | 신고 사유, 제출·투표 확인 및 오류 안내에 적합하다. |
| table | 직접 사용하지 않음 | 모바일 카드 목록 요구와 맞지 않는다. |
| `useApi` | 신규 query에서 사용하지 않음 | TanStack Query와 로딩·취소·오류 상태 소유권이 중복된다. 기존 명령형 흐름에만 유지한다. |
| `ApiClient` / `ApiResult` | 재사용 | Axios 전송과 서버 envelope 정규화 경계를 보존한다. query 함수는 실패 `ApiResult`를 typed error로 변환해야 한다. |

## 요구사항 추적표

| PDF 화면 | 명시된 기능/API 책임 | Claude Code UI 책임 |
| --- | --- | --- |
| 메인 | 배너·주요 제안·공지·내 활동 조회, 바로가기 route, 갱신 | 헤더, 배너, 바로가기, 주요 항목, 공지, 내 활동 섹션 |
| 시민 제안 목록 | `myActivity` 필터, 상태별 카드, 상세 이동 | 서비스 탭, 제목/필터, 접수·채택·검토중 카드 |
| 시민 제안 상세 | route id로 상세 조회, 목록 복귀 | 상태·제목·메타·본문·액션 |
| 시민 제안 작성 | 필수 필드 검증, 요청 DTO 변환, 생성 mutation | 작성 안내, 입력 필드, 오류 문구, 제출 UI |
| 시민 투표 목록 | 목록 조회, 찬성/(찬성+반대) 비율 계산 | 카드와 결과 그래프 |
| 시민 투표 상세 | 상세 조회, 진행 상태에 따른 투표 mutation/결과, 좋아요, 페이지 댓글 | 투표 선택·결과, 그래프, 댓글 카드 |
| 시민 토론 목록/상세 | 투표와 유사한 목록·상세·참여·댓글 계약 | 토론 카드, 상태별 참여 UI, 댓글 |
| 정책반영 목록/상세 | 제안과 유사한 목록·상세, 처리 결과와 댓글 계약 | 처리 결과 카드, 댓글 및 목록 버튼 |
| 설문조사 목록/상세 | 상태·검색·정렬 query, 상세 및 설문 제출 | 상태 탭, 검색/정렬, 문항과 제출 결과 |
| 내 활동 | 내 정보와 유형별 활동 query, 유형별 상세 route 이동 | 전체 기본 필터, 유형별 결과 카드 |
| 신고 팝업 | 신고 사유와 대상 식별자를 mutation payload로 전달 | 사유 선택·확인·취소 팝업 |

## 제약 조건 및 미확인 사항

- 실제 endpoint namespace, 인증 필요 여부, 서버 envelope, 오류 코드, pagination shape가 미확정이다.
- 토론 참여 방식, 설문 문항 유형, 제안 작성 필드별 필수·길이·첨부 제한은 PDF만으로 API 계약을 확정할 수 없다.
- 목록 상태 값과 사용자 화면에서 허용할 상태 전이가 확정되지 않았다.
- mock을 개발 환경에서 자동 시작할지 환경 변수로 선택할지 결정이 필요하다.
- UI 완료 전 Hephaestus는 production UI 파일에 hook을 연결하지 않는다.

## 결론

기능 계층은 `entities`의 도메인 모델/전송, `features`의 query·mutation·form 동작, `pages`의 route 조립으로 분리하는 것이 적합하다. 상세 이동은 메모리 state가 아니라 공유·새로고침 가능한 URL parameter를 사용한다. 미확정 서버 계약은 임의로 고정하지 않고 `plan.md`의 승인 결정으로 남긴다.
