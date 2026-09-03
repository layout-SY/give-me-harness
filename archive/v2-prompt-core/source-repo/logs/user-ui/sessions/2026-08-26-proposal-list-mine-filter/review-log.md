# 검토 로그

## Watcher 판정

PASS

## 검토 범위

`GET /citizen/proposals`의 `mine`/`sort` 전송, 목록 응답에 본문 4필드 부재, 제안 목록 「내활동만 보기」가 같은 list API를 쓰는지, MSW·테스트가 그 계약을 재현하는지.

## 점검 항목

| 점검 | 결과 | 근거 |
| --- | --- | --- |
| 목표 충족 | PASS | `mine===true`일 때만 `mine=true`를 보내고, 기본 `sort=createdAt,desc`를 붙인다. 목록 토글은 `useProposalListQuery({ mine: true })`다. |
| 승인 근거 | PASS | 사용자 지시 `추가해` 이후 구현했다. |
| 불러온 스킬 | PASS | api-authoring, data-dto, data-fetch-layer, type-definition, publishing, documentation을 적용했다. |
| `src/shared/ui/` 재사용 | PASS | 새 공용 UI를 만들지 않았고 기존 `MyActivityToggle` 라벨만 바꿨다. |
| 타입 안전성 | PASS | `npm run build`의 `tsc -b`가 통과했다. `ProposalListSort`로 허용 sort를 좁혔다. |
| 요청 데이터 완전성 | PASS | `toProposalListParams`가 `page`/`size`/`sort`를 보내고 `mine`은 true일 때만 붙인다. `mine=false`·`status`·`myActivity`는 없다. |
| 중복/추상화 | PASS | 공용 activity 필터를 만들지 않았고 제안 목록만 list `mine`으로 옮겼다. |
| 검증 | PASS | 관련 vitest 62건, `npm run build`, `npm run lint` 성공. |
| 문서화 | PASS | 세션 산출물 8종을 이 디렉터리에 작성한다. |

## 발견 사항

| 심각도 | 경로 | 발견 사항 | 필수 조치 |
| --- | --- | --- | --- |
| 없음 | - | 현재 변경이 `mine`/`sort`를 잘못 보내거나 목록에 본문 4필드를 넣는 결함은 확인되지 않았다. | 없음 |

## 결론

현재 작업 범위에서 확정 계약을 충족한다. 투표 목록 activity 분기와 정렬 UI는 후속 대상이다.
