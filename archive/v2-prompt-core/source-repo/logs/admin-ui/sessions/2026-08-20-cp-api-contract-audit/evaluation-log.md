# 평가 로그

## 컨텍스트
- user-ui 기준 API 흐름을 관리자 시민참여 전체 도메인에 적용할 수 있는지 평가한다.

## 구조적 리스크
1. typed API 흐름과 raw Axios/fixture 흐름이 공존해 도메인별 오류·cache 동작이 달라진다.
2. PDF UI label 모델이 wire DTO로 오인될 수 있다.
3. mock coverage가 로컬 API operation 4/41에 편중되고 자동 계약 테스트가 없어 실제 연동 오류를 조기에 발견하지 못한다.
4. 지속 가능한 HTTP telemetry가 없어 route template·status·duration·request ID를 일관되게 추적할 수 없다.
5. 운영 변경 API의 idempotency·권한·revision·동시성 계약이 없다.
6. user-ui 댓글 query key가 전체 request query를 표현하지 않아 잘못된 cache 공유 위험이 있다.
7. `/cp/*` route가 인증·역할 guard 없이 노출된다.
8. 등록된 admin role 전체 허용과 CP operation별 최소 권한 사이의 구분이 없고 object-level authorization·tenant 범위 계약이 없다.
9. `localStorage` token 보관 위협과 서버 감사 로그의 신뢰·보존·변조 방지 기준이 확정되지 않았다.

## 왜 중요한가
- 관리자 처리 mutation은 상태 변경·노출·보상 지급을 포함하므로 stale cache나 중복 요청이 실제 운영 데이터 오류로 이어질 수 있다.

## 개선 옵션
1. 기존 승인 순서대로 Vote부터 한 도메인씩 Proposal 패턴으로 전환한다.
2. backend 명세 확정 전에는 DTO와 endpoint를 `임시 계약`으로 문서화하고 parser 경계에서 격리한다.
3. `error.request` 직렬화를 제거하고 Axios interceptor 또는 telemetry adapter에 redaction된 HTTP metadata logging을 추가한다.
4. MSW handler를 실제 backend contract test와 공유 가능한 request/response fixture로 구성한다.
5. route guard와 서버 권한 검사를 함께 정의하고 client telemetry와 서버 감사 로그를 분리한다.
6. CP permission matrix와 object-level authorization을 operation·target state·tenant scope 단위로 정의한다.
7. token 보관 방식의 위협 모델과 CSP·TTL·rotation/revocation 또는 session 전환 통제를 문서화한다.
8. 서버 인증 문맥의 actor와 변경 전후 revision을 포함한 authoritative audit event를 변조 방지 저장소에 기록한다.

## 권장 백로그
1. P0 계약 선행: OpenAPI/backend DTO 및 PDF 원본 확보
2. P0 금전·노출·운영 상태: pay/publish/apply/bulkHide의 validation·권한·idempotency·revision·409 확정
3. P0 접근 제어: `/cp/*` route guard와 서버 권한 계약 연결
4. P0 최소 권한: CP permission matrix, object-level authorization, tenant scope, 대상 상태 검증
5. P0 인증 토큰: `localStorage` 위협 수용과 CSP·TTL·rotation/revocation/session 통제 확정
6. P0 moderation/audit: p27~p33 request/response와 authoritative server audit log 신뢰·필드·보존·변조 방지 계약 확정
7. P1 기준선 수정: user-ui 댓글 query key 전체 dependency 반영
8. P1 순차 구현: Vote → Discussion → Policy → Survey → Comment → Report → Board/Notice → Activity Log → Reward → Main Display → Operation Policy
9. P1 관측성: raw `error.request` 제거, allowlist operation 기반 redacted HTTP telemetry와 서버 request ID 연동
10. P1 계약 검증: operation별 MSW/contract test와 미등록 요청 실패 정책
11. P2 mapping: UI label 모델과 wire DTO의 명시적 mapping layer 정리

## 다음 단계 제안
- PDF와 backend 명세 및 고위험 mutation 계약을 먼저 확보한 뒤 Vote 수직 슬라이스 계획을 승인받아 구현한다.
