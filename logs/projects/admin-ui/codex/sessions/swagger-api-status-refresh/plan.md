# Swagger API 작업 현황 갱신 계획

사용자가 2026-09-29에 요청한 문서 갱신과 다음 작업 목록 보고를 수행한다. 기능 구현이나 Git 변경은 이번 범위에 포함하지 않는다.

- 역할: inject Logic, owner.
- 요청 확정: “일단 문서 갱신 후에 다음 작업이 뭐가 있는 지 말해봐”. 후속 기능 선택을 이번 문서 작업의 선행 조건으로 두지 않는다.
- 작업 위치: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`, `sy-main@84d47a87f032ec5cc106f4fad8ec3a9709e901e1`.
- 재사용 근거: 기존 `swagger-api-coverage-audit/unknown/`의 OpenAPI 스냅샷·계약·작업 문서. 다른 세션 기록은 읽기 전용으로 보존한다.
- 결과물: [최신 작업 현황](./unknown/api-work-items.md). 원본 명세를 다시 수집하거나 서버 계약을 변경한 것으로 표현하지 않는다.

## 수행 항목

1. 기본 checkout에서 기존 기준 `4b0b7db` 이후 Git 변경과 실제 API·DTO·controller를 비교하여 문서의 오래된 완료 상태를 갱신한다.
2. 같은 저장소의 문의 UI worktree를 읽기 전용으로 확인하여 기본 브랜치 반영과 별도 구현 완료를 구분한다.
3. 현재 세션 문서에 T01~T13의 완료·잔여·확인 필요 사항과 근거 경로를 기록한다.
4. 로컬 링크, 작업 번호 누락, 스냅샷 규모와 Git 상태를 확인한다. 소스 변경이 없으므로 앱 테스트·lint·build는 실행하지 않는다.

## 경계

- 소스·패키지·다른 세션 로그를 수정하지 않는다.
- 실제 업무 API, 원격 Swagger 재조회, 브라우저 검증은 이번 갱신 근거가 아니다.
- 후속 기능의 정책·계약 공백은 미확정으로 유지하고 구현하지 않는다.

## 후속 승인: 이용 내역 API·controller 구현

사용자가 별도 브랜치·워크트리에서 이용 내역 API 연결을 요청하고, 화면 없는 controller까지 구현하도록 승인했다. 날짜 기본값 없이 입력 후 조회, 시작일이 종료일보다 늦으면 차단, 검색 기준·검색어 동시 입력, 응답 필드 필수·null 허용 및 objectName 보정을 확정했다. 최대 기간에 대한 수치를 확정하지 않았으므로 임의 제한을 추가하지 않는다.

- 생성 완료: `feature/usage-api-controller`, 부모 `sy-main`, 기준 `c6ed8d3c09fe3d4ecedd608f2c314795038d5b73`.
- 작업 위치: `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/usage-api-controller`.
- 승인 Git 생성 작업 `7af0e8a93daa4b3992409c2217cf8796`: done. 기존 `84d47a8` 기준 작업은 문의 UI 병합으로 무효화되어 실행되지 않았다.
- 재사용: `entities/usage` API·DTO·parser·query keys/options/hooks, 공통 `PageResponseDto`/`createPageResponseSchema`, `isoCalendarDateSchema`, 기존 node:test·MSW·Vite SSR controller 테스트 방식. 기존 maintenance/inquiry/news controller의 공개 입력·상태·콜백 패턴을 참조한다.
- 예상 변경: usage의 포인트/아이템별 날짜·검색 schema, objectName/정수/명세 enum 응답, null 입력 시 비활성 query, `pages/usage`의 화면 없는 controller와 공개 타입, 관련 테스트. page 기본 1·size 기본 20은 Swagger 값을 사용한다.
- controller 계약: 날짜·검색어 입력과 적용 조건 분리, 제출/초기화/페이지 이동/재시도, 행과 페이지 메타, 조회 전/로딩/빈 결과/오류 구분. Logic 선행이므로 이후 UI가 이 계약을 사용한다.
- 테스트: 입력 오류 시 HTTP 없음, 두 API의 필터·인증·sort·취소·캐시, nullable/누락/enum/정수, controller 제출 전 미조회·새 조건 첫 페이지·초기화·실패·재시도.
- 검증 순서: 실제 formatter → usage 관련 node:test → lint → build. 완료 후 자기 문서에 UI 인계 계약과 결과를 기록한다.
- UI 마크업·라우트·메뉴·레거시 `/v1/usage` 변경, commit·merge·push는 이번 승인 범위에 포함하지 않는다.
