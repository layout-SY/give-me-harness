# Maintenance API·Controller 완료 상태

## 역할과 승인

- requested_roles / confirmed_roles: logic / logic(inject).
- completed_roles: logic API·controller 구현·포맷·테스트·lint·build 완료.
- next_role: 없음. API·controller 구현과 사용자 요청 커밋 완료.
- 사용자 계약: 기존 모듈 교체, Swagger 경로 통일, 조회 모든 필드 필수·null 금지, PATCH 성공 data는 null.
- 구현 승인: `작업 진행`. 필요한 자체 실패 패치·오래된 npm ci 기록 복구는 사용자 일반 채팅 승인 후 완료했다. 복구 상세 이력은 final-summary.md에 있다.
- controller 추가 승인: `그럼 일단 이 패턴대로 controller 구현해봐`. UI 화면 없이 타입·mapper·controller hook을 추가했다.

## 현재 및 다음 작업 위치

- 공간 이름: maintenance-shared.
- project/저장소/실행 디렉터리: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`.
- branch: `sy-main`, HEAD `b5c35a8` (`feat: maintenance API 및 controller 구현`).
- 현재 기본 checkout에서 그대로 이어간다. 기준 브랜치라 직접 부모 없음. 새 branch/worktree 생성 계획 없음.
- staged·unstaged: 없음. maintenance 소스·테스트 22개 파일은 모두 커밋되었다.
- untracked: 다른 작업의 `docs/admin-routes.md`만 남았다. 정확한 최신 상태는 시작 시 git status로 재확인한다.
- 다른 작업의 untracked `docs/admin-routes.md`는 수정하거나 포함하지 않고 보존했다.
- 자기 산출물: `.codex/logs/sessions/maintenance-api/`. 다른 세션 기록은 수정하지 않는다.

## 완료 내용과 검증

1. Swagger 7개 API와 DTO·parser, 조회 2개/변경 5개 훅을 `src/entities/maintenance/`에서 구현했다. 공개 import 경로는 `~/entities/maintenance`다.
2. 공통 ApiClient·인증·AbortSignal·오류 reporter를 재사용한다. 조회 필수/non-null 검증, PATCH null 성공 처리, 성공 후 maintenance 조회 취소·무효화가 포함된다.
3. `~/pages/maintenance`에서 목록·단건·변경 controller와 UI 타입을 제공한다. 통합 hook의 `list`로 조회 상태·데이터, `actions`로 제출 콜백·결과를 연결한다. 입력 보관은 소비 UI에서 수행하며 `onSaveConfigs`, `onSaveVersion`, `onSaveTime`, `onTurnOn`, `onTurnOff`로 넘긴다. 성공은 `isSuccess`로 판단한다. 연결 계약 상세는 final-summary.md에 있다.
4. 중앙 formatter로 최초 API 14개 및 추가 수정 12개 소스·테스트 포맷 완료.
5. `node --test tests/maintenance-controller.test.mjs tests/maintenance-contract.test.mjs tests/maintenance-query-mutation.test.mjs tests/logic-api-types.test.mjs`: 27개 통과. `npm run lint`, `npm run build`, `git diff --check` 모두 통과했다.

세부 구현·재사용 자산·검증 범위는 같은 세션 plan.md/final-summary.md에 있다. 사용자 승인 후 stage·commit은 보호 실행 작업 `d4f29d350430d1e373f0183a8edb068f`로 완료했다. merge·push와 실제 점검 변경 호출은 실행하지 않았다. 향후 이어갈 때 현재 diff를 먼저 재확인한다. 완료한 커밋 실행이나 기존 실패 기록용 복구 작업을 다시 실행하지 않는다.
