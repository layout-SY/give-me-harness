# 문의 관리 Logic 구현 계획

## 범위와 승인

- 사용자 요청: UI handoff를 읽고 필요한 Logic을 구현한 뒤 화면에 연결한다.
- 작업 공간: `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/inquiry-ui`, `feature/inquiry-ui`, 시작 HEAD `4b0b7db45aa9d15bf918a1a084370594e138a124`.
- 역할: Logic. `.claude/logs/sessions/inquiry-ui/handoff.md`의 controller 계약을 구현한다. UI view·page·라우트는 아직 없으며 UI 세션의 후속 작업이다.
- 확정 답변: 유형 관리 10개씩·필터 전체 페이지 조회, 검색 대상 미선택 시 TITLE, 유형 삭제는 서버 판단과 기존 오류 다이얼로그 사용.
- Git 변경은 미승인이다. 기존 UI handoff와 기본 checkout의 maintenance 작업을 보존한다.

## 구현 순서

1. 문의 entity에서 미사용 i18n 라벨을 제거하고 유형 코드 export를 추가한다. 기존 페이지 조회·공통 DTO·parser를 재사용해 필터의 전체 유형 조회를 지원한다.
2. `src/pages/inquiry/`에 목록·상세 타입, 설정, controller를 작성한다. 검색·페이지 전환·답변 등록/수정/삭제·완료·문의 삭제를 기존 Query mutation과 연결한다.
3. `src/pages/inquiry-type/`에 유형 관리 controller와 타입을 작성한다. 등록 코드 선택, 이름 수정, 서버 오류 표시와 페이지 갱신을 제공한다.
4. 기존 Node test·Vite SSR·MSW 방식으로 검색 계약, 전체 유형 조회, controller 상태와 변경 요청을 검증한다. 새 테스트 프레임워크는 도입하지 않는다.
5. 중앙 포맷 트리거 적용 후 관련 테스트, lint, build를 실행하고 UI 연결 방법을 자기 handoff에 기록한다. package.json에 test script가 없으므로 `node --test`를 사용한다.

## 재사용 근거

- `src/entities/inquiries/`: API·DTO·parser·Query key·조회 및 mutation hook·캐시 무효화.
- `src/shared/api/common/response.dto.ts`: 공통 페이지 응답 계약.
- `src/pages/item/hook/use-item-list-data.tsx`: 오류 알림·표·KPI 반환 방식.
- `src/pages/item-category/hook/use-item-category-controller.tsx`: 선택·편집 상태와 저장·삭제 패턴.
- `src/shared/ui/dialog/`: 기존 확인·오류 다이얼로그.
- `tests/events-controller.test.mjs`, `tests/news-list-controller.test.mjs`: controller 상태 검증 방식.

## 확인한 정책

task-role-routing, git-branch-strategy, coding-convention, type-definition, data-fetch-layer, documentation, implementation-quality, validation, reference-custom-hooks, recipe-data-fetch. 역할 라우팅에서 참조하는 workflows.md는 현재 bundle에 없어 읽지 못했으며 직접 제공된 역할·승인·handoff 계약을 따른다.
