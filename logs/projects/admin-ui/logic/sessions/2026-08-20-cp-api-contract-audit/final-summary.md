# 최종 요약

## 무엇이 변경되었는가
- source code는 변경하지 않았다.
- user-ui 참조 API 흐름과 known gap, admin-ui 13개 도메인 커버리지, 인수인계 문서 기반 요구사항 추적, MSW 행동 수준, HTTP telemetry 상태를 기록했다.
- 감사 산출물은 목표·정적 QA·문서 품질·보안·문맥의 5개 독립 검토 축을 모두 통과했다.

## 왜 변경했는가
- 관리자 시민참여 API 구현의 실서버 연동 준비 수준을 판정하기 위해서다.

## 재사용한 자산
- user-ui API·query 주요 참조 구조와 댓글 query-key/MSW 예외
- 기존 관리자 Dashboard·Proposal 수직 슬라이스
- PDF 파생 인수인계 문서와 현재 화면 모델

## 영향받는 영역
- Dashboard·Proposal: 현재 작업 트리에서 API 구조가 통합된 임시 계약 slice
- Vote 이하 11개 도메인: typed API/query/MSW 전환 필요
- `src/shared/api/axios-instance.ts`: 후속 logging 정책 적용 후보
- `src/mocks/handlers.ts`: 후속 도메인 handler 등록 지점

## 남은 리스크
- 최종 제품 판정은 Local integration readiness `FAIL`, Backend contract readiness `BLOCKED`다.
- `시민참여v_4.8.pdf` 원본이 없어 세부 라벨과 p39~p43 팝업을 직접 재검증하지 못했다.
- 실제 backend 명세가 없어 현재 endpoint·payload·response가 실서버와 동일하다고 보증할 수 없다.
- 지속 가능한 성공 HTTP structured telemetry가 없고 현재 `error.request` 직렬화는 정보 노출 위험이 있다.
- `/cp/*` route 권한 guard와 고위험 mutation의 권한·멱등성·409 계약이 없다.
- CP operation별 최소 권한·object-level authorization·tenant 범위와 `localStorage` token 보관의 보완 통제가 확정되지 않았다.
- authoritative server audit log의 actor 신뢰 경계, 필수 필드, 보존·접근·변조 방지 계약이 없다.
- admin 프로젝트에 CP 자동 계약 테스트가 없다.

## 후속 제안
- PDF/OpenAPI와 고위험 mutation 계약 확보 후 Vote부터 승인된 순서로 한 도메인씩 전환한다.
- telemetry는 header/query/body/token/PII를 제외하고 method, route template, status, duration, 서버 request ID, error code만 기록한다.
- telemetry operation은 allowlist된 이름/정적 route template을 사용하며 client telemetry를 서버 감사 로그로 취급하지 않는다.
- 서버는 인증 문맥의 actor와 CP permission/object scope를 검증하고 변경 전후 revision·result·reason·request/idempotency correlation을 변조 방지 감사 이벤트로 남겨야 한다.
- Bearer token 보관 방식은 CSP·짧은 TTL·rotation/revocation과 더 안전한 session 방식 전환 가능성을 포함해 별도 확정한다.
- 각 operation은 runtime parser, 완전한 query key, cache adjustment, AbortSignal, 필요한 MSW behavior·4xx 계약, 독립 contract source 기반 검증을 완료 조건으로 둔다.
