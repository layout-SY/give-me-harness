# 가상 오피스 Swagger 비교 분석

- 요청: Swagger 가상 오피스 명세와 현재 임시 API의 연결·데이터·구조 차이 분석.
- 역할: inject로 확인된 Logic. 구현·Git 변경은 요청 범위에 포함하지 않는다.
- 작업 위치: `/Users/okand/SynologyDrive/asan-metaverse-user-ui`, `sy-main`, HEAD `5df71dc0aed38ba793f5cb413b9bd2e2ce070bc1`.
- 기존 변경: `README.md`, `docs/meeting-api-contract.md`. 읽기만 수행하고 보존한다.
- 근거: 사용자 제공 Swagger 발췌의 8개 연산, 현재 소스, `docs/meeting-api-contract.md`, `docs/meeting-expected-api.md`, `docs/meeting-architecture.md`, `docs/agora-rtc-contract.md`.
- 범위: 현재 checkout의 예약 기반 회의실 입장 흐름을 중심으로 기존 `/meeting` RTC 화면과 예약 MSW도 구분한다. 다른 linked worktree의 변경은 분석 기준에 포함하지 않는다.
- 방법: endpoint → DTO/parser → controller → 화면 소비 지점을 추적하고 확인된 불일치, 재사용 가능 부분, 명세 미확인 사항을 분리한다.
- 적용 스킬: task-role-routing은 Logic 범위·요청 명확성, git-branch-strategy는 읽기 전용 상태 확인, documentation은 자기 세션의 근거·결과 기록에 적용한다. api-authoring은 API 계층 비교 참고로 읽었으며 구현은 수행하지 않는다.
- 재사용 조사: `shared/api/api-client.ts`, 공통 응답 mapper, 기존 RTC parser, `useAgoraMeeting`, 장치 검사, 입장 controller, 예약 DTO·MSW 및 Vite 임시 서버.
- 검증: 정적 코드·사용처 대조. 서비스 호출·자동 테스트·빌드로 검증한 것으로 보고하지 않는다.

## 진행 결과

- Swagger 직접 접근과 `/v3/api-docs` 조회는 8443 연결 시간 초과. 같은 호스트 443도 시간 초과.
- 사용자가 8개 회의실 API 발췌를 제공하여 명시된 계약 비교를 진행했다.
- 최종 비교와 미확정 계약은 `final-summary.md`에 기록한다.
