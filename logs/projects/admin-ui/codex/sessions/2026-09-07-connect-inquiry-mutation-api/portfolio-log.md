# 이력서·포트폴리오 기록

## 사례 1 — 문의 변경 API와 답변 없음 상태를 실제 서버 계약에 연결

- 작업 유형: 프로젝트 구현
- 관련 도메인/서비스: asan-metaverse-admin-ui 문의 관리
- 문제 출처: 사용자 요구

### 문제 상황

사용자가 문의 삭제·상태 변경·답변 등록·수정·삭제 API를 제공하며 기존 mock 또는 누락 기능을 실제 계약에 맞춰 연결하고 UI handoff를 요청했다. 기존에는 조회 API와 `/v1` multipart 답변 등록만 있었고 미답변 mock은 id 0인 빈 객체를 사용했다. 공용 API client에는 답변 수정에 필요한 PUT이 없었다.

### 고민과 선택

- 사용자 제안: `/admin/inquiries`의 실제 backend 계약으로 변경하고, 미답변 null에는 관리자 UI의 no-result를 표시한다.
- 에이전트 제안: 전송 API·DTO 외에 mutation hook과 캐시 후처리를 제공하고 UI의 렌더링 책임을 인계한다.
- 검토한 대안: 전송 API만 추가, 문의 도메인 hook까지 제공, 공용 CRUD framework 도입.
- 최종 선택: 기존 공용 전송 경계를 재사용하며 문의 전용 mutation hook을 제공한다.
- 선택 이유: UI에서 캐시 처리를 반복하지 않으면서 문자열 mutation 응답·상세 삭제의 도메인 의미를 보존한다. 공용 CRUD framework는 이 작업의 근거와 범위를 넘는다.

### 적용

- 변경 경로: 문의 entities, 공용 api-client.ts, 문의 MSW와 공통 등록, 문의 테스트 3개.
- 구현 내용: 5개 mutation, JSON payload와 문자열 응답 검증, nullable 답변, 공용 PUT, 상태 어휘 정합화, 캐시 취소·무효화·삭제.
- 핵심 동작: 답변 삭제 후 상세가 null로 재조회되며, 문의 삭제 후 늦게 도착한 이전 응답이 삭제된 상세 캐시를 복구하지 못하도록 처리한다. UI 담당자에게 NoResults 표시 조건을 전달한다.

### 사용 기술과 구체적 목적

| 기술·구조·패턴 | 해결하려는 구체적 문제 | 적용 위치와 방식 |
| --- | --- | --- |
| TypeScript·Zod | 미답변 null, 허용 상태 및 JSON 필드 계약 불일치 | 문의 DTO와 요청/응답 parser |
| Axios·ApiResult | 신규 PUT에서 인증·envelope·오류 흐름 이탈 방지 | 공용 ApiClient PUT 및 문의 API |
| TanStack Query | mutation 이후 오래된 목록·상세 표시 방지 | 도메인 mutation options의 취소·무효화·제거 |
| MSW·Node test | 서버 데이터 변경 없이 실제 HTTP·캐시 동작 검증 | 실제 Axios 요청, 상태 fixture, QueryClient 테스트 |
| 역할별 handoff | Logic 완료와 UI 연결 조건의 혼동 방지 | 공개 hook 매핑과 null/오류/삭제 후 표시 조건 문서 |

### 결과

- 적용 전: 조회 계약과 이전 multipart 등록만 존재하고, null 미답변 표현 및 mutation 캐시 처리가 없었다.
- 적용 후: 5개 실제 mutation API와 hook, nullable 상세, 상태가 갱신되는 MSW 및 UI handoff를 제공했다.
- 검증 결과: 전체 106개 테스트(문의 33개), build 및 변경 파일 lint 통과. 전체 lint는 기존 미변경 파일의 71 오류·5 경고로 실패했다.
- 사용자 후속 피드백: 구현 전에 answerContent가 null이며 no-result를 사용하도록 확인했다. 구현 후 사용성 피드백은 아직 없다.
- 사용자 후속 작업: Logic 작업의 sy-main 병합을 별도로 요청·승인하여 ff-only 병합, 병합 후 build 및 CLOSED 기록까지 완료했다.
- 남은 제한: 실제 backend 및 UI 통합 검증, 기존 전체 lint 개선.

### 이력서·포트폴리오 문구

- 이력서 문구: 관리자 문의 관리의 5개 변경 API를 실제 JSON 계약에 연결하고, nullable 답변·TanStack Query 캐시 동기화·MSW 검증 및 UI 인계 계약을 구현했다.
- 포트폴리오 서술: 기존 multipart 답변 등록과 불완전한 mock을 실제 서버 계약으로 이전하면서, 전송 결과가 문자열이라는 특성을 반영해 캐시 재조회와 삭제를 분리했다. 실제 Axios/MSW와 QueryClient를 사용해 답변 없음, 변경 후 조회, 늦은 응답의 캐시 복구 방지까지 검증하고 UI 담당자에게 NoResults 표시 조건을 인계했다.
