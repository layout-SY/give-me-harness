# 구현 로그

## 승인된 범위

- `src/pages/cp-main-display/model`
- `src/pages/cp-main-display/ui`
- `src/pages/cp-main-display/hook`
- `src/pages/cp-main-display/lib`
- `src/mocks/cp-main-display.handlers.ts`
- `tests/cp-main-display-order-control.test.mjs`
- `.codex/logs/sessions/2026-08-29-cp-main-display-order-wiring`

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `src/pages/cp-main-display/lib/cp-main-display.model.ts` | 순서 이동, 이동 가능 여부, `order` 기반 dirty 비교 추가 | 경계 이동을 차단하고 변경 상태를 계산함 |
| `src/pages/cp-main-display/model/cp-main-display.types.ts` | 이동 방향과 process/view 계약 확장 | hook과 UI 간 타입 계약을 명시함 |
| `src/pages/cp-main-display/hook/use-cp-main-display-process.tsx` | draft 재정렬, 이동 가능 상태, 저장 후 동기화 연결 | 이동 후 저장 가능, 저장 후 dirty 해제 |
| `src/pages/cp-main-display/hook/use-cp-main-display-controller.tsx` | process의 이동 계약을 view에 전달 | 화면 이벤트가 상태 변경에 연결됨 |
| `src/pages/cp-main-display/ui/cp-main-display-view.tsx` | 위·아래 이동 버튼과 disabled 상태 추가 | 사용자가 경계 조건을 확인하며 순서를 변경 가능 |
| `src/pages/cp-main-display/ui/cp-main-display-view.css` | 순서 제어와 disabled 스타일 추가 | 기존 화면 구조에 맞는 제어 표시 |
| `src/mocks/cp-main-display.handlers.ts` | 저장 payload 순열·중복 검증과 `order` 정렬 응답 | 잘못된 저장을 거부하고 저장 결과를 재현함 |
| `tests/cp-main-display-order-control.test.mjs` | 이동·경계·dirty·round-trip·중복 order 회귀 테스트 | 핵심 상태 경계를 자동 검증함 |

## 결정 사항

- 순서 이동은 동일 섹션의 인접 항목 교환으로 한정했다.
- 이동 결과의 `order`는 배열 위치에 맞춰 연속 값으로 재부여한다.
- 저장 성공 후 서버 응답을 draft와 기준 상태에 함께 반영해 저장 버튼을 다시 비활성화한다.
- MSW handler는 ID와 제목 집합뿐 아니라 순서 집합과 중복도 검증한다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `node --test tests/*.test.mjs` | 20/20 통과 |
| `npm run build` | 통과 |
| 변경 파일 대상 `npx eslint ...` | 오류·warning 없이 통과 |
| `GIT_MASTER=1 git diff --check` | 통과 |
| 브라우저 `http://127.0.0.1:13001/cp/main-display` | 이동, 저장 HTTP 200, 응답 order 반영, 저장 후 disabled, console error 0건 확인 |

## Watcher 인계

- 검토 대상은 위 승인 범위의 코드·테스트 변경이다.
- Watcher는 blocking/high/medium/low 발견 없이 PASS로 판정했다.
- 비차단 관찰은 신규 테스트 파일을 최종 commit에 반드시 포함하라는 내용이다.
