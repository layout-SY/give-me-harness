# 시민제안·투표 API 연결

기존 전역 Swagger 인계의 T01 승인 범위를 이어서 구현한다. 최신 OpenAPI 조회에서 제안·투표 8개 operation 중 누락된 4개를 현재 소스와 대조했다.

- 역할: Logic. 현재 사용자의 추가 연결 요청과 `swagger-api-coverage-audit/handoff.md`의 T01 구현 승인·확정 계약을 적용한다.
- 작업 위치: `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/citizen-proposal-vote-api`.
- branch: `feature/citizen-proposal-vote-api`, 직접 부모 `sy-main`, 시작 HEAD `4b0b7db45aa9d15bf918a1a084370594e138a124`. 시작 시 미커밋 변경 없음.
- 확인한 명세: 2026-09-28 `https://admin-api.oasis.shovvel.com:8443/v3/api-docs`의 성공 응답. 실제 업무 API는 호출하지 않는다.

## 변경 계획

1. 같은 작업 공간의 기존 cp-proposal API·DTO·parser를 확장하여 상태 PATCH와 review-result PATCH를 연결한다. 공통 ApiClient/envelope 처리를 재사용하고 UI 상태를 서버 상태로 변환하며 빈 성공 응답을 처리한다.
2. 상세 reviewResult를 기존 reviewComment에 매핑한다. 기존 확정 계약대로 null/누락은 빈 문자열로 표시한다. 검토 결과 제출은 공백 거부·trim·최대 5,000자를 검증한다.
3. 제안·투표 summary DTO·query를 기존 도메인 경계에 추가하고 목록 KPI에 연결한다. 목록 검색 건수와 전역 집계를 구분한다. mutation 성공 시 필요한 목록·상세·집계 캐시를 갱신한다.
4. 담당부서 선택은 기존 확정대로 미지원 안내 후 변경 요청을 차단한다. 기존 controller·KPI·callback 계약을 재사용한다.
5. 개발용 제안·투표 MSW handler 등록과 citizen 경로 mock 전용 판정을 제거한다. 기존 테스트 전용 fixture와 다른 도메인의 handler는 보존한다.
6. 동일 공간에서 바인딩된 formatting.py apply 실행 후 관련 node:test, npm run lint, npm run build를 실행한다. method/body/상태 매핑/빈 성공/오류/캐시/입력 경계/MSW 비가로채기를 확인한다.

## 근거와 재사용

`src/shared/api/common/response.dto.ts`, ApiClient·unwrapApiResult·withAbortSignal, cp-proposal/cp-vote API·DTO·parser·query keys, 목록·상세 process hook, KpiStripItem, useDialog를 조사했다. task-role-routing, git-branch-strategy, data-fetch-layer, api-authoring와 전송·query 참조, coding-convention, type-definition, validation, implementation-quality, documentation 스킬을 확인했다.

## 승인·완료와 Git

초기 DTO 수정은 현재 세션의 구현 승인 미확인으로 차단되었다. 이후 사용자가 “작업 진행”으로 위 계획을 명시적으로 승인하여 구현과 검증을 완료했다. 실제 포맷 완료, 관련 테스트 46개 통과, 최종 lint/build 통과, git diff --check 통과다. 자세한 내용은 final-summary.md를 따른다. 새 UI 구조와 Git stage/commit/merge/정리는 포함하지 않는다.
