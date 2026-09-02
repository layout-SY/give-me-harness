# 검토 로그

## Watcher 판정

PASS

## 검토 범위

- Logic Session이 소유한 투표 댓글 DTO, parser, API, mutation, mock, 회귀 테스트
- 승인된 브랜치와 파일 범위 준수 여부
- Claude Code production UI 인계를 위한 경계의 완결성
- production UI 자체 연결 완료 여부는 이번 PASS 범위에 포함하지 않는다.

## 점검 항목

| 점검 | 결과 | 근거 |
| --- | --- | --- |
| 요청 경로·method | PASS | API 테스트가 단순 ID의 DELETE method·path를 검증하고, `vote.api.ts` 구현 확인으로 두 ID의 `encodeURIComponent` 적용을 확인 |
| 인증 설정 | PASS | `voteApi`가 `customConfig`를 전달하고 실제 `voteClient`가 access token interceptor를 가진 공유 Axios instance를 사용함을 구현에서 확인; endpoint 테스트는 header 자체를 검증하지 않음 |
| 응답 데이터 보존 | PASS | schema와 parser가 `likeCount`, `liked`를 검증·매핑 |
| optimistic update | PASS | 성공 테스트에서 mutation 완료 전 감소 상태 관찰 |
| rollback | PASS | 서로 다른 두 query cache를 준비한 404 테스트에서 두 snapshot의 원래 count·상태 복원 관찰 |
| 서버 재동기화 | PASS | DELETE 성공과 404 실패 후 두 query state의 `isInvalidated`를 직접 관찰 |
| MSW 계약 | PASS | 200/null, 404/`LIKE_NOT_FOUND`, 재조회 상태 검증 |
| 회귀 검사 | PASS | 460 Vitest tests, 20 governance tests, lint, build 통과 |
| 변경 범위 | PASS | production UI와 패키지 설정을 수정하지 않음 |

## 발견 사항

| 심각도 | 경로 | 발견 사항 | 필수 조치 |
| --- | --- | --- | --- |
| Medium | `src/pages/citizen-participation/ui/CitizenParticipationDetailRoutes.tsx:97` | `VoteDetailRoute`가 기존 `nextLiked` 인자를 mutation에 전달하지 않아 현재 production UI에서는 취소 클릭도 POST로 남는다. | Claude Code가 인계서의 콜백 연결을 적용한 뒤 통합 검증한다. |
| Info | `src/features/citizen-participation/hook/useCitizenParticipationMutations.ts:28` | UI 연결 전 호환을 위해 `nextLiked`가 optional이다. | 모든 caller가 명시적 상태를 전달한 후 required 전환을 검토한다. |
| Info | `src/features/citizen-participation/api/http/voteComments.api.test.ts:95` | endpoint 테스트는 격리 Axios instance를 사용해 access token header 자체는 관찰하지 않는다. | 공유 interceptor 회귀 테스트를 정본으로 유지하고 endpoint별 header 중복 테스트가 필요한지는 별도 범위에서 결정한다. |
| Info | build output | 기존 프로덕션 chunk가 500 kB 경고 기준을 초과한다. | 이번 범위에서는 조치하지 않고 별도 성능 작업으로 분리한다. |

## 결론

- 초기 Watcher FAIL에서 지적된 다중 query rollback·성공/실패 invalidation 증거를 hook 테스트에 추가했고, 문서의 encoding·인증 근거를 구현 확인과 테스트 확인으로 분리했다.
- Logic Session 범위는 최종 독립 재판정 기준 PASS다. transport, parser, cache 전이, 오류 복구가 테스트와 구현에서 일치한다.
- 전체 사용자 흐름은 `handoff.md`에 명시한 production UI 한 줄 연결이 완료된 뒤 최종 완료로 판정해야 한다.
