---
name: reference-ui-library-heroui-react
description: admin-ui에서 HeroUI(@heroui/react)를 공용 어댑터(Button, IconButton, Modal, TextInput)로 사용할 때의 계약과 사용법
---

# HeroUI 사용 계약

## 목적과 적용 범위

- **요구·선택 이유**: admin-ui의 버튼, 아이콘 버튼, 모달, 입력 기본 요소를 HeroUI v3로 렌더링한다. 이미 도입된 의존성이며, 이번 작업에서 새로 도입하지 않았다.
- **대상 프로젝트**: `asan-metaverse-admin-ui`만. 다른 소비자에 같은 어댑터가 있다고 가정하지 않는다.
- **적용 화면(이번 작업)**: 튜토리얼 목록·편집 화면, `features/image-manager`의 순서 이동 버튼, 미리보기 모달.
- **제외**: 기능 코드에서 `@heroui/react`를 직접 import하는 것.
- **문서 상태**: 구현 확인(2026-10-02, `npm run lint`·`npm run build` 통과). 중앙 등록 전이다.
- **실제 사용처(이번 작업)**: `src/pages/tutorial/ui/tutorial-{list,editor}-view.tsx`(Button, TextInput, Modal), `src/features/image-manager/ui/ImageManager.tsx`(IconButton)

## 버전과 근거

- **패키지**: `@heroui/react`. 선언은 `^3.2.3`, `package-lock.json` 설치 버전은 `3.2.4`.
- **스타일 진입점**: `src/app/styles/heroui.css`(`@import "@heroui/react/styles"`). `src/app/index.tsx`에서 import한다.
- **조사한 어댑터**(2026-10-02, `feature/tutorial` HEAD `987616b`)
  - `src/shared/ui/button/button.tsx`
  - `src/shared/ui/icon-button/icon-button.tsx`
  - `src/shared/ui/modal/modal.tsx`
  - `src/shared/ui/text-input/text-input.tsx`(`InputGroup`)
- **공식 문서**: 이번 세션에서 확인하지 않았다. 계약은 실제 어댑터 코드 기준이다.

## 구현 방식과 계약

- **의존 경계**: 기능 코드는 `~/shared/ui/{button/button,icon-button/icon-button,modal,text-input/text-input}`의 default export만 사용한다.
- **Button**
  - props: `isLoading`, `disabled`, `type`, `title`, `className`, `children`, `onClick`, `fullWidth`(기본 true)
  - HeroUI 매핑: `isPending`, `isDisabled`, `aria-label`, `variant`, `onPress`
  - `className` 토큰 `primary`, `secondary`, `outline`, `cancel`, `ghost`, `danger`가 variant로 바뀐다. 매핑되지 않는 값은 `primary`가 된다.
- **IconButton**
  - `isIconOnly` 버튼이다. 기본 variant는 `secondary`.
  - 접근성 이름은 `title`로 전달한다(`aria-label`). `onClick`은 인자가 없다.
- **Modal**
  - props: `open`, `close`, `children`, `className`
  - HeroUI 매핑: `Modal.Root isOpen`, `onOpenChange(false)`일 때 `close()`
  - ESC와 백드롭 클릭으로 닫히는 것은 HeroUI 기본 동작이다.
- **상태 소유권**: 열림·비활성·로딩 상태는 호출부(controller)가 소유한다. 어댑터는 controlled로만 동작한다.

## 사용법

```tsx
import Button from "~/shared/ui/button/button";
import IconButton from "~/shared/ui/icon-button/icon-button";
import Modal from "~/shared/ui/modal";

<Button className="primary" fullWidth={false} isLoading={isSaving} disabled={!canSave} onClick={onSave}>저장</Button>
<IconButton className="ghost" title="앞으로 이동" disabled={isFirst} onClick={onMovePrev}>{chevronLeftIcon}</IconButton>
<Modal open={url !== null} close={onClose}><img src={url ?? ""} alt="미리보기" /></Modal>
```

잘못 쓰기 쉬운 점:
- `onClick`은 HeroUI `onPress`로 연결된다. 이벤트 객체를 받지 않으므로 `stopPropagation`이 필요한 위치에는 네이티브 `button`을 쓴다.
- 기본값이 `fullWidth=true`라서 버튼을 나란히 둘 때는 `fullWidth={false}`를 준다.

## 제약과 검증

- 검증 방법: `npm run build`(타입), `npm run lint`. 시각 QA는 사용자 요청 시에만 한다.
- 미확정: 공식 문서와 대조하지 않았다. 어댑터 계약이 바뀌면 이 문서를 갱신한다.

## 중앙 등록·갱신

- **세션 초안**: `.claude/logs/sessions/튜토리얼-관리-UI/unknown/ui-library-skills/heroui-react/SKILL.md`. 자산 선정 문서는 `../../ui-asset-plan.md`.
- **대상 중앙 경로**: `policy/common/skills/reference/libraries/heroui-react/SKILL.md`. 기존 정본은 없다.
- **상태**: 미등록. 중앙 저장소 작업으로 인계한다.
