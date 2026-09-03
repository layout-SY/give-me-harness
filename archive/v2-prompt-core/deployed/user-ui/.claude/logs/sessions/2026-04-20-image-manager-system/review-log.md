# Review Log

## Review Target
- `src/components/image-manager/` 전체 신규 파일
- `src/pages/dao/proposal-manage/hooks/useDaoProposalImageBridge.ts`
- `src/pages/dao/proposal-manage/detail/components/sections/imagesSection.tsx`
- `src/pages/dao/proposal-manage/detail/_id.modal.tsx`
- `src/components/image-slot-item/imageSlotItem.tsx` (shim)

## Result
- 1차: **fail** (2개 항목)
- 2차: **pass**

## Checklist Review
- SKILL compliance: 통과 — uploadApi 주입 패턴, BEM CSS 클래스명 준수
- Reuse check: 통과 — sortDaoProposalImages, SCOPE, useApi 등 기존 자산 활용
- Validation check: 통과 — MIME 검증, upload 실패 시 상태 미변경
- Payload completeness: 통과 — FormData에 file + type(SCOPE.WEB) 포함
- Performance concern: 해당없음
- Duplicate code concern: 통과 — imageSlots 레거시 제거 완료

## Violations

### 1차 검토 위반 항목

**V-01 (major) — useImageUpload.ts 미삭제**
- `src/pages/dao/proposal-manage/hooks/useImageUpload.ts` 삭제 지시됐으나 잔존
- 이유: 어디서도 import되지 않는 dead code + pubsub 의존 레거시 로직 잔존
- 조치: 파일 삭제 → 해소됨

**V-02 (minor) — image-manager__footer dead CSS**
- `ImageManager.css`에 `.image-manager__footer` 정의됐으나 JSX에 해당 요소 없음
- 이유: footer 기능이 확정 설계에 포함되지 않았으나 CSS만 미리 작성됨
- 조치: CSS 블록 제거 → 해소됨

### 2차 검토
- 위반 항목 없음

## Required Fixes
1. ~~`src/pages/dao/proposal-manage/hooks/useImageUpload.ts` 삭제~~ → 완료
2. ~~`ImageManager.css`의 `.image-manager__footer` CSS 제거~~ → 완료

## Repeat Issue
- false

## Escalation
- none
