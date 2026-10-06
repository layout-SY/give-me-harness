# 문의 controller 구현 재개

- 역할·책임: Logic contributor. 사용자 요청으로 기존 계획의 구현을 승인받았다. UI가 제공한 계약에 controller를 맞춘다(`controller -> UI`).
- 실제 작업 위치: `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/inquiry-ui`, `feature/inquiry-ui`, HEAD `4b0b7db45aa9d15bf918a1a084370594e138a124`. writable root에 이 경로가 포함된다. 직접 부모는 기존 인계의 생성 기록상 `sy-main`이다.
- 보존: 인계된 entity 5개·테스트 1개 변경, 다른 세션 산출물. 이번 요청에 commit·merge 승인은 없다.
- 확정 요구: 두 목록 size 10, 유형 필터는 size 10으로 모든 페이지 조회, 빈 검색어는 by·keyword 생략, 검색 대상 미선택은 TITLE, sort 생략, 답변 등록 후 추가 PATCH 없음, 완료만 COMPLETED, 유형 수정은 name만, 삭제 허용은 서버 판단.
- 재사용 확인: `src/entities/inquiries/`의 DTO/parser·query/mutation과 캐시 무효화, `src/shared/api/common/response.dto.ts`, `src/shared/ui/dialog/`, `src/app/providers/query-client.ts`의 전역 오류 처리. 기존 item·item-category controller와 cp-news·events SSR 테스트를 확인했다. 전역에서 표시하는 서버 오류는 controller에서 중복 알리지 않는다.
- 적용 스킬: task-role-routing, git-branch-strategy, coding-convention, type-definition, data-fetch-layer, validation, documentation, implementation-quality, reference-custom-hooks, recipe-data-fetch 및 ui-controller 계약.

## 작업 순서

1. 같은 worktree에서 기존 entity 변경의 테스트를 실행한다. 기존 51개 테스트 통과(2026-09-28), 포맷 트리거 정상 실행(신규 기록 대상 없음).
2. `src/pages/inquiry/`와 `src/pages/inquiry-type/`에 공개 타입·config·controller 3종을 작성한다. 기존 승인 범위의 hook 내부에 초안·선택·동기 중복 요청 방지를 둔다.
3. 기존 Node test + Vite SSR + MSW 방식으로 요청 매핑, 상태 전이, 오류·빈 결과·잘못된 ID·중복 실행을 확인한다. 프레임워크를 추가하지 않는다.
4. 중앙 포맷 트리거, 문의 관련 테스트, lint, build를 실제 workdir에서 실행한다.
5. 자기 세션 handoff에 실제 변경, 검증과 UI page/view·라우터·메뉴의 후속 연결 계약을 남긴다.

## 완료 결과

- 기존 변경 6개의 기능을 보존하고 controller 3종·공개 타입 3종·config 2개 및 controller 테스트를 추가했다.
- 이전 세션 쓰기 예약은 사용자 `명령 실행 승인` 후 공식 복구 작업 `f6c0769e37ed4cb2a3a672402470edf5`를 1회 실행하여 해소했다(stage `done`). 소스·Git 이력 변경은 없었다.
- 신규 controller 테스트에서 확인 중 ID 전환 시 비활성 상태가 남는 문제를 재현한 뒤 수정했다. 해당 테스트의 수정 전 FAIL·수정 후 PASS를 확인했다.
- 기존 변경을 포함한 작업 대상 15개 코드·테스트 파일에 중앙 Prettier 포맷을 적용했다. 문의 관련 테스트 71개, `npm run lint`, `npm run build`, `git diff --check` 통과.
- UI 연결은 다음 ui 세션의 작업이다. 실행 위치·공개 계약·검증 범위·미완료 UI 작업은 [handoff.md](handoff.md)에 정리했다.
- commit·merge는 수행하지 않았다. 현재 변경은 `feature/inquiry-ui`의 미커밋 상태다.
