# 튜토리얼 관리 UI 구현 결과

튜토리얼 목록·등록·수정·삭제 화면을 Logic controller에 연결하고 `ImageManager`를 확장했다. 포맷·테스트·lint·build가 통과했다. Git 작업은 하지 않았다.

- **작업 위치**: `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/tutorial`, `feature/tutorial`, HEAD `987616b`(직접 부모 `sy-main`)
- **계약**: Logic 선행(`controller <- UI`). 불일치는 없었다. 계약 문서는 `.codex/logs/sessions/tutorial-api-controller/unknown/controller-contract.md`.

## 변경 파일

| 구분 | 경로 | 내용 |
| --- | --- | --- |
| 신규 | `src/pages/tutorial/ui/tutorial-list-{page,view}.tsx` | 목록. 등록 버튼, 전체 개수, 표(ID·제목·페이지 수·등록일·수정일), 행 클릭 시 상세, 실패 시 다시 조회 |
| 신규 | `src/pages/tutorial/ui/tutorial-editor-{page,view}.tsx`, `tutorial.css` | 등록·수정. 제목, 이미지 페이지, 삭제 확인, 404·로드 실패, 미리보기 모달, 성공 시 목록 이동과 완료 알림 |
| 신규 | `src/pages/tutorial/{lib/tutorial-display.ts,model/tutorial.columns.ts}` | 목록 경로 상수, 날짜 표시, 표 컬럼 |
| 수정 | `src/pages/tutorial/index.ts` | 페이지 export 추가. Logic export는 그대로 |
| 신규 | `src/features/image-manager/lib/image-slots.ts`, `ui/components/ImageSlotEmpty.tsx` | 슬롯 추가·삭제·교체·이동 순수 함수, 빈 자리 슬롯 |
| 수정 | `src/features/image-manager/ui/{ImageManager.tsx,ImageManager.css,types.ts,hooks/useImageSlots.tsx}` | 선택형 `reorderable`, `allowEmptySlots`(판별 유니온), `onPreview(url, index)` 추가. 기본 모드의 렌더·업로드는 그대로 |
| 수정 | `src/app/router/routes.tsx` | `/manage/operations/tutorials`, `/new`, `/:tutorialId` 등록(`new` 우선) |
| 수정 | `src/widgets/side-navigation/{model/_navigation2.ts,lib/build-navigation-items.ts}` | 운영 관리 > 튜토리얼 메뉴 추가, 셸 노출 경로 추가 |
| 수정 | `docs/admin-routes.md` | 튜토리얼 경로와 메뉴 설명 추가 |
| 신규 | `tests/image-manager-slots.test.mjs` | 슬롯 조작 4건 |

## 검증

- `formatting.py apply`: 18개 파일 포맷 완료.
- `node --test tests/image-manager-slots.test.mjs tests/tutorial-contract.test.mjs tests/tutorial-controller.test.mjs`: 23/23 통과.
- `npm run lint`: 오류 없음.
- `npm run build`: 타입 검사와 빌드 성공. 기존 경고 2건(vite-tsconfig-paths 안내, 500 kB 청크)이 있다. 아이템 폼의 `ImageManager` 호출은 타입 변경 없이 통과했다.
- 수행하지 않음
  - 브라우저 실행·시각 QA, 실제 서버 호출
  - Watcher 독립 판정
  - React 컴포넌트 DOM 테스트(저장소에 DOM 테스트 도구가 없다)

## 알려진 제한과 후속

- **업로드 흐름**: 업로드는 `ImageManager`의 `uploadApi` 경로를 쓴다. 이미지는 선택 즉시 서버에 업로드되므로, 저장하지 않고 떠나면 스토리지에 파일이 남는다(서버 동작).
- **제목 공백**: 제목 앞뒤 공백은 그대로 저장된다(Logic 동작). 필요하면 Logic에서 보완한다.
- **HeroUI 사용 스킬**: 세션 초안만 있다(`unknown/ui-library-skills/heroui-react/SKILL.md`). 중앙 `policy/common/skills/reference/libraries/heroui-react/SKILL.md` 등록은 중앙 저장소 작업으로 인계한다.
- **기본 checkout 사본**: `sy-main`에 Logic 구버전 사본 18개가 untracked로 남아 있다. Logic 세션의 정리 대상이며 이번 작업에서는 손대지 않았다.
- **Git**: 2026-10-02에 사용자 승인을 받아 `feature/tutorial`에 `2967764`로 커밋했다(19개 파일). push와 `sy-main` 병합은 하지 않았다.
- **기획서 대조 후속**: Logic 보완 사항과 UI 2차 작업은 [handoff.md](handoff.md)에 있다.
