# Final Summary — 시민참여 관리자 Web UI 구현

## 결론

`시민참여v_4.8.pdf` p15~p43의 **관리자 화면 23종을 전부 구현**했다(p38은 사용자 Mobile 화면이라 범위 제외). FSD 레이어 계약을 유지했고, 타입·lint·빌드 및 브라우저 실렌더까지 확인했다.

## 화면 대응표

| PDF | 화면 | 라우트 |
| --- | --- | --- |
| p15 | 운영 대시보드 | `/cp/dashboard` |
| p16 | 메인 노출 관리 | `/cp/main-display` |
| p17·p18 | 시민제안 목록/상세처리 | `/cp/proposals`, `/cp/proposals/:id` |
| p19·p20 | 시민투표 목록/상세처리 | `/cp/votes`, `/cp/votes/:id` |
| p21·p22 | 시민토론 목록/상세처리 | `/cp/discussions`, `/cp/discussions/:id` |
| p23·p24 | 정책반영 목록/상세처리 | `/cp/policies`, `/cp/policies/:id` |
| p25·p26 | 설문조사 목록/상세처리 | `/cp/surveys`, `/cp/surveys/:id` |
| p27 | 댓글 통합 관리 | `/cp/comments` |
| p28·p29 | 신고 목록/상세처리 | `/cp/reports`, `/cp/reports/:id` |
| p30·p31 | 게시판 관리 / 게시글 상세처리 | `/cp/boards`, `/cp/boards/:id` |
| p32·p33 | 활동 로그 / 사용자 활동 상세 | `/cp/activity-logs`, `/cp/activity-logs/users/:userId` |
| p34 | 공지 등록/수정 | `/cp/boards/notices/:noticeId/edit` |
| p35 | 운영 정책 설정 | `/cp/operation-policy` |
| p36 | 보상/포인트 정책 설정 | `/cp/rewards/policy` |
| p37 | 보상/포인트 지급 관리 | `/cp/rewards` |
| p39~p43 | 팝업 5종 | 각 부모 화면 내 오버레이 |

## 레이아웃 수치 통일 (재설정 결과)

`shared/assets/css/_cp-admin.css`의 토큰이 단일 기준:
본문 max 1440 / padding 32 / 블록 gap 20 / 카드 padding 24·radius 12 / 필드·버튼 높이 40 / 버튼 min-width 120 / 상세 패널 360 / 목록 min-height 480 / 팝업 폭 540.

PDF 원본이 틀어져 있어 임의 재설정한 항목:
- KPI가 3개여도 4열 기준폭이 남던 문제 → 항목 수만큼 균등 분할
- 필터 필드 수(3~4)와 버튼 유무가 화면마다 달라 폭이 제각각 → 필드 `auto-fit(min 200px)` + 버튼 그룹 우측 고정
- p20 하단 액션 버튼이 라벨 없이 잘려 있던 것 → `목록으로`/`처리 저장` 표준 액션바로 복원
- p27·p28·p30·p32·p37에서 목록 **바깥 하단**에 떠 있던 상태 칩 → 조작 대상이 선택 행이므로 우측 상세 패널 내부로 이동
- p30에서 상세 패널에 가려지던 `등록일` 컬럼 → 2단 grid 분리 + 컬럼 폭 재산정
- p23·p25 목록/패널 하단선 불일치 → 목록 min-height + 패널 sticky
- p26 설문 정보 항목 간격 → 라벨폭 96px 고정 2열
- p34 노출 기간 두 필드 폭 불일치 → 동일폭 + 구분자 24px 고정
- GNB가 페이지마다 다름(p17~p33은 "메인 노출 관리" 누락) → 항목이 가장 많은 p36 기준 13항목 정본화

## 재사용 자산 활용

기존 자산 그대로 사용: `table`(전 목록) · `status`(상태 칩) · `dropdown` · `text-input` · `text-area` · `button` · `popup` · `pagination`/`no-results`(table 내장) · `calendar-picker`의 `DateRangeField`(기간 필터·노출기간) · `side-navigation` · `app-header` · `useApi`.

신규 자산은 PDF 전반에 반복되는 블록만 최소로 세웠다(shared 7 / widgets 5). `search-state-bar`는 탭+키워드 구조라 PDF의 n열 필터 폼과 계약이 맞지 않아 차용하지 않고 `FilterBar`를 별도로 두었다.

## 미결/후속 (다음 단계 권장)

1. **API 연동**: 각 entity의 `*.api.ts`는 엔드포인트 골격만 있고, 화면은 `model/*.fixture.ts` mock으로 구동한다. 스펙 확정 시 `*.dto.ts` + 파서 추가 후 fixture를 교체하면 된다.
2. **폼 검증**: 공지 등록(p34), 보상 정책(p36) 등 입력 화면에 zod+RHF 스키마 미적용. `ARCHITECTURE.md`의 폼 스택 계약에 따라 후속 적용 대상.
3. **권한 가드**: `app/router`의 `private-route`/`role-based-route`가 준비돼 있으나 이번 라우트에는 미적용(로그인 흐름 확정 후 연결).
4. **잔존 타입 오류 17건**: 전부 기존 파일(`select-users` 6, `event`/`news` DTO 6, `dao/table-rows` 2, `shared/ui` 3). `erasableSyntaxOnly` 정책과 함께 별도 정리 필요.
5. **보상 포인트 수치**: 협의 확정값 전제라 placeholder만 두고 임의 기본값을 넣지 않았다. 확정 시 fixture/스키마 반영 필요.
6. **p22 토론 상세**는 "결과 현황" 명칭을 유지했다(명칭 변경 지시는 p20 투표에 한정). 동일하게 맞출지 확인 필요.
