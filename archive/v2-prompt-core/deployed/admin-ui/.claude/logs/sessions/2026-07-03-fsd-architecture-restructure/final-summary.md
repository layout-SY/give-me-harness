# Final Summary — FSD 아키텍처 재설계

> 작성일: 2026-07-03
> 상세: `implementation-log.md` · `review-log.md` · 계약: `../../dependency/2026-07-03-fsd-layer-contract.md` · `src/ARCHITECTURE.md`

## What Changed
- **구조 전환**: 기술 유형별(apis/components/hooks/store/enums/utils) → **엄격 FSD 6레이어**(app·pages·widgets·features·entities·shared). src 최상위가 순수 레이어만 남음.
- **잔재 제거**: `ecommerce·videos·nft·parcel` 도메인 삭제, `item-category`→`items` 병합. nft는 전면 제거하되 유지 도메인(users·dao) 참조부는 `[nft-removed]` 주석 처리.
- **결합 #1 (pub-sub)**: `PubSubEvents`를 도메인-무지 `interface`로 전환 + 도메인 이벤트는 **선언 병합**으로 각 레이어(calendar-picker/dao) 소유.
- **결합 #2 (api registry)**: 전역 `~/apis` 집계 폐기 → **entity별 `<d>Api` singleton** + `useApi`는 `{execute,isLoading}` 순수 실행기.
- **shared 순수성**: table domain rows→entities, admin-role.util→admin entity, date.util 로컬 타입화로 shared의 상위-레이어 참조 제거.
- **문서화**: `src/ARCHITECTURE.md`(살아있는 계약) + 본 세션 산출물 + dependency 계약.

## Why It Changed
- 도메인이 여러 최상위 폴더에 흩어져 응집도가 낮고, shared 계층이 전 도메인을 아는 역방향 결합이 존재.
- 이전 프로젝트 복붙 잔재가 다수 포함.
- 목표: 레이어 단방향 의존 + shared 도메인-무지 + 슬라이스 격리.

## Reused Assets
- 기존 공용 컴포넌트/훅/유틸 전량 보존(이동만) — `shared/ui`, `shared/lib`.
- `createApiClient`/`ApiResult` 계약(`2026-05-21-api-result-contract`) 유지, 위치만 `shared/api`로.
- 도메인 API factory 모듈 재사용 — 래핑만 entity singleton으로.

## Impacted Areas
- **전 src 트리**: 파일 이동 + `~/` import 대규모 remap(293 파일).
- **규약 변경**: api 접근 `useApi().api.x()` → `import { <d>Api }` + `execute(() => <d>Api.x())`.
- **진입점**: `main.tsx`→`app/index.tsx`, `index.html` script src 변경.

## Remaining Risks
- **git 미사용**: 롤백 수단 없음 → `git init`+커밋 권장.
- **cross-entity type 2건**: profile→admin, usage→sales (type-only).
- **라우터 미배선**: `App.tsx`는 Vite 템플릿 잔존(페이지 부재).
- **선재 이슈**: `erasableSyntaxOnly` tsc 16건 / eslint any·unused (재설계 무관, 별도 정리 대상).

## Follow-up Suggestions
1. cross-entity enum(ADMIN_ROLE_TYPE_CODES, TRANSACTION_*) → `shared/config/enums` 승격.
2. `pages/` 생성 + `app/router` RouterProvider 배선(가드 준비 완료).
3. entity 루트 `index.ts`(api/model/ui 통합 배럴) 정비.
4. `[nft-removed]` 주석 최종 제거 여부 확정.
5. `reference/custom-hooks` SKILL: `jotai`→`zustand` 정정 + api 접근 규약(ADR-1) 반영.
6. ESLint FSD 경계 강제(`eslint-plugin-boundaries`) 도입 검토.
7. `erasableSyntaxOnly` 정책 유지/완화 결정.
