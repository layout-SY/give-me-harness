# Maintenance API 연결 계획

## 목표와 승인

기존 maintenance 모듈을 Swagger의 7개 API로 교체하고 DTO·parser·TanStack Query 조회/변경 훅을 구현한다. 사용자 `작업 진행`으로 구현 승인을 받았다.

- 역할: Logic(inject), owner. 요청 명확성: clear, can_proceed: true.
- 작업 위치: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`, `sy-main`.
- 시작 HEAD: `4b0b7db45aa9d15bf918a1a084370594e138a124`. 시작 시 미커밋 변경 없음.
- 계약 근거: `.codex/logs/sessions/swagger-api-coverage-audit/unknown/openapi.snapshot.json`의 `/maintenance` 7개 operation과 사용자 답변. 저장된 명세 기준이며 최신 원격 명세나 실서버 동작을 검증한 것으로 보지 않는다.
- 사용자가 기존 모듈 교체와 Swagger 경로 통일을 확정했다. `VITE_SYNTHORIA_CONFIG_RESOURCE` override를 제거한다.
- 조회 항목의 `id/key/value/createdAt/updatedAt`은 모두 필수이며 null을 허용하지 않는다. 기존에 확정된 8개 설정 키를 유지한다.
- 모든 PATCH의 성공 data는 null이다. 기존 ApiClient가 undefined로 정규화하며 공통 성공·실패 판정과 unwrap을 재사용한다. 반환 data를 문자열 등으로 검증하지 않는다.
- 요청의 required·길이·시간 형식은 Swagger를 따른다. 문서에 없는 시간대 변환·시간 선후관계·버전 형식 제한·설정값 변환을 추가하지 않는다.

## 변경과 재사용

1. 같은 workdir의 `src/entities/maintenance/api/`에서 기존 Axios 직접 호출·구 DTO를 factory/요청 schema/응답 parser로 교체한다. 일괄 수정은 `{config:[{key,value}]}` 한 요청으로 전송한다.
2. `src/shared/api/api-client.ts`, `common/response.dto.ts`, `common/api-result`, `axios-instance.ts`, `with-abort-signal.ts`를 재사용한다. 공통 envelope는 복제하지 않는다. 조회는 unknown payload를 캐시에 넣기 전에 한 번 검증한다.
3. 인접 `entities/inquiries`·`entities/usage`의 query options·mutation options·훅 패턴으로 maintenance 전용 파일을 추가한다. 단건 key를 query key에 포함하고, 변경 성공 시 maintenance 조회를 취소한 뒤 무효화한다. 전용 PATCH의 내부 설정 변경 범위를 추측하지 않아 maintenance 도메인의 조회를 함께 갱신한다.
4. 기존 타입 회귀 검증을 새 필드 계약으로 바꾸고 `tests/maintenance-contract.test.mjs`, `tests/maintenance-query-mutation.test.mjs`를 추가한다. 기존 node:test·tsx·Vite·MSW를 재사용한다. MSW는 테스트 안에서만 사용하며 실제 점검 상태 변경 요청은 실행하지 않는다.

## 검증과 산출물

- 중앙 `formatting.py apply`로 수정한 코드만 실제 Prettier 포맷한다.
- `node --test tests/maintenance-contract.test.mjs tests/maintenance-query-mutation.test.mjs tests/logic-api-types.test.mjs`로 DTO·요청·응답·인증·업무/HTTP/전송 실패·취소·캐시 갱신을 확인한다.
- `npm run lint`, `npm run build`, `git diff --check`를 실행하고 최종 diff와 검증 결과를 기록한다. package.json에 test script는 없다.
- 자기 세션 `final-summary.md`에 실제 변경·검증·제한을 기록한다. UI 화면 생성과 Git stage/commit/merge/push는 승인 범위에 포함하지 않는다.

## 적용 정책

task-role-routing, git-branch-strategy, recipe-api-authoring 및 transport/query 참조, data-fetch-layer, type-definition, coding-convention, implementation-quality, documentation을 읽었다. 재사용 근거는 실제 shared API와 inquiries/usage 파일, 기존 타입·MSW 테스트다.

## 완료 결과

7개 API·DTO·parser·조회/변경 훅과 기존/신규 테스트 작성 완료. 중앙 Prettier 14개 파일 적용 및 최종 확인 완료. 대상 테스트 16개와 lint·build·diff 검사 모두 통과했다. 미확인 쓰기 예약 차단은 승인된 복구와 확인된 외부 상태 변경 후 해소되었다. 최종 검증 근거와 빌드 경고·실서버 미검증 범위는 final-summary.md에 기록했다.

## Controller 추가 — 사용자 승인 후 진행

사용자 `그럼 일단 이 패턴대로 controller 구현해봐`로 UI–Logic adapter 구현을 승인했다. 공지사항·아이템·출석 이벤트의 model 타입, lib mapper, controller hook, View 소비 구조를 확인했다. Logic 역할과 같은 workdir에서 진행하며 화면 렌더링은 추가하지 않는다.

- `src/pages/maintenance/model/maintenance-controller.types.ts`에 목록·단건 데이터, 조회 상태·재시도, 변경 입력과 제출 상태·콜백 계약을 정의한다.
- `lib/maintenance-controller.model.ts`에서 응답 필드를 명시적으로 옮기고 UI 입력을 Swagger 요청 DTO로 검증·변환한다. 공통 envelope와 transport, 기존 Query/Mutation을 재사용한다.
- `hook/`에서 목록·단건 조회 및 변경 5종을 조합한다. UI는 입력을 콜백으로 전달하고 controller는 중복 제출·취소·성공·실패를 처리한다. 폼 입력의 보관·레이아웃은 이 계약 소비자에게 남긴다.
- 단건 키 미입력은 조회를 비활성화하고 UI 오류로 제공한다. 설정 문자열·날짜 원문·optional·빈 문자열 계약을 유지한다. 전용 API가 어떤 설정 키를 바꾸는지, boolean 표현·시간대를 추측하지 않는다.
- 새 controller 회귀 테스트와 기존 maintenance 16개 테스트, 중앙 포맷·lint·build를 실행한다. 커밋은 controller 검증 이후 별도 Git 승인 절차로 처리한다.

Controller 구현과 검증 완료: 신규 테스트 11개를 포함한 27개 테스트, lint·build·diff 검사가 통과했다. 추가 변경 12개 소스·테스트를 중앙 Prettier로 포맷했다. UI 계약·사용법·검증 범위는 final-summary.md에 기록했다.

사용자 커밋 요청 및 실행 승인 후 `sy-main`에 `b5c35a8` (`feat: maintenance API 및 controller 구현`)을 생성했다. maintenance 관련 22개 파일만 포함했으며, 다른 작업의 `docs/admin-routes.md`는 미추적 상태로 보존했다. push는 수행하지 않았다.
