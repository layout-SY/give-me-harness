# Plan

## Request Summary
- DAO 제안 이미지 업로드 관련 컴포넌트/훅을 도메인 독립적인 `ImageManager` 시스템으로 재구성
- 모든 도메인에서 `uploadApi: (formData: FormData) => Promise<string>` 하나만 주입하면 재사용 가능한 구조

## Work Type
- hybrid (refactor + feature)

## Scope
- `src/components/image-manager/` 디렉토리 신규 생성
- `src/components/image-slot-item/imageSlotItem.tsx` → re-export shim으로 교체
- `src/pages/dao/proposal-manage/hooks/useDaoProposalImageBridge.ts` 신규 생성
- `src/pages/dao/proposal-manage/detail/components/sections/imagesSection.tsx` 수정
- `src/pages/dao/proposal-manage/detail/_id.modal.tsx` 수정
- `src/pages/dao/proposal-manage/components/image-slots/imageSlots.tsx` + `imageSlots.css` 삭제
- `src/pages/dao/proposal-manage/hooks/useImageUpload.ts` 삭제 (레거시 dead code)

## Out of Scope
- `src/pages/dao/proposal-manage/create/_id.modal.tsx` (별도 후속 작업)
- `src/pages/manage/items/_id.modal.tsx` (pubsub 패턴 유지)
- `src/pages/manage/operations/inquiries/_id.modal.tsx` (pubsub 패턴 유지)
- `src/components/image-upload/image-upload.tsx` (전역 pubsub 컴포넌트 보존)
- `PubSubEvents`의 `open-image-upload-popup` 항목 (다른 사용처 존재)

## Sections
1. S1 — `image-manager/types.ts` 공통 타입 정의
2. S2 — `ImageSlotItem` 이동 + re-export shim
3. S3 — `ImageSlotAdd` 신규 생성 (hidden file input + 버튼)
4. S4 — `useImageUpload` 신규 (uploadApi 주입, pubsub 무관)
5. S5 — `useImageSlots` 신규 (add/remove → onChange)
6. S6 — `ImageManager` 최상위 컴포넌트 생성
7. S7 — `index.ts` public API 정의
8. S8 — `useDaoProposalImageBridge` 신규 (DTO ↔ URL 변환)
9. S9 — `ImagesSection` 수정 (ImageSlots → ImageManager)
10. S10 — `_id.modal.tsx` 수정 (uploadApi prop 주입)
11. S11 — 레거시 파일 삭제 (imageSlots, useImageUpload)

## Required Agents
- planner (계획 수립 및 결정사항 도출)
- generator (S1~S10 구현)
- refactorer (S2 이동, S11 삭제)
- watcher (구현 검증)

## Required Skills
- coding-convention/SKILL.md
- refactoring/SKILL.md

## Risks / Assumptions
- `open-image-upload-popup` pubsub 이벤트는 3곳에서 여전히 사용 중 → 전역 컴포넌트/이벤트 보존 필수
- `DaoProposalImageDto`의 `id` 필드: 신규 URL 추가 시 id 없는 상태로 DTO 구성 → sortOrder만 재계산
- `imageAlt`: i18n 없이 `이미지 N` 자동 생성으로 확정
- `useApi()` 위치: `_id.modal.tsx`에서 `uploadApi` prop으로 주입 (ImagesSection 순수 유지)
- 기존 `image-slot-item/` 경로: re-export shim으로 하위호환 유지

## Approval Request
이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?
