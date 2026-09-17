# 조사 결과

두 프로젝트의 신규 API는 factory→ApiClient→DTO/parser→TanStack Query라는 공통 책임을 공유하지만 전체 도메인에 일관되게 적용되지는 않는다.

## 전수 범위

[전수 목록](/Users/okand/SynologyDrive/asan-agent-policy/docs/api-pattern-inventory-2026-09-17.md)과 근거 JSON에 고유 API 경로 60개를 기록했다. user-ui 14, admin-ui 기준본 44 + video worktree 2이며, event 변경본 2행을 따로 추가하여 관찰 62행이다. 최초 조사 이후 usage API가 추가되었음을 명시했다. TypeScript AST의 값 import/export로 U 14/14, A 16/44 entry 도달을 확인했다. 정적 도달은 실 API 실행 증거가 아니다.

## 재사용 자산

기존 api-authoring/data-fetch/data-dto skill, ApiClient/ApiResult/withAbortSignal, shared unwrap, query/mutation options, 오류 reporter를 확인했다. 새 registry 대신 이 자산의 계약을 스킬에 남겼다. admin news·items·category·users·inquiries·video·usage 신규 계층, CP 14 도메인, 일반·DAO·event 레거시, auth·meeting fetch 예외를 구분했다.

## 주요 발견

- user-ui useApi는 active count와 모든 응답 반영, admin-ui는 최신 sequence 정책이었다. 반환 형식도 달라 동시 요청 정책만 맞추도록 결정했다.
- CP 상세 캐시 갱신 전 조회 취소의 일관성, user mutation 응답 검증, 중복 unwrap/abort helper가 개선 대상이다.
- 미연결 DAO 두 POST는 config를 body 위치로 전달한다. 기준본 attendance의 개발 fallback은 실제 실패를 숨길 수 있다. event 담당 worktree에서 개선 중이었다.
- 활성 중앙 정책에는 React 18/Jotai 지시가 없었다. 전역 /Users/okand/.codex/AGENTS.md에 이전 스택 지시가 남아 있었다.
- 실제 정책 환경으로 확인한 소비자 프로세스 6개는 모두 portfolio 파일이 없었다. 주입 정책은 portfolio를 optional로 분류한다.

세부 코드 근거·영향·개선 완료 기준은 [조사 보고서](/Users/okand/SynologyDrive/asan-agent-policy/docs/api-pattern-audit-2026-09-17.md)에 있다. 과거 bundle은 세션 의무 확인의 데이터로만 읽었고 정책 정본으로 사용하지 않았다.
