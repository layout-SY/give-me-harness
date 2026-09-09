# 탐색

## 요청

- 실제 관리자 API인 `GET /citizen/votes`, `GET /citizen/votes/{voteId}`를 시민투표 목록·상세에 연결한다.
- mutation 명세는 없으므로 조회만 구현하고 다른 동작은 실제 조회 계약을 기준으로 정리한다.

## 대상 관련 사실

- 현재 조회 client와 MSW는 legacy resource `/v1/cp/votes`를 사용한다.
- 실제 목록 query는 `page`, `size`, 반복 `sort`만 허용한다. 기본값은 `{ page: 1, size: 20, sort: ["createdAt,desc"] }`이고 size는 최대 100으로 제한된다.
- 정렬 필드는 `createdAt`, `id`, `startsAt`, `endsAt`이고 `status`는 파생값이라 정렬할 수 없다.
- 실제 상태는 `DRAFT`, `UPCOMING`, `IN_PROGRESS`, `CLOSED`, `CANCELLED`다. 기존 `VOTING`, `CLOSING_SOON`, `COMPLETED`와 일대일 대응하지 않는다.
- 목록 응답은 `{ items, total, page, size }`, 상세 응답은 `id/status/title/agenda/startsAt/endsAt/totalCount/agreeCount/disagreeCount/createdAt/updatedAt`이다.
- `voteId`는 양의 `int64`이며 목록·상세의 `id`도 number다.
- 실제 목록에는 status별 count, 작성자, 공개 기준이 없고 상세에는 작성자, 댓글, 처리 이력, 공개 정책이 없다.
- 현재 UI는 unsupported 검색 네 종류와 legacy 상태/종료일/공개 mutation을 노출하므로 transport 교체만으로는 정확한 사용자 표면이 되지 않는다.
- `src/mocks/handlers.ts`는 `createCpVoteHandlers()` 배열을 이미 등록하므로 handler 파일 내부 resource 교체만 필요하다.
- 문자열 `SUCCESS` 및 문자열 오류 code는 기존 `ApiResult` 경계에서 지원한다.

## 불러온 스킬

- 작업·승인: `policy-git-branch-strategy`, `git-master`, `skill-index`, `policy-harness`.
- TypeScript·계약: `programming`과 TypeScript `README.md`, `data-modeling.md`, `type-patterns.md`, `policy-coding-convention`, `policy-type-definition`.
- API·상태: `policy-data-fetch-layer`, `policy-tanstack-query`, `recipe-api-authoring`, `recipe-data-dto`, `recipe-data-fetch`.
- 재사용·협업: `reference-components`, `reference-custom-hooks`, `project-ui`, 루트 `CLAUDE.md`.
- 검토·기록: `policy-review-checklist`, `policy-documentation`, `policy-portfolio`.
- compact 이전 계약 복구: `coding-agent-sessions`와 세션 `ses_fa4ffb7c9ffeo48WsnnzvwhKCH`.

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| `table/` | 재사용 | 기존 목록 pagination과 row 선택 표면을 유지할 수 있다. |
| `loading/`, `dialog/` | 재사용 | 기존 query pending·오류 surface가 이미 사용한다. |
| `status/` | 재사용 | 실제 5개 상태의 label/color 설정만 도메인 model에서 교체하면 된다. |
| `ratio-bar/` | Claude Code 판단 후 재사용 | 실제 agree/disagree count로 정확한 비율을 계산할 수 있으나 markup은 UI 소유 범위다. |
| `status-transition-field/` | 제외 | 조회-only 범위에 mutation 계약이 없으므로 상태 변경 UI를 유지하면 잘못된 write를 유도한다. |
| `search-state-bar/`, `date-range-picker/`, `text-input/` | 목록 검색에서는 제외 | 실제 목록 query가 해당 검색 조건을 지원하지 않는다. |

## 제약 조건 및 미확인 사항

- 투표 mutation의 method, URI, payload, 전이 규칙과 오류 계약은 미확정이다.
- 실제 인증 backend는 사용자 지시에 따라 호출하지 않는다.
- production UI 변경은 Claude Code가 별도 세션에서 수행하고 `handoff.md`로 인계해야 한다.
- 저장소 전체 lint에는 이전 작업에서 확인된 기존 오류가 있으며 변경 파일 lint와 기준선 차이를 분리해 기록한다.

## 결론

- 외부 DTO와 내부 read model을 실제 응답 기준으로 교체하고, 반복 sort serialization·ID parsing·pagination 계산을 시민제안 통합 패턴과 동일한 계층에 둔다.
- parser는 backend에 없는 데이터를 채우지 않는다. 목록 KPI, 검색, 상세 섹션, 처리 controls는 production UI 인계 후 실제 read model만 소비하도록 연결한다.
- MSW는 실제 endpoint와 공개 error code를 재현하고 Node contract/MSW 테스트로 wire 동작을 고정한다.
