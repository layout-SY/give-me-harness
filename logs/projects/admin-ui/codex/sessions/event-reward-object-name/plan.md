# 출석·룰렛 보상 이름 연결 계획

- 역할·책임: Codex Logic, owner. 사용자 지시로 핸드오프의 objectName 연결을 구현한다.
- 사용자 확인: 해당 워크트리 작업 지시 후 `진행`으로 구현 승인했다. 소스 7개 파일과 테스트 3개 파일에 변경을 적용했다.
- 작업 위치: `/private/tmp/asan-metaverse-admin-ui-event-api`, branch `feature/event-attendance-roulette-api`, HEAD `0bf712b3a35e64a81857e81a1ea06826134dc431`, 직접 부모 `sy-main`.
- 근거: `.claude/logs/sessions/event-attendance-roulette-ui/handoff.md`의 2026-09-21 후속 인계와 실제 DTO·parser·보상 편집 hook·UI props를 확인했다.
- 요청 명확성: clear. 서비스 계약의 미확정 항목은 없다. 구현·기록 복구·최종 포맷·검증 완료.

## 구현 범위

1. 기존 출석·룰렛 보상 응답 schema에 `objectName: z.string().nullable()`을 추가한다. 상세와 보상 조회는 기존 parser/schema를 함께 사용한다.
2. 기존 attendanceDrafts·rouletteDrafts와 보상 editor에 이름을 보존해 캘린더·일차 목록·보상 행·룰렛 조각으로 전달한다.
3. useEventItemSearch의 선택 callback에 기존 검색 결과 name을 전달한다. 직접 ID 편집은 이름을 null로 초기화한다. 추가 조회는 하지 않는다.
4. 요청 mapper는 기존 허용 필드만 전달해 objectName을 제외한다.
5. 기존 node:test·SSR controller 방식으로 이름 보존, nullable·필수 응답 계약, 검색 선택, 직접 입력 초기화, 요청 제외를 검증한다. 공통 포맷 후 관련 테스트·lint·build를 실행한다.

## 재사용과 변경 보존

- shared/api/common/response.dto.ts의 PageSummaryResponseDto/schema 및 기존 ApiClient/parser 경계를 재사용한다.
- 기존 useEventItemSearch/useEventRequest/useEventRewardCopy와 도메인 draft·payload mapper를 확장한다. UI props는 이미 준비되어 있다.
- 기존 미커밋 UI 변경, date-range-picker 변경, 룰렛 chance 합계 경고와 테스트를 보존한다. 겹치는 파일은 use-roulette-reward-editor.ts, roulette-rewards.ts, events-controller.test.mjs이며 해당 변경 위에 순차로 추가한다.
- 적용 스킬: task-role-routing, git-branch-strategy, coding-convention, type-definition, data-dto, implementation-quality, data-fetch-layer, custom-hooks, documentation.
- Git 변경은 요청받지 않았다. stage·commit·merge·push는 실행하지 않는다.

## 실행 상태

- 구현 승인 후 소스 7개 파일 적용·실제 Prettier 포맷 완료. 이후 회귀 테스트 3개 파일을 수정했다.
- 첫 테스트 패치는 같은 파일의 중복 Update 지시로 apply_patch 검증 단계에서 실패했다. 정상 패치로 고쳤으나 중앙 formatter에 실패 호출의 미확인 기록이 남았다.
- 관련 테스트 56개를 먼저 실행해 54개 통과, 신규 SSR 검색·가져오기 테스트 2개 실패를 확인했다. Vite의 시험용 요청 결과 plugin에 enforce pre를 지정해 두 테스트가 통과했다. 아직 최종 포맷 후 전체 관련 테스트·lint·build 검증은 남아 있다.
- 기존 UI 변경은 다른 작업자가 작업 중 commit `aae0ba7cb908ef5d08d50d00e9b4b4bf3b011b59`로 기록했다. 최신 diff에는 이 작업의 objectName 관련 소스·테스트 10개만 남아 있으며 UI와 chance 경고 구현은 보존되어 있다.
- 기록 복구 대상: `31f2d368d99db096c01877e11862aec67106f7ea02bcf9b5176f8dd17d1af08a` (실패한 apply_patch 호출). 원래 operation `6426f096aa5c4a9a97cf264aeed8577d`는 사용자가 승인했으나 Codex PreToolUse의 workdir 누락으로 위치 확인에서 차단됐다.
- 대체 operation `6f2f374d137244cda3425087c3083af8`: 같은 프로젝트 기본 checkout에서 동일 기록만 복구하도록 준비했다. 사용자가 위치 변경까지 승인했으나 선택형 질문 도구가 답변에 질문 인용문을 붙여 중앙 승인 검사에 등록되지 않았다. Git 내용·파일 변경은 없는 기록 복구다.
- 차단 원인 확인: 중앙 approval_policy.py의 update 경로는 `prompt.strip() == COMMAND_APPROVAL_PHRASE`인 전체 일치만 허용한다. 인용문이 포함된 답변은 문장에 `명령 실행 승인`이 있어도 등록되지 않는다. 동일 작업을 새로 준비하지 않고 인용문 없는 승인 메시지 반영 뒤 기존 operation을 실행한다.
- 사용자가 인용문 없는 `명령 실행 승인`을 전달한 뒤 operation `6f2f374d137244cda3425087c3083af8`을 한 번 실행해 stage done을 확인했다.
- 이벤트 워크트리에서 공통 포맷 apply·check, 관련 테스트 56개, lint, 타입 검사·build, git diff --check를 모두 통과했다. 연결 워크트리 포맷·검증은 리터럴 cd를 명령에 명시해 PreToolUse가 실제 위치를 인식하게 했다.
- 후속 사용자 요청: 커밋 후 merge. 명령 실행 승인 후 operation `92941f574e2e6b392142dcb8abff6404`로 10개 파일을 commit `60f1ef7`에 기록했다. 소스 워크트리는 clean.
- sy-main `ed9d65b`와의 병합 review `b93f4974622f46f2840edb3e3c69a6ff`에서 UI 파일 6개 텍스트 충돌을 확인했다. 현재 Logic 역할 범위 밖의 JSX·CSS 충돌 해결은 같은 작업 공간의 UI 세션에 인계한다. merge·push는 미실행이며 후속 경로와 계약은 handoff.md에 기록했다.
