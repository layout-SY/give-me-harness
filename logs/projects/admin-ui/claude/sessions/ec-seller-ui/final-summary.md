# 최종 요약 — EC 판매자 UI

## 결론

Figma `해커톤, EC` 판매자 섹션을 `/ec/*` 화이트 모드 UI로 구현했다. `feature/ec-seller-ui` worktree에 미커밋 상태로 있다. 대시보드는 빈 페이지만 있다. 데이터는 비어 있고, View props 계약만 정의했다. 미확인 쓰기 기록이 외부에서 해소된 뒤 공통 포맷 트리거로 Prettier 포맷을 완료했다. 포맷 결과를 기준으로 lint·build를 다시 실행해 통과했다.

## 결정 (사용자 확정)

- 입점 신청: 사업자 번호를 제거했다.
- 모드: 입점 신청·승인 대기·주문 상세를 화이트 모드로 구현했다.
- 대시보드: 구현을 보류했다.
- 주문 상세: 두 프레임을 합쳤다. 배송 정보가 없으면 입력 카드를, 있으면 진행 현황표를 보여준다.
- 문의: 목록과 상세 모두 두 프레임을 합쳤다. 매출 3개 화면은 각각 유지했다.
- 사이드바 메뉴: 대시보드 / 상품 관리 / 주문 관리 / 문의 관리 / 정산 관리 / 설정
- 임시 데이터: 넣지 않았다.
- 리치 텍스트 입력: `TextArea`만 쓰고 툴바는 뺐다.
- 작업 위치: 별도 브랜치와 worktree에서 진행했다.

## 실제 변경

- **공용 사이드바**(4개 기존 셸 포함):
  - 흰 테마, 브랜드 구분선, 부모 탭은 펼침 전용(▼/▲ + bold)
  - 활성 경로는 가장 길게 일치하는 링크로 판정
  - 콘텐츠 영역과 border·배경으로 분리, `footer` prop 추가
- **공용 UI 신규**: `shared/ui/trend-badge`, `shared/ui/filter-tabs`(underline·pill), `shared/assets/icons/line-icons.ts`
- **공용 UI 확장**: `KpiCard`에 icon·trend 추가, `ChoiceChipGroup`의 배열 값(다중 선택) 지원
- **EC 위젯**: `widgets/ec-seller` — 테이블 카드·셀·필드·선택 박스·차트 영역·프로필·증감 캡션·계약 타입·포맷 함수
- **페이지**: `pages/ec-seller-apply`, `ec-dashboard`, `ec-product`, `ec-order`, `ec-inquiry`, `ec-settlement`, `ec-settings`
- **라우트·셸**: `routes.tsx`, `ec-seller-shell.tsx`, `ec-apply-shell.tsx`, `_navigation8.ts`

## 검증

- `tsc --noEmit`: 통과
- `npm run lint`: 통과
- `npm run build`: 통과. chunk 크기 경고는 기존부터 있던 것이다.
- 공통 포맷 트리거(`formatting.py apply`): 기록이 해소된 뒤 실행해 완료했다. 대상은 변경 파일 88개이고, 제외된 파일은 없다.
- 브라우저 확인: 요청이 없어 하지 않았다.

## 미완료

1. Prettier 포맷: 완료했다.
2. commit: 완료했다. `feature/ec-seller-ui`의 `b6fc92d`로, 89 files changed이며 부모는 `bc579b3`이다. 커밋 후 작업 트리는 깨끗하다. `sy-main` 병합은 아직 요청받지 않았다.
3. **중앙 등록**: 증감 뱃지 정책 스킬과 lucide-react·heroui 라이브러리 스킬은 세션 초안까지만 작성했다.
4. **기존 화면 필터 UI 일괄 교체**: EC 적용 결과를 확인한 뒤 진행하기로 했다.
5. **Logic 연결**: [handoff.md](handoff.md) 참고

## 완료 점검 (2026-10-02)

- Logic 연결: 다른 작업에서 `bbb337d`(feat(ec): 판매자 API와 MSW 연결)로 page를 controller에 연결했다. UI 계약 파일(`*.types.ts`)과 View는 그대로다.
- 검증(worktree 기준):
  - `npm run lint`: 통과
  - `npm run build`: 통과
  - `node --test tests/ec-seller-api.test.mjs tests/mock-api-policy.test.mjs`: 17/17 통과
  - 처음 실행에서 1건 실패했는데, 기본 checkout을 기준으로 vite를 띄운 실행 위치 오류였다.
- 정리 후보: `EC_ORDER_LIST_EMPTY_PROPS`, `EC_INQUIRY_LIST_EMPTY_PROPS`는 정의만 남고 쓰이지 않는다.
- `sy-main` 병합(2026-10-02): `8fceaf9 merge: feature/ec-seller-ui 작업을 sy-main에 통합`
  - 진행 순서: 관계 등록(op `9f3af62a…`, 부모 `sy-main`, fork `bc579b3`) → 검토(review `08b91bfe…`, merge 전략) → 완료(op `c3f71815…`)
  - 병합 결과: `npm run lint`, `npm run build` 모두 exit 0, `verification_passed: true`
  - 정리 요청이 없어 stage는 `retained`. branch·worktree를 보존했다.
  - 형제 `feature/tutorial`은 이후 병합할 때 `routes.tsx`의 `/manage` 주석 줄 근처 충돌 가능성을 확인해야 한다.
- 남은 작업:
  - 정책·라이브러리 스킬 중앙 등록
  - 기존 화면 필터 UI 일괄 교체(사용자 판단)
