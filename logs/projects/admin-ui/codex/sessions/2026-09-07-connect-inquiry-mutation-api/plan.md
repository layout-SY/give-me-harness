# 계획

## 목표

문의 삭제·상태 변경·답변 등록·수정·삭제를 제공된 실제 백엔드 계약으로 구현하고 UI 담당자가 연결할 수 있는 hook과 handoff를 제공한다. 답변이 없는 상세 응답의 `answerContent`는 사용자가 확인한 `null`이다.

## 작업 유형

기능 구현 및 기존 답변 API 이전.

## 범위

- `src/entities/inquiries`: DTO, parser, 전송 API, 상태 어휘, mutation hook 및 공개 계약.
- `src/shared/api/api-client.ts`: 기존 전송 계약과 같은 PUT 지원.
- `src/mocks/inquiries.handlers.ts`, `src/mocks/handlers.ts`: 실제 요청 계약과 상태 변화의 mock 구현 및 등록.
- `tests/inquiries-contract.test.mjs`, `tests/inquiries-msw.test.mjs`, `tests/inquiries-mutation.test.mjs`: 요청·응답·재조회·캐시 경계 검증.
- 현재 세션 문서 8종과 UI용 `handoff.md`.

## 제외 사항

화면 JSX/CSS 변경, 실제 서버 데이터 변경, 패키지 추가 및 승인 전 병합은 수행하지 않는다.

## 제약 조건

변경 응답은 `{ code, message, data: string }` 계약을 공용 ApiResult로 처리한다. 답변 요청은 JSON `{ content }`이며 기존 파일·이메일·message 필드를 보내지 않는다. 상태는 기존 조회 계약의 `OPEN`, `IN_PROGRESS`, `COMPLETED`를 재사용한다. 답변 변경에 따른 자동 문의 상태 전이는 제공되지 않았으므로 만들지 않는다.

## 스킬 및 역할

- 확인된 역할: inject `logic`, Git 통합 담당자: `codex`, 산출물 책임: `owner`.
- UI 연결은 다음 `ui` 역할에 인계한다. 성공적으로 조회한 `answerContent === null`에 기존 `NoResults`를 표시한다.
- 적용 스킬: task-role-routing, git-branch-strategy, coding-convention, implementation-quality, type-definition, data-fetch-layer, validation, abstraction-strategy, documentation, api-authoring, data-dto, custom-hooks.

## 작업 순서

1. 문의 DTO와 공용 API에서 nullable 답변·JSON mutation·PUT 계약을 구현하여 전송 경계를 맞춘다.
2. 문의 전용 mutation hook에서 성공 이후 목록·해당 상세 캐시를 갱신하여 UI가 오래된 데이터를 표시하지 않게 한다.
3. 문의 MSW와 기존 테스트에서 mutation 후 조회와 실패 경계를 검증한다.
4. 타입·lint·테스트 결과를 검토하고 UI 담당자에게 NoResults 조건과 호출·오류·완료 처리 계약을 인계한다.

## 검증

`node --test tests/*.test.mjs`, `npm run lint`, `npm run build`, 변경 범위의 diff 확인. 실제 백엔드 호출과 시각 QA는 범위 밖이다.

## 위험 요소 및 결정 사항

전송 함수만 추가하는 안은 UI별 캐시 처리 중복이 생긴다. 도메인 mutation hook까지 제공하는 안을 선택한다. 공용 CRUD 추상화는 도입하지 않는다. 성공 응답이 상세 객체가 아니므로 응답 문자열로 상세 캐시를 덮어쓰지 않고 재조회한다. 문의 삭제 후 해당 상세 조회는 취소·제거하며 UI가 목록 이동 또는 상세 닫기를 담당한다.

## 승인

- 사용자: 제공한 5개 API로 수정·신규 구현 및 UI handoff 작성 요청, `answerContent: null` 및 NoResults 표시 확인, 계약 제시 뒤 `작업 진행` 승인.
- 브랜치: `task/connect-inquiry-mutation-api`, parent·직접 merge 대상: `sy-main`.
- 부모 HEAD: `1d246f55f25a593e26d68a85b54e49f66874b7c1`.
- 계약 SHA-256: `15a8ddfc98c0efd04037cc24229f76f9cd33b2817ee24209e48f04bebbd41b0d`.
- worktree: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`.
- 상태: 구현 및 브랜치 계약 승인 완료. 후속 사용자 요청과 완료 계약 `5dba11e389b14c7034d5f5e6e9e4a380911cd5e0bb511269794be64e4ed8298d`의 승인으로 sy-main 병합·build 검증·CLOSED 처리까지 완료했다.
