# Implementation Log

## Task Summary
DAO 제안 이미지 업로드 파편화된 구조를 `src/components/image-manager/` 기반의 도메인 독립 시스템으로 재구성.
`uploadApi` 주입 패턴(useFetchAdapter와 동일 컨벤션)으로 도메인 교체 가능하도록 설계.

## Reused Assets
- `src/assets/icons/add-photo-alternative.icon` — ImageSlotAdd 버튼 아이콘
- `src/assets/icons/close.icon` — ImageSlotItem 삭제 버튼 아이콘
- `src/assets/icons/upload.icon` — ImageSlotItem overlay 아이콘
- `src/hooks/use-api.tsx` — execute, useApi 패턴
- `src/hooks/use-language` — mui 다국어
- `src/modules/dialog` — useDialog (MIME 오류 알림)
- `src/enums/common.enum` — SCOPE.WEB (FormData type 값)
- `src/pages/dao/proposal-manage/utils/image.util.ts` — sortDaoProposalImages, DAO_PROPOSAL_MAX_IMAGE_COUNT

## New Files / Updated Files

### 신규 생성
| 파일 | 역할 |
|---|---|
| `src/components/image-manager/index.ts` | public API export |
| `src/components/image-manager/types.ts` | `UploadApiFunction`, `ImageManagerProps` 타입 정의 |
| `src/components/image-manager/ImageManager.tsx` | controlled 최상위 컴포넌트 |
| `src/components/image-manager/ImageManager.css` | 슬롯 레이아웃 스타일 |
| `src/components/image-manager/components/ImageSlotItem.tsx` | 단일 슬롯 (조회/편집 모드) |
| `src/components/image-manager/components/ImageSlotItem.css` | 슬롯 스타일 |
| `src/components/image-manager/components/ImageSlotAdd.tsx` | "+" 버튼 + hidden file input |
| `src/components/image-manager/components/ImageSlotAdd.css` | 추가 버튼 스타일 |
| `src/components/image-manager/hooks/useImageUpload.tsx` | MIME 검증 + FormData 구성 + execute |
| `src/components/image-manager/hooks/useImageSlots.ts` | add/remove → onChange |
| `src/pages/dao/proposal-manage/hooks/useDaoProposalImageBridge.ts` | DTO ↔ URL 변환 브릿지 |

### 수정
| 파일 | 변경 내용 |
|---|---|
| `src/components/image-slot-item/imageSlotItem.tsx` | re-export shim으로 교체 (하위호환 유지) |
| `src/pages/dao/proposal-manage/detail/components/sections/imagesSection.tsx` | `ImageSlots` → `ImageManager` + `useDaoProposalImageBridge`. `onAddImage` prop 제거, `uploadApi` prop 추가 |
| `src/pages/dao/proposal-manage/detail/_id.modal.tsx` | `useDaoProposalImageUpload` 제거, `api.dao.uploadDaoProposalImage`를 `uploadApi`로 주입 |

### 삭제
| 파일 | 이유 |
|---|---|
| `src/pages/dao/proposal-manage/components/image-slots/imageSlots.tsx` | ImageManager로 대체 완료 |
| `src/pages/dao/proposal-manage/components/image-slots/imageSlots.css` | 스타일 image-manager로 통합 |
| `src/pages/dao/proposal-manage/hooks/useImageUpload.ts` | dead code (pubsub 의존 레거시) |

## Key Logic

### uploadApi 주입 패턴
```ts
// 호출부 (_id.modal.tsx)
const { api } = useApi();
<ImagesSection uploadApi={api.dao.uploadDaoProposalImage} ... />

// useImageUpload 내부
const formData = new FormData();
formData.append("file", file);
formData.append("type", scope);   // SCOPE.WEB
const url = await execute(() => uploadApi(formData));
```

### DTO ↔ URL 브릿지
```ts
// URL → DTO 역변환 시 기존 id 보존, sortOrder 재계산
const next = newUrls.map((url, sortOrder) => {
  const existing = dtos.find(d => d.imageUrl === url);
  return existing ? { ...existing, sortOrder } : { imageUrl: url, sortOrder };
});
```

### imageAlt 자동 생성
- `이미지 ${index + 1}` — i18n 비의존

## Validation / Request Handling
- MIME 검증: `accept` 배열 기반, 실패 시 `Dialog.alert` 표시
- 업로드 실패: `execute`의 기본 에러 핸들링에 위임 (Dialog.alert 자동 표시)
- 동일 파일 재선택: `onChange` 후 input value 초기화 처리

## Risks
- `create/_id.modal.tsx`의 인라인 이미지 업로드는 ImageManager 미적용 상태 → 별도 후속 작업 필요
- `useDaoProposalImageUpload` 훅 삭제로 인해 해당 훅을 직접 참조하던 코드가 있었다면 빌드 오류 발생 가능 → tsc 검증으로 확인 완료 (0건)
- `DaoProposalImageDto`의 `id` 없는 신규 항목 → API 서버에서 id 생성 예정이므로 클라이언트에서는 `imageUrl` + `sortOrder`만 전송

## Handoff Note
- Ready for watcher review
