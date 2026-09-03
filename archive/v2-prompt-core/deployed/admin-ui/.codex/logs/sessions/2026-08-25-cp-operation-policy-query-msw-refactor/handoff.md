# 인계

## 목표 및 현재 상태
- 시민참여 운영 정책 설정 화면을 fixture 직접 import 방식에서 TanStack Query + MSW 기반 데이터 흐름으로 전환하고, page → controller → process → view 구조로 분리하는 작업이다.
- Generator 구현과 자체 검증까지 완료된 `paused_after_generator` 상태이며, Watcher의 독립 판정과 완료 산출물 정리는 아직 수행하지 않았다.

## 완료된 작업
- `entities/cp-operation-policy`에 조회 DTO·parser·query key·query 및 save/apply mutation을 구성했다.
- GET `/v1/cp/operation-policy`, POST `/v1/cp/operation-policy/save`, POST `/v1/cp/operation-policy/apply` 임시 계약을 MSW handler와 연결했다.
- 페이지의 fixture 직접 import를 제거하고 controller, process, model, lib, view 책임으로 분리했다.
- `PolicyApplyPopup`, `PageHeader`, `KpiStrip`, `ActionBar`, `ChoiceChipGroup`과 보상 정책의 dirty save/apply 흐름을 재사용했다.
- `postPermission`, `commentPermission`, `reportPermission`, `defaultExposure`, `changeReason`을 저장·적용 payload에 포함했다.

## 대기 중인 작업
- Watcher가 현재 변경을 독립적으로 검토하고 PASS 또는 FAIL을 판정해야 한다.
- Watcher 판정 이후 `grill-me-review.md`, `evaluation-log.md`, `final-summary.md`, `portfolio-log.md` 등 완료 단계 산출물을 현재 세션 디렉터리에 정리해야 한다.
- 실제 backend 계약이 확정되면 임시 POST `/save`, POST `/apply` 엔드포인트와 DTO를 재검토해야 한다.

## 결정 사항 및 제약 조건
- 공용 정책 controller는 추출하지 않았다. 보상 정책과 운영 정책의 허용/차단·기본 노출 vocabulary가 달라 도메인 전용 hook을 유지했다.
- 공용 `ApiClient`에 PUT이 없어 저장과 적용을 POST 엔드포인트로 정의했다. 이는 MSW 기반 임시 계약이다.
- 정책반영 관리의 `/v1/cp/policies`와 운영 정책의 `/v1/cp/operation-policy`는 서로 다른 도메인으로 취급했다.
- 닫힌 Popup 문구가 접근성 트리에 남는 현상은 기존 공용 Popup 동작과 동일하며 이번 범위에서 변경하지 않았다.

## 관련 경로
- `src/entities/cp-operation-policy/`: API, DTO, parser, query key, query/mutation 계약
- `src/mocks/cp-operation-policy.handlers.ts`: 운영 정책 조회·저장·적용 MSW handler
- `src/mocks/handlers.ts`: 운영 정책 handler 등록
- `src/pages/cp-operation-policy/`: controller, process, model, lib, view 및 page 연결
- `src/features/cp-policy-apply/`: 적용 확인 Popup 재사용 경계
- `.codex/logs/sessions/2026-08-25-cp-operation-policy-query-msw-refactor/`: 계획·탐색·구현·검토 및 후속 산출물

## 명령어 및 결과
- `yarn tsc --noEmit`: 통과로 기록되어 있다.
- `yarn eslint <대상 경로>`: 통과로 기록되어 있다.
- 브라우저 `/cp/operation-policy`: KPI의 적용 상태와 적용일, 변경 사유 입력 후 저장 Dialog, 적용 후 마지막 적용일 갱신을 확인한 것으로 기록되어 있다.
- 이번 인계 작성 시점에는 위 명령과 브라우저 검증을 다시 실행하지 않았다.

## 다음 조치
1. 최신 대상 파일과 현재 Git 상태를 다시 읽는다.
2. Watcher가 payload 완결성, query key, AbortSignal 전달, parser 연결, MSW 요청 검증, controller-view 책임 분리를 독립적으로 판정한다.
3. FAIL이면 지적 범위만 수정하고 검증을 다시 수행한다. PASS이면 Evaluator 기록과 완료 산출물 및 `portfolio-log.md`를 작성한다.
4. backend 계약이 제공되면 임시 endpoint와 요청·응답 schema를 실제 계약에 맞춰 갱신한다.
