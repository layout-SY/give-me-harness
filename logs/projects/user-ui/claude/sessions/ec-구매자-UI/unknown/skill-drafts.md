# 중앙 정책 반영용 스킬 문서 초안 (UI 라이브러리)

> 이 세션은 중앙 정책을 수정할 수 없다. 아래 초안을 중앙 저장소의 `reference` 스킬(예: `reference/ui-library-usage/SKILL.md`)로 옮기는 것을 제안한다. 경로·구조는 중앙 승인 절차에서 확정한다.

---

## 1. embla-carousel-react (신규 추가, ^8.6.0)

```yaml
name: reference-embla-carousel
description: 이미지나 카드를 가로로 넘기는 캐러셀·스와이프 UI가 필요할 때 shared ImageCarousel 어댑터로 구현한다.
```

### 이런 작업일 때 사용한다
- 여러 장의 이미지를 좌우 스와이프로 넘겨야 할 때(상품 대표 이미지, 전체 보기 모달)
- 한 화면 폭 단위로 스냅되는 가로 목록이 필요할 때

### 사용하지 않는다
- 단순 가로 스크롤 칩·탭 → CSS `overflow-x: auto`(`ChipGroup layout="scroll"`)
- 한 장짜리 이미지 확대 → 기존 전역 `ImageModal`(pubsub `open-image`)

### 라이브러리 설명
- 스타일이 없는 headless 캐러셀 엔진(약 7KB gzip). 드래그·스냅·루프·정렬 옵션만 제공하고 마크업·CSS는 프로젝트가 소유한다.
- `useEmblaCarousel(options)` → `[viewportRef, api]`. `api.scrollTo/scrollNext/scrollPrev/selectedScrollSnap()`, 이벤트 `select`, `reInit`.
- 드래그 후 발생하는 click은 엔진이 막아 준다(이미지 클릭과 스와이프가 충돌하지 않음).

### 프로젝트 어댑터
- `src/shared/ui/image-carousel/image-carousel.tsx` — `images`, `label`, `startIndex`, `fit(cover|contain)`, `onIndexChange`, `onImageClick`, `overlay`
- `src/shared/ui/image-carousel/image-frame.tsx` — 1:1 이미지 프레임(출처 정책·로드 실패 대체). 목록 카드와 캐러셀이 공유
- `src/shared/ui/image-gallery-modal/image-gallery-modal.tsx` — 제어형 전체 보기 모달(`open`, `images`, `startIndex`, `onClose`)
- 기능 코드는 `embla-carousel-react`를 직접 import하지 않는다.

### 주의
- 접근성: 영역 `role="region"`+`aria-roledescription="carousel"`, 슬라이드 `role="group"`, 점 버튼에 `aria-current`, viewport 방향키 이동.
- 레이아웃 속성 애니메이션 금지(DESIGN.md) — 점 표시 등은 전환 없이 상태만 바꾼다.
- 테스트(jsdom)는 `matchMedia`·`ResizeObserver`·`IntersectionObserver` stub이 필요하다(`image-gallery-modal.test.tsx` 참고).

---

## 2. HeroUI v3 어댑터 (기설치, 이번에 새로 감싼 컴포넌트)

```yaml
name: reference-heroui-adapters
description: 펼침 목록·수량 입력·칩 선택이 필요할 때 HeroUI를 직접 쓰지 않고 shared 어댑터를 사용한다.
```

| 목적 | 어댑터 | HeroUI 원본 | 핵심 props |
| --- | --- | --- | --- |
| 펼침·접힘 목록(FAQ, 상품 안내) | `shared/ui/accordion` | `Accordion` (React Aria Disclosure) | `items{id,title,content}`, `variant(divided|card)`, `marker`, `allowsMultipleExpanded` |
| 수량 −/+ | `shared/ui/quantity-stepper` | `NumberField` | `value`, `label`, `min`, `max`, `disabled`, `onChange` |
| 단일 선택 칩(카테고리, 유형) | `shared/ui/chip-group` | `TagGroup` + `Tag` (selectionMode single) | `items{label,value}`, `value`, `label`, `layout(scroll|wrap)`, `onChange` |

- 카드형 라디오(결제 수단)는 HeroUI Radio 하위 구조 대신 `react-aria-components`의 `RadioGroup`/`Radio`를 `shared/ui/choice-card-group`에서 감쌌다.
- HeroUI 기본 스타일 위에 어댑터 클래스(`.chip-group .chip-group__chip` 등 2단계 선택자)로 덮어쓴다. 색은 `--accent`만 참조한다.

---

## 3. lucide-react (기설치)

- 인터페이스 아이콘은 `lucide-react`를 사용한다(이모지 금지). 장식 아이콘은 `aria-hidden="true"`, 아이콘만 있는 버튼은 `IconButton`에 `aria-label`.
- 기존 `src/shared/assets/icons/*` SVG와 같은 의미의 아이콘이 있으면 기존 자산을 우선할지는 중앙 정책에서 결정이 필요하다(이번 작업은 lucide로 통일).

---

## 4. 외부 라이브러리를 쓰지 않은 항목(참고)

- 주문 진행 단계: 스테퍼 라이브러리 대신 `shared/ui/progress-steps` 자체 구현(`<ol>`, `aria-current="step"`). 기존 라이브러리들은 유지보수 중단 또는 스타일 재정의 비용이 커서 제외.
