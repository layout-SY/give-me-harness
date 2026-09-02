# 리뷰 로그

## 리뷰 대상
- 시민참여 API·query cache·MSW·로깅 전수 감사

## 결과
- Audit document QA: pass
- Local integration readiness: fail
- Backend contract readiness: blocked

## 독립 검토 게이트

| 검토 축 | 최종 판정 |
|---|---|
| 목표·제약 충족 | PASS |
| 정적 QA 재현 | PASS |
| 문서·아키텍처 품질 | PASS |
| 보안 계약 감사 | PASS |
| 이력·문맥 누락 확인 | PASS |

- 1차 검토에서 발견된 query-key, generic MSW, PDF 증거 등급, 409, logging·권한 계약 누락을 보정한 뒤 fresh review를 수행했다.
- 보안 축은 CP 최소 권한·object-level authorization·token 보관 위협·서버 감사 로그 계약을 추가한 뒤 재검토 PASS를 받았다.

## 체크리스트 검토
- SKILL 준수: 감사 절차는 준수. 전체 CP source는 data-fetch/DTO/query 정책 미적용.
- 재사용 확인: 공용 ApiClient·AbortSignal·query factory 패턴은 Dashboard·Proposal만 재사용.
- 검증 확인: Dashboard·Proposal만 MSW 요청/응답 경로가 존재하며 자동 계약 테스트는 없음.
- Payload 완결성: Proposal 외 미정의 request payload와 unparsed response가 대부분이어서 fail. parser 전 response `unknown`은 정상 안전 경계다.
- 성능 우려: 현재 fixture 화면에는 network/cache 성능을 판정할 실제 호출이 없음.
- 중복 코드 우려: 도메인별 raw Axios API 골격이 반복되고 공통 typed client 계약이 분기됨.

## 위반 사항
1. 로컬 API operation 41개 중 4개만 MSW 업무 handler가 있다.
2. 11개 도메인이 typed DTO/parser/query/cache 없이 fixture 또는 raw Axios를 사용한다.
3. 지속 가능한 성공 HTTP structured telemetry가 없다.
4. PDF 원본과 backend API 명세가 없어 모든 CP wire contract의 검증 완료 판정이 차단된다.
5. user-ui 댓글 query key가 `size/status/myActivity/search/sort`를 누락해 참조 기준 자체에 cache collision 위험이 있다.
6. Proposal behavioral mock에 기존 계획이 요구한 409 conflict 계약이 없다.
7. `/cp/*` route에 `PrivateRoute`/`RoleBasedRoute`가 적용되지 않았다.
8. CP 전용 role/permission matrix와 object-level authorization·tenant 범위 계약이 없다.
9. `localStorage` Bearer token 보관의 위협 수용 근거와 CSP·TTL·rotation/revocation 통제가 문서화되지 않았다.
10. authoritative server audit log의 필드·신뢰 경계·보존·변조 방지 계약이 없다.

## 필수 수정 사항
1. 실제 backend OpenAPI/DTO를 확보해 임시 endpoint·payload·response를 확정한다.
2. pay/publish/apply/bulkHide의 권한·멱등성·409·감사 로그 계약을 우선 확정한다.
3. Vote부터 도메인별 `DTO/schema → ApiClient → parser → query/mutation/cache → MSW` 수직 슬라이스를 적용한다.
4. operation별로 필요한 query/body validation, pagination, 403/404/409, state mutation, 후속 조회를 N/A 근거와 함께 정의한다.
5. user-ui 댓글 query key에 전체 query dependency를 포함하도록 별도 수정 계획을 세운다.
6. `error.request` 전체 직렬화를 제거하고 redacted HTTP metadata telemetry 요구를 확정한다.
7. `/cp/*` route와 서버 API 양쪽의 인증·권한 계약을 연결한다.
8. operation별 CP 최소 권한, object-level authorization, tenant scope, 대상 상태 검증 matrix를 정의한다.
9. `localStorage` token 보관 위험을 평가하고 CSP·짧은 TTL·rotation/revocation 또는 더 안전한 session 방식의 통제를 확정한다.
10. 서버 인증 문맥 기반 actor와 operation/target/result/reason/revision/request ID/idempotency correlation을 포함한 변조 방지 감사 로그 계약을 정의한다.

## 반복 이슈
- true

## 에스컬레이션
- planner / evaluator
