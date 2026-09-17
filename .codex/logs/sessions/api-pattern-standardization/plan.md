# Logic/API 패턴 분석·정리 계획

두 소비자 프로젝트의 API 연결을 전수조사하고 기존 공통 스킬을 확장한다. 사용자가 승인한 분석 역할과 후속 요청에 따라 상세 조사 문서·개선 근거·기존 문제·포트폴리오·활성 세션 산출물 조사까지 수행한다.

## 범위와 결정

- user-ui/admin-ui의 공유 전송부터 각 도메인의 DTO/parser, Query, mutation, 실제 entry 연결까지 조사한다. admin video/event 별도 worktree의 변경본도 기준본과 구분한다.
- 기존 api-authoring/data-fetch/data-dto와 admin use-api reference를 재사용한다. 거대한 신규 API registry나 무조건적인 파일 이동을 만들지 않는다.
- user-ui useApi는 사용자의 선택에 따라 admin-ui의 최신 호출 우선·최신 완료 시 로딩 종료로 변경한다. user-ui의 판별 union, 오류 표시 정책과 unmount 취소는 유지한다.
- 활성 스킬/지침의 오래된 스택 가정을 제거한다. 중앙에는 해당 안내가 없고 전역 AGENTS.md에 있으므로 그 원본을 수정한다.
- 실제 소비자 세션의 산출물 위치와 주입된 정책을 대조한다. 다른 세션의 문서를 대신 작성하지 않는다.

## 효율·장기 영향

불변 계약은 짧은 스킬 본문, 전송과 Query 상세는 references로 나눈다. 서버 상태를 Query에 맡겨 중복 loading/state를 줄이고, sequence ref로 UI에 반영할 요청만 판정한다. endpoint별 인증·nullable·반환 타입 차이를 보존한다. 미연결 레거시를 표준 사례로 재사용하지 않게 목록에 연결 상태를 표시한다.

## 예상 변경

중앙 스킬 4개 수정, 참조 문서 2개 추가, 조사/전수 목록/세션 조사 문서와 근거 JSON 추가. user-ui use-api.tsx와 회귀 테스트 변경, 전역 AGENTS.md 레거시 안내 제거. 기존 다른 세션의 dirty 변경과 commit은 보존하며 자동 commit/merge하지 않는다.

## 검증

useApi 새 요구 회귀를 기존 구현에서 실패시킨 뒤 수정한다. hook 및 직접 소비처 테스트, 전체 테스트, lint, build를 실행한다. 중앙 unittest와 audit를 실행한다. 조사 문서의 모든 파일과 스킬 참조가 실제 존재하는지 확인하고, 포트폴리오에는 실제 검증 결과와 한계를 적는다.

## 권한과 인계

후속 사용자 요청은 위 수정의 작업 승인을 제공한다. 소비자 코드·전역 안내·중앙 .codex 산출물은 쓰기 sandbox 밖/보호 경로이므로 정확한 파일별 쓰기 승인을 사용한다. 이미 실행 중인 소비자 세션에는 수정 bundle이 자동 적용되지 않으며, 각 담당 세션이 handoff 후 새 inject 세션으로 이어야 한다.
