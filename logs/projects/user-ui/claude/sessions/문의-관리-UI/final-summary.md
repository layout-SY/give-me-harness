# 문의 관리 UI 최종 요약

## 변경
- 공용화: `src/shared/ui/screen/`(`page-screen`, `screen-header`, `detail-head`, `bottom-action-bar`, `screen.css`), `src/shared/ui/content/`(`content-card`, `section-block`, `meta-line`, `content.css`), `src/shared/ui/field-group/`(`field-group`, `field-group.css`)
  - 시민참여의 기존 8개 부품 파일은 `git rm`으로 삭제(staged), 13개 페이지 import와 `CitizenScreen` → `PageScreen`으로 교체
  - 시민참여 전용 CSS 규칙은 기존 파일에 남기고, 해당 클래스를 쓰는 부품·페이지에서 직접 import
  - 클래스 이름(`cp-*`)은 기존 테스트·스타일 호환을 위해 유지
- 문의 UI: `src/features/inquiry/ui/`(`InquiryListPage`, `InquiryDetailPage`, `InquiryWritePage`, `inquiryStatus`)
- 연결: `src/pages/manage/`(`ui/InquiryRoutes.tsx`, `model/presentation.ts`, `index.ts`), `src/shared/config/manageRoutes.ts`, `src/app/routing.ts`
- 테스트: `src/pages/manage/ui/InquiryRoutes.test.tsx`, `src/app/routing.test.ts`에 `/manage` 경로 추가

## 검증 결과
- `npm run lint`: 통과
- `npm run build`: 통과
- `npm run test`: 신규 문의·라우팅 테스트 통과. 전체에서 기존 13건 실패(투표·토론 API/MSW의 `AGREE|DISAGREE` 선택값 불일치 등, 이번 변경 파일과 무관)

## 미완료·제한
- 드롭다운(HeroUI Select)에 id를 넘길 수 없어 `FieldGroup` label의 `htmlFor`가 드롭다운에 연결되지 않음(aria-label은 placeholder로 제공)
- Git commit은 수행하지 않음(삭제 8건만 staged)
