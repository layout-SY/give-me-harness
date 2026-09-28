# 출석·룰렛 이벤트 연결 결과

## 완료 범위

2026-09-18, UI commit `dad057f` 위에서 출석·룰렛 목록·등록·상세·설정·보상 화면의 Logic 연결을 완료했다. 사용자가 승인한 UI 핸드오프와 추가 답변을 적용했으며, 아이템 이름 검색은 5건으로 제한했다.

같은 날 후속 요청으로 sortOrder가 날짜·DAILY/ACC별 재시작 없이 전체 배열의 index+1을 보내는 것을 확인했다. 등록·수정이 같은 매핑을 사용하며 구현은 유지했다. 출석·룰렛의 화면 isActive는 false가 기본값이며 응답 null도 false로 처리한다. 토글 숨김·null 활성 저장 차단을 제거하고, 다른 필드 수정 없이도 기본값 false를 저장할 수 있도록 했다. 목록·상세 요약도 동일하게 표시한다. 원본 API 응답의 nullable 계약은 유지한다.

## 동작과 주요 변경

- 출석 보상 DAILY/ACC, config IMAGE/TEXT를 DTO 요청·응답 검증에 반영했다. configKey/configValue의 자유 문자열 계약과 응답 nullable은 유지했다.
- 상세 items와 별도 보상 조회는 같은 schema/DTO이며, 보상 저장 성공 후 두 캐시를 갱신한다.
- 기존 View·props에 controller를 연결하고 /events 라우트의 목록·등록·상세 페이지를 추가했다. 상세 탭은 detail query 하나를 사용한다.
- 목록 page는 URL에 유지하고 size는 20이다. 아이템 검색은 이름 keyword, page 1, size 5이며 최대 5건만 표시한다.
- KST 날짜 표시·기간 전송, 900/901+YYYYMM ID와 코드 자동 입력, 사용자 수정 필드 보호를 구현했다.
- 보상 가져오기·추가/삭제/순서·필수값 검증을 구현했다. 기간 초과 DAILY는 경고만 하고 저장을 허용한다.
- 출석 일차 목록은 보상이 있는 날과 기간 밖 보상 일차를 표시한다. 빈 일차에는 달력에서 보상을 추가한다.
- 룰렛 chance는 그대로 전송하고 사장 필드 objectImageUrl은 원본 또는 빈 문자열을 보존한다.
- 이미지 업로드 후 서버 저장값 기준 configs 전체 PATCH를 수행한다. null URL·실패·취소는 PATCH를 막는다. 텍스트 초안은 이미지 저장과 재조회 후에도 유지한다.
- 미저장 탭의 초안은 재조회로 덮어쓰지 않으며 저장 성공 탭만 초기화한다.
- 입력 가능한 null은 빈 입력, 보완할 수 없는 null 필드는 탭별 저장 차단 사유로 표시한다. 후속 요청에 따라 isActive는 예외로 false를 기본값으로 사용한다.
- 임의 configKey의 객체 기본 속성 이름 충돌과 날짜에 배치할 수 없는 DAILY day를 회귀 테스트로 보완했다.
- 중복 저장과 화면 종료 후 늦은 결과를 차단한다. 이미지 미리보기는 기존 ImageModal·pubsub을 재사용했다.

## 변경 위치

- API 계약: src/entities/event/api의 공통·출석·룰렛 DTO.
- 공통 Logic: src/widgets/event-admin/lib 및 hook.
- 이벤트별 Logic·페이지: src/pages/event-attendance, src/pages/event-roulette.
- 라우트: src/app/router/routes.tsx, event-admin-shell.tsx.
- 날짜 재사용: shared/lib/utils/date.util.ts에 선택적 timeZone 인자.
- 테스트: events-controller.test.mjs 신규, events-contract/events-query-mutation의 확정 타입 계약 갱신.

## 검증

후속 isActive 수정 검증: 중앙 포맷 성공, 아래 관련 6개 테스트 파일 51 pass / 0 fail / 0 skipped, npm run lint·npm run build·git diff --check 통과. 전체 39개 테스트 파일 결과는 직전 Logic 연결 커밋의 검증이며 이번 소규모 수정에서는 관련 범위를 재검증했다.

직전 Logic 연결 커밋 검증:

| 작업 | 최종 결과 |
| --- | --- |
| 중앙 formatting.py apply | 수정한 소스·테스트 포맷 성공 |
| node --test, tests의 39개 파일을 명시 | 271 pass / 0 fail / 0 skipped, 약 17.2초 |
| npm run lint | 통과 |
| npm run build | 타입 검사·Vite build 통과 |
| git diff --check | 통과 |

기존 vite-tsconfig-paths 안내와 500kB 초과 번들 경고가 남아 있다. 실서버·실제 브라우저 기능/시각 검증은 수행하지 않았다. 테스트는 기존 node:test, Vite SSR, Axios/MSW, QueryClient를 사용했고 새 프레임워크를 추가하지 않았다.

관련 범위 재검증:
```sh
node --test tests/events-controller.test.mjs tests/events-contract.test.mjs tests/events-query-mutation.test.mjs tests/logic-api-contract.test.mjs tests/logic-api-types.test.mjs tests/common-response-contract.test.mjs
npm run lint
npm run build
```

전체 검증은 rg --files tests에서 확인한 39개 .test.mjs 파일 경로를 node --test에 나열하여 실행했다. shell wildcard는 사용하지 않았다.

## 승인·현재 Git 상태

- host·role: Codex·Logic. 작업 산출물 책임: owner.
- 사용자: UI commit 후 작업 진행 지시, 공통 처리 제안 승인, 검색 결과 5개로 확정.
- worktree: /private/tmp/asan-metaverse-admin-ui-event-api
- branch: feature/event-attendance-roulette-api, 직접 부모 sy-main.
- HEAD: 1b8e7336b382def67d97edf74b5a25192732fea0.
- 이전 완료: API b418379, UI dad057f.
- 사용자 승인 후 `feat(events): 출석·룰렛 관리 화면에 API 연결` 커밋 완료. 39개 파일, 1836줄 추가·9줄 삭제. 커밋 후 staged·unstaged·untracked 없음.
- 보호 실행 작업: 60f18b6a1cb1d92aa1e09621266adf55. merge·push·branch 변경은 수행하지 않았다. 기존 UI 변경 및 다른 세션 산출물은 보존했다.
- 현재는 후속 isActive 수정 5개 파일이 unstaged다. staged·untracked 없음. 대상은 widgets/event-admin의 lib/event-form.ts, hook/use-event-basic-fields.ts, hook/use-event-info.ts, hook/use-event-list-controller.ts와 tests/events-controller.test.mjs다. 후속 수정의 commit·merge·push는 요청받거나 실행하지 않았다.
- 자기 plan/handoff/final-summary는 .codex/logs/sessions/event-attendance-roulette-api 아래이며 ignored다.

## 인계

handoff.md를 현재 화면 사용·API 계약·소스 구조·예외 처리·검증 결과로 갱신했다. 최초 API 작업 당시 UI 미구현·type string·ID 자동 생성 제외 기록은 이번 후속 연결에서 갱신됐다. 구현 미완료 항목과 차단 요인은 없으며, 실서버 기능 확인과 Git 통합은 이후 요청 범위다.
