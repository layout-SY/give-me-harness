# Exploration

## Target Paths
- `src/components/image-slot-item/`
- `src/pages/dao/proposal-manage/components/image-slots/`
- `src/pages/dao/proposal-manage/hooks/useImageUpload.ts`
- `src/pages/dao/proposal-manage/detail/components/sections/imagesSection.tsx`
- `src/components/image-upload/` (전역 pubsub 업로드 팝업)
- `src/hooks/use-api.tsx`
- `src/components/table/hooks/useFetchAdapter.ts` (API 주입 패턴 참조)

## Existing Reusable Assets Found

- **Found**: `src/components/image-slot-item/imageSlotItem.tsx`
  - **Suggested Reuse**: `image-manager/components/ImageSlotItem.tsx`로 이동 후 그대로 활용
  - **Reason**: props 시그니처 변경 없이 재사용 가능

- **Found**: `src/pages/dao/proposal-manage/utils/image.util.ts`
  - `sortDaoProposalImages`, `DAO_PROPOSAL_MAX_IMAGE_COUNT`
  - **Suggested Reuse**: `useDaoProposalImageBridge`에서 import하여 그대로 활용
  - **Reason**: DAO 도메인 유틸이므로 image-manager로 이동하지 않고 원위치 유지

- **Found**: `useFetchAdapter.ts`의 `fetchApi` 주입 패턴
  - **Suggested Reuse**: `uploadApi: (formData: FormData) => Promise<string>` 동일 패턴 적용
  - **Reason**: 프로젝트 내 확립된 API 주입 컨벤션

- **Found**: `src/assets/icons/add-photo-alternative.icon`, `close.icon`, `upload.icon`
  - **Suggested Reuse**: `ImageSlotAdd`, `ImageSlotItem`에서 그대로 사용

## Assets Not Suitable for Reuse

- **Asset**: `src/pages/dao/proposal-manage/hooks/useImageUpload.ts`
  - **Why**: `api.dao` 하드코딩 + pubsub 의존 → 도메인 독립 시스템 설계와 충돌. 삭제 대상.

- **Asset**: `src/pages/dao/proposal-manage/components/image-slots/imageSlots.tsx`
  - **Why**: `variant: "urls" | "dtos"` 혼재 설계 → 관심사 분리 위반. ImageManager로 대체 후 삭제.

## pubsub 의존성 현황 (scope 판단 근거)

`open-image-upload-popup` 이벤트 사용처:
- `hooks/useImageUpload.ts` → 이번 작업에서 제거 (파일 삭제)
- `create/_id.modal.tsx` → 범위 밖, 유지
- `manage/items/_id.modal.tsx` → 범위 밖, 유지
- `manage/operations/inquiries/_id.modal.tsx` → 범위 밖, 유지

→ 전역 `ImageUploadPopup` 컴포넌트와 pubsub 이벤트는 보존 필수

## New Asset Necessity

- **Needed**: `src/components/image-manager/` 전체 디렉토리
  - **Why**: 도메인 독립 이미지 관리 시스템. 기존 컴포넌트 없음.

- **Needed**: `src/pages/dao/proposal-manage/hooks/useDaoProposalImageBridge.ts`
  - **Why**: `ImageManager`(string[]) ↔ `DaoProposalImageDto[]` 변환 레이어. DAO 도메인 전용.
