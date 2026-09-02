# 인계

## 목표 및 현재 상태

`ADM_CP_MAIN_DISPLAY_WEB`(화면정의서 p16 / Figma P019) `DEF_ROW_07 「노출 설정」`의 정의는
"선택 항목의 노출 여부**와 순서 변경**"이나, 기존 구현은 노출 여부만 제어형이고 순서는
읽기 전용 텍스트였다.

UI에 순서 이동 컨트롤과 제어형 계약을 추가했다. **마크업·스타일·props 계약까지 완료**이며,
실제 재정렬·저장 로직은 hook 영역이라 미배선 상태다. 현재 순서 이동 버튼은 항상 비활성으로
렌더된다(`canMoveUp`/`canMoveDown`이 `undefined`).

이 화면은 **기능 배선까지 끝난 뒤 한 번에 merge**하기로 했으므로, 아직 `sy-main`에
반영되지 않았고 반영해서도 안 된다. 상세는 아래 「작업 브랜치와 merge 방침」 참조.

## 완료된 작업

- `model/cp-main-display.types.ts`
  - `CpMainDisplayOrderDirection` (`"UP" | "DOWN"`) 타입 추가·export
  - `CpMainDisplayProcessController`에 `canMoveUp` / `canMoveDown` / `onOrderChange` 추가
- `ui/cp-main-display-view.tsx`
  - 「선택 항목 노출 설정」 카드의 `순서 {order}` 텍스트를 `↑ / 현재순서 / ↓` 컨트롤로 교체
  - 각 버튼에 `title`(→ `aria-label`) 부여: "순서 위로" / "순서 아래로"
- `ui/cp-main-display-view.css`
  - `.cp-display-setting__order`를 라벨+컨트롤 세로 배치 컨테이너로 전환
  - `.cp-order-control`, `.cp-order-control__value` 추가

## 대기 중인 작업

Hephaestus가 `hook/`에서 배선해야 한다.

1. `hook/use-cp-main-display-process.tsx`
   - `moveItemOrder(overview, itemId, direction)` 구현 (`lib/cp-main-display.model.ts`에 배치 권장)
   - 같은 그룹(배너/주요 콘텐츠/공지) 내에서만 이동, 경계에서 no-op
   - `canMoveUp` / `canMoveDown` 파생값 노출
   - 순서 변경도 `isMainDisplayDirty` 판정에 포함되어 `canSave`가 켜지는지 확인
     (현재 `toMainDisplaySavePayload`가 `order`를 payload에 포함하는지 검증 필요)
2. `hook/use-cp-main-display-controller.tsx`
   - `process` 객체에 `canMoveUp`, `canMoveDown`, `onOrderChange` 전달
3. 배선 완료 후 `model/cp-main-display.types.ts`의 세 필드에서 `?`를 제거해 필수로 승격

## 결정 사항 및 제약 조건

- **세 계약을 optional(`?`)로 선언했다.** 필수로 두면 읽기 전용 경로인
  `hook/use-cp-main-display-controller.tsx`가 계약을 만족하지 못해 `tsc`가 깨진다.
  배선 완료 시 필수로 승격하는 것을 전제로 한 임시 조치이며, 타입에 주석으로 명시했다.
- 방식은 `↑ ↓` 버튼. 숫자 직접 입력·드래그 정렬은 범위 밖(사용자 승인 범위).
- 수치는 `shared/assets/css/_cp-admin.css` 토큰을 따랐다.
  버튼 `var(--cp-field-h)`(40px) 정사각, 컨트롤 간격 0.5rem.
  Figma의 절대좌표 수치는 사용하지 않았다.
- 정렬 대상 판별은 UI가 하지 않는다. UI는 선택 항목과 방향만 전달한다.

## 관련 경로

```
src/pages/cp-main-display/model/cp-main-display.types.ts   변경 (계약)
src/pages/cp-main-display/ui/cp-main-display-view.tsx      변경 (마크업)
src/pages/cp-main-display/ui/cp-main-display-view.css      변경 (스타일)
src/pages/cp-main-display/hook/**                          미변경 (읽기 전용 · 배선 대상)
src/pages/cp-main-display/lib/cp-main-display.model.ts     미변경 (재정렬 함수 배치 권장 위치)
```

## 명령어 및 결과

| 명령 | 결과 |
| --- | --- |
| `npx tsc --noEmit -p tsconfig.app.json` | 변경 범위 오류 **0건**. 전체 15건은 모두 기존 파일(`select-users`, `dialog.store`, `reason-prompt-host` 등) |
| `npx eslint src/pages/cp-main-display` | **0건** |
| `npx vite build` | **성공** (1.42s) |

## 작업 브랜치와 merge 방침

- 브랜치: `task/cp-main-display-order-control` (부모 `sy-main` @ `3f5b4d4b3199`)
- **merge 시점: 기능 배선까지 완료한 뒤 일괄 merge**로 확정했다.
  UI 계약만 먼저 `sy-main`에 올리지 않는다. 따라서 Hephaestus의 hook 배선도
  **이 브랜치 위에서** 수행한다.
- 현재 UI 변경은 commit 전 working tree 상태다.
- merge는 배선·검증 완료 후 별도 승인 절차를 거친다.

## 다음 조치

1. Hephaestus가 `task/cp-main-display-order-control` 브랜치로 전환한다.
2. 위 「대기 중인 작업」 3단계를 배선한다.
   - 3단계(타입에서 `?` 제거)까지 완료해야 계약이 최종 형태가 된다.
3. 배선 후 확인 항목
   - 순서 이동 버튼 활성/비활성 (그룹 경계에서 no-op)
   - 순서 변경이 `canSave`를 켜는지 (`isMainDisplayDirty`)
   - `toMainDisplaySavePayload`가 `order`를 payload에 포함하는지
   - `tsc` / `eslint` / `vite build` 재실행
4. 검증 통과 후 `sy-main` merge 승인을 요청한다.
