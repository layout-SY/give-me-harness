# Final Summary

## What Changed
- `src/components/image-manager/` 신규 생성 — 도메인 독립 이미지 관리 시스템
- `src/components/image-slot-item/imageSlotItem.tsx` → re-export shim으로 교체
- `imagesSection.tsx` — `ImageSlots(variant=dtos)` → `ImageManager + useDaoProposalImageBridge`로 교체
- `detail/_id.modal.tsx` — `useDaoProposalImageUpload` 제거, `api.dao.uploadDaoProposalImage` prop 주입 방식으로 전환
- 레거시 `imageSlots.tsx`, `imageSlots.css`, `useImageUpload.ts` 삭제

## Why It Changed
- 기존 `useImageUpload`가 `api.dao`에 하드코딩되어 다른 도메인 재사용 불가
- `ImageSlots`의 `variant: "urls" | "dtos"` 혼재 설계가 관심사 분리 위반
- pubsub으로 팝업 열고 닫는 간접 통신 → hidden file input 직접 처리로 단순화
- 프로젝트 내 `useFetchAdapter`의 `fetchApi` 주입 패턴과 일관성 확보

## Reused Assets
- `sortDaoProposalImages`, `DAO_PROPOSAL_MAX_IMAGE_COUNT` (`image.util.ts`)
- `useApi`, `SCOPE.WEB`, `useDialog`, `useLanguage`
- `add-photo-alternative.icon`, `close.icon`, `upload.icon`

## Impacted Areas
- `src/pages/dao/proposal-manage/detail/` — ImagesSection, _id.modal.tsx
- `src/components/image-slot-item/` — re-export shim (기존 import 경로 하위호환 유지)

## Remaining Risks
- `src/pages/dao/proposal-manage/create/_id.modal.tsx` — 인라인 이미지 업로드 로직이 ImageManager 미적용 상태. 별도 후속 작업 필요.
- `src/pages/manage/items/_id.modal.tsx`, `inquiries/_id.modal.tsx` — 여전히 pubsub 기반. 이번 범위 밖.
- `image.util.ts`의 일부 유틸(`removeDaoProposalImageUrlAtIndex` 등) 사용처 소멸 → 불필요 코드로 잔존. evaluator 레벨 정리 필요.

## Follow-up Suggestions
1. `create/_id.modal.tsx` 이미지 업로드를 `ImageManager`로 교체
2. `items`, `inquiries` 도메인에도 `ImageManager` 도입 검토 (uploadApi만 교체하면 됨)
3. `image.util.ts` 미사용 유틸 정리
4. `image-slot-item/` 디렉토리 — 장기적으로 shim 제거 후 `image-manager` 경로 직접 참조로 전환
