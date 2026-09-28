# 출석·룰렛 objectName 커밋 후 UI 병합 충돌 인계

## 목표와 상태

사용자는 objectName 연결 완료 후 커밋과 merge를 요청했다. Logic 구현과 commit `60f1ef7`은 완료했다. 직접 부모 sy-main과의 병합 사전 검사에서 JSX·CSS 6개 파일의 텍스트 충돌을 확인했다. 실제 merge는 시작하지 않았으므로 MERGE_HEAD나 미해결 index는 없다.

- requested_roles: Logic(기존 구현), UI(병합 충돌 해결 제안)
- confirmed_roles: Logic (inject --role logic)
- completed_roles: Logic
- next_role: UI
- 이유: 이전 이름 표시와 새 보상 레이아웃의 JSX·CSS 충돌은 화면 표현 영역이다. 현재 역할을 임의로 확대하지 않았다. UI 역할은 새 --role ui 세션으로 시작한다.
- 사용자 승인: objectName 핸드오프 구현, 이벤트 워크트리 작업, 변경 10개 파일 stage·commit 명령 실행 승인. merge 의도는 명시됐지만 정확한 병합 명령 실행 승인은 아직 없다.

## 보내는 위치와 인계 대상 작업 공간

작업 공간 `event-api-shared`를 그대로 순차 사용한다. 별도 브랜치·워크트리를 생성할 필요는 없다.

| 항목 | 값 |
| --- | --- |
| project | `/Users/okand/SynologyDrive/asan-metaverse-admin-ui` |
| source branch | `feature/event-attendance-roulette-api` |
| source worktree·실행 디렉터리 | `/private/tmp/asan-metaverse-admin-ui-event-api` |
| source HEAD | `60f1ef781c1e5a32e3ce0bd33caff8e6211abd26` |
| 직접 부모·통합 대상 | `sy-main` (중앙 관계 graph 확인) |
| target HEAD | `ed9d65bd6c74eabf3f8e5070c203135d2067264e` |
| target worktree | `/Users/okand/SynologyDrive/asan-metaverse-admin-ui` |
| 확인 시점 | 2026-09-21, commit 완료 및 병합 review 직후 |
| staged·unstaged·untracked | source·target 모두 없음. 세션 산출물은 ignored |

현재 소스는 다음 두 commit을 보존한다.

- `aae0ba7`: 기존 UI 세션의 보상·설정 화면·DateRangePicker 표시 개선과 chance 합계 100 초과 경고.
- `60f1ef7`: 응답 objectName, draft·editor·검색 선택 연결, 테스트 10개 파일 변경.

## UI 역할의 상세 작업

시작 시 source·target의 최신 HEAD와 dirty 상태를 다시 확인한다. 중앙 git-branch-strategy의 부모 동기화·완료 절차와 새 세션의 승인 계약에 따라 통합한다. 이 문서는 병합 명령의 승인 자체를 대신하지 않는다.

확인된 충돌 경로:

1. `src/pages/event-attendance/ui/attendance-reward-rows.tsx`
2. `src/pages/event-attendance/ui/event-attendance.css`
3. `src/pages/event-roulette/ui/roulette-reward-editor.tsx`
4. `src/pages/event-roulette/ui/event-roulette.css`
5. `src/widgets/event-admin/ui/event-admin.css`
6. `src/widgets/event-admin/ui/object-id-field.tsx`

`sy-main`의 ed9d65b는 이전 `itemName` 선택 props와 아이템 검색 결과 Table 전환을 포함한다. source의 aae0ba7은 최신 `objectName` props와 보상 행 레이아웃, 이름 확인 중 표시, 캘린더 칩·룰렛 휠 개선을 포함한다. 두 변경의 의도를 보존하며 충돌을 해결한다. 자동 병합되는 두 보상 model 타입도 `itemName`과 `objectName`이 함께 남을 수 있으므로 실제 UI 호출부·controller 계약과 함께 확인한다.

보존할 확정 계약:

- `AttendanceRewardRow.objectName`, `RouletteRewardRow.objectName`, 칩·휠의 `objectNameLabel`은 Logic controller가 채운다.
- 이름은 응답 전용 필수 nullable 필드다. 요청 DTO에는 넣지 않는다.
- 검색 선택은 기존 결과 name을 사용한다. 직접 ID 편집 때는 이름 null, 추가 조회 없음, 기존 UI의 이름 확인 중 표시를 유지한다.
- 보상 가져오기는 이름을 함께 가져오며 저장 전까지 초안이다.
- chance 합계 100 초과는 경고만 하고 저장을 막지 않는다.
- sy-main의 기존 아이템 검색 Table·아이템 표시 공용화와 /login 경로 변경을 보존한다.

재사용 자산: 기존 ObjectIdField, ItemSearchPopup, shared Table, attendance/roulette editor props, shared DateRangePicker. 새 화면 설계나 API 계약을 추가할 작업은 아니다. 역할 전환 후에도 기존 코드·검증 결과와 최신 UI 핸드오프를 기준으로 통합하며, 추가 기획 선택이 필요하면 질문한다.

## 병합 검토와 협업

- 검토 ID: `b93f4974622f46f2840edb3e3c69a6ff`
- evidence_digest: `e76d7a3719ce68a34c95f05201928761f12f93f55610f2f42fda035b5935333b`
- 검토 결과: ff-only 불가, 텍스트 충돌 있음. semantic review 완료·병합 승인을 아직 제출하지 않았다.
- source의 미처리 자식은 graph에서 확인되지 않았다.
- 형제 `feature/auth-guard-menu-api`는 당시 sy-main과 같은 ed9d65b, 워크트리 clean이었다. 작업이 진행될 수 있으므로 완료 검토 때 재확인한다.
- 형제 `feature/item-ui`는 7bcc83e, clean이며 이미 sy-main 통합 이력이 있다. 이전 `feature/event-item-ui`는 ed9d65b로 통합된 변경이 이번 UI 충돌과 직접 관련된다.
- 종료/삭제된 뉴스·가상오피스 등 형제 이력도 중앙 review에 수집됐다. 이번 인계에서 전체 형제 의미 검토를 완료했다고 주장하지 않는다.
- branch/worktree 정리·원격 push는 요청받거나 승인받지 않았다.

## 검증과 다음 인계

60f1ef7의 내용은 commit 직전 실제 Prettier·관련 테스트 56개·npm run lint·npm run build·git diff --check 통과했다. merge된 결과의 검증은 아직 수행하지 않았다.

관련 테스트 명령:

`node --test --test-reporter=dot tests/events-contract.test.mjs tests/events-controller.test.mjs tests/events-query-mutation.test.mjs tests/common-response-contract.test.mjs tests/logic-api-contract.test.mjs tests/logic-api-types.test.mjs`

UI 충돌 해결 후 포맷 → 위 테스트·아이템 Table 관련 tests/item-form.test.mjs·lint·build → 최종 source commit → 새 완료 review → source에서 직접 부모 sy-main으로 병합 승인·사후 검증 순서로 진행한다. 실제 Git 명령·순서는 최신 상태와 사용자 승인으로 확정한다.

## 실행 환경 참고

현재 Codex hook은 exec_command.workdir를 PreToolUse에서 누락하는 사례가 있었다. 보호 Git 실행기는 기본 checkout에서 준비·실행하고 Git 대상은 리터럴 `git -C /private/tmp/asan-metaverse-admin-ui-event-api ...`로 지정했다. 포맷·검증은 리터럴 `cd /private/tmp/asan-metaverse-admin-ui-event-api && ...`로 실제 위치를 명시했다.

명령 승인은 `명령 실행 승인`만 있는 사용자 메시지로 받는다. 선택형 질문 도구의 인용문이 붙으면 중앙 전체 일치 검사에서 등록되지 않았다. 실패 패치의 미확인 기록은 승인된 operation 6f2f374d137244cda3425087c3083af8로 해소했으며 포맷 check까지 통과했다.

필수 정책: task-role-routing(ui), git-branch-strategy, coding-convention, implementation-quality, documentation. 다른 세션·host 로그는 읽기 전용이다.
