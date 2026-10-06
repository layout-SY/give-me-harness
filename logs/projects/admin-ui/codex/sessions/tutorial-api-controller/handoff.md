# 튜토리얼 편집 controller 보완 → UI 2차 인계

제목·페이지 규칙 보완과 자동 검증을 완료하고 변경 3개 파일을 `811c8bb`로 커밋했다. 작업 트리는 clean이며 UI 1차 커밋은 그대로 보존했다.

## 역할과 작업 공간

- requested_roles / confirmed_roles: logic
- completed_roles: logic 구현·자동 검증
- next_role: ui
- 근거: 사용자가 tutorial의 Claude UI handoff를 읽고 추가 작업을 진행하라고 요청했다. 미정 항목은 코드 포인트 계산, 20개 이하로 줄여야 저장하는 방식으로 답변받았고 계획에 `진행` 승인을 받았다.
- 현재 및 다음 작업 위치: admin-ui, `feature/tutorial`, `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/tutorial`. 명령 실행 위치도 동일하다.
- HEAD: `811c8bbc4570572e4167c4aeef5e62ea2ac8e6a6` (Logic 보완), 직접 부모 `sy-main`, 분기 기준 `987616b724273b63b1d8c7037679402ad26f7c87`. 기존 Logic 커밋은 `6b96d7b`, UI 1차는 `2967764`다.
- 공유 이유: controller 규칙을 UI가 순차로 연결한다. 다음 작업자도 같은 branch/worktree에서 최신 diff를 확인한 뒤 진행하며 동시 편집하지 않는다.
- 산출물 정본: `.codex/logs/sessions/tutorial-api-controller/`. Claude handoff `.claude/logs/sessions/튜토리얼-관리-UI/handoff.md`는 읽기 전용으로 참조했다.

## 실제 변경과 검증

- 수정 1: `src/pages/tutorial/hook/use-tutorial-editor-controller.ts` — 제목 코드 포인트 30자, 등록 기본 빈 칸 3개, 페이지 추가 조건과 최대 20개, 초과 데이터 저장 차단·단계적 감소.
- 수정 2: `src/pages/tutorial/model/tutorial-controller.types.ts` — `titleLength`, `titleMaxLength:30`, `maxImages:20`, `canAddImage`, `imagesError` 공개.
- 수정 3: `tests/tutorial-controller.test.mjs` — 등록 기본값의 의도적 계약 변경 반영 및 6개 경계 테스트 추가.
- 기존 UI·ImageManager·라우트·API DTO·의존성은 변경하지 않았다. 재사용은 기존 controller·actions·Query·SSR/MSW 테스트에 한정한다.
- 공식 `formatting.py apply`: 위 3개 파일 Prettier 성공.
- `node --test tests/tutorial-contract.test.mjs tests/tutorial-controller.test.mjs tests/image-manager-slots.test.mjs`: 29/29 통과(튜토리얼 25 + 이미지 슬롯 4).
- `npm run lint`, `npm run build`, `git diff --check`: 모두 exit 0.
- 빌드 경고: vite-tsconfig-paths 대체 안내, 500 kB 초과 청크. SSR 검증은 DOM mount/unmount를 실행하지 않는다. 실제 서버 변경·시각 QA·독립 Watcher 판정은 수행하지 않았다.

## UI가 사용할 확정 계약

- 연결 방향: 보완된 controller를 기준으로 UI 2차가 맞춘다(`controller <- UI`). 자세한 계약은 [controller-contract.md](unknown/controller-contract.md).
- 제목 카운터는 `fields.titleLength / fields.titleMaxLength`를 사용한다. JS string.length나 HTML maxLength=30은 이모지 계산이 다르므로 검증 기준으로 사용하지 않는다. 입력은 자르지 않고 31자부터 오류·저장 불가 상태를 제공한다.
- 등록 초기 images는 null 3개, 수정은 서버 배열 그대로다. 빈 칸도 저장하고 페이지 수에 포함한다. 이미지 0개도 유효한 제목이면 저장 가능하다.
- 페이지 추가 버튼은 `fields.canAddImage`로 비활성화하고 `fields.onAddEmpty`를 호출한다. 상한 표시는 `fields.maxImages`를 사용한다. 빈 칸이 남아 있으면 추가할 수 없다.
- `onImagesChange`는 20개 초과 입력과 빈 칸이 있는 상태의 개수 증가를 거부한다. 서버 초과 데이터의 단계적 개수 감소는 예외로 허용한다. `onRemoveImage`도 기존대로 한 칸씩 삭제한다.
- 기존 20개 초과 데이터를 자동 삭제·잘라내지 않는다. `fields.imagesError` 및 `save.errorMessage`를 표시하며 20개 이하로 줄이기 전에는 저장하지 않는다.
- 기존 칸 교체는 `uploadApi(FormData)`로 업로드한 URL을 해당 위치에 넣고 `onImagesChange`에 전달한다. 20개인 상태에서도 기존 칸 교체는 가능하다. 기존 초과 상태의 전체 배열 교체는 거부되므로 먼저 페이지 수를 줄인다.
- 직접 끝에 이미지를 추가하는 `onAddImage(File)`도 빈 칸·최대 개수 제한을 업로드 전에 확인한다. `uploadApi` 자체에는 이 제한을 넣지 않아 기존 칸 채우기·교체를 유지한다.
- 삭제 확인·재정렬·미리보기 및 API payload 매핑은 기존 계약을 유지한다. 이미지 단위 삭제 확인·세로 목록·드래그·카운터는 UI 단계에서 구현한다.

## 다음 순서와 완료 기준

1. 같은 worktree에서 커밋 `811c8bb`와 기존 UI를 확인하고 후속 UI 작업을 시작한다. 새로운 Git 변경은 정확한 대상·명령으로 사용자 승인을 받는다.
2. UI 2차에서는 기존 ImageManager 및 tutorial-editor-view에 공개 계약을 연결한다. 현재 1차 화면은 maxImages=Infinity를 쓰고 카운터·추가 버튼 제어가 없으므로 이를 새 계약에 맞춘다.
3. UI handoff의 세로 목록·번호·썸네일·수정·삭제 확인·드래그 요구를 처리한다. @dnd-kit 도입과 자산 선정은 UI 스킬 및 별도 승인 절차를 따른다.
4. UI 연결 후 관련 동작 테스트, 포맷·lint·build를 완료한다. 브라우저 캡처·시각 QA는 사용자 요청이 있을 때 수행한다. sy-main 병합은 별도 승인이다.

## Git 및 보존 상태

- 이번 작업의 source/test 3개는 사용자 승인 후 `811c8bb` (`feat(tutorial): 제목 길이 및 페이지 편집 규칙 적용`)로 커밋했다. 보호 작업 `26b0b445ff7bdb80c49f0e2b9a9a7ffd` done 및 staged·unstaged·untracked 변경 없음 확인. push·merge는 수행하지 않았다.
- UI 1차 `2967764`와 Logic `6b96d7b`를 보존했다. 다른 세션의 문서는 수정하지 않았다.
- primary의 이전 튜토리얼 사본 18개는 앞선 사용자 승인으로 제거 완료했다. 이번 작업은 tutorial worktree에서만 수행했다.
- 필요한 스킬: task-role-routing, git-branch-strategy, UI 역할의 ui-library·외부 라이브러리 스킬, api-authoring/ui-controller, documentation.
