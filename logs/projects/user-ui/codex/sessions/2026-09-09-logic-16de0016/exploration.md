# 예약 상세 후속 탐색

## 결론과 요청 요약

반려 사유 누락과 배경 refetch의 폼 언마운트는 실제 코드에서 확인했다. 팝업 닫기 이동은 사용자가 `/meeting`으로 확정했다. 기존 DTO/parser·controlled UI·MSW·라우트 테스트를 확장하면 해결할 수 있다.

## 조사 대상과 확인한 사실

- 원본 handoff: `/Users/okand/SynologyDrive/asan-worktrees/reservation-detail-ui/.claude/logs/sessions/2026-09-09-reservation-detail-ui/handoff.md`.
- 부모 branch는 `ACTIVE`, HEAD `2184467e3270acd2d49f7652122999fc1e8061f6`, clean이다. 기존 Logic 자식은 `CLOSED`이므로 새 Logic 자식 계약을 승인받았다.
- `MeetingReserveRoute.tsx`는 `isPending || isFetching`으로 폼 대신 Loading을 렌더하고 제한 팝업 닫기에서 예약 목록으로 이동한다.
- `MeetingReservationRoutes.tsx`는 상세 UI에 안내 props를 전달하지 않는다. 상세 DTO에도 안내 필드가 없다.
- `MeetingReservationDetailPage.tsx`는 `noticeTitle`과 `noticeDescription`이 모두 undefined가 아닐 때 `NoticeBox`를 렌더한다. 빈 문자열을 함께 전달하면 빈 안내 상자가 생길 수 있으므로 유효한 쌍만 전달한다.
- `meetingReservationRead.parser.ts`는 응답 DTO를 파싱한 후 날짜·시간·참여자 표시 문자열을 만든다. 안내 표시 매핑도 이 경계에 둔다.
- `fixtures.ts`는 상태 6종을 생성한다. `handlers.ts`의 신규 신청 경로도 상세 DTO를 직접 생성하므로 안내 필드의 null 초기값을 함께 추가해야 한다.
- `useMeetingReservationReadQueries.ts`의 제한 쿼리는 진입마다 재조회하고 창 포커스 refetch는 끈다. 무효화에 의한 배경 조회는 가능하다.
- `MeetingReservationRoutes.test.tsx`는 React `act`·memory router·QueryClient·실제 feature UI와 MSW를 사용한다. 기존 제한 해제 재진입 검증을 유지하며 로비 복귀 기대값을 바꾼다.
- 인접 시민참여 라우트 테스트는 native input setter와 `input` 이벤트로 입력을 재현한다. 동일 방식을 예약 입력 보존 검증에 재사용한다.

## 재사용 자산과 새 자산 필요성

`src/shared/ui`의 Loading·Button·Popup과 예약 UI의 NoticeBox·상세 페이지를 읽었다. 새 UI 자산이나 공용 hook은 필요 없다. 기존 QueryClient 무효화와 MSW handler 옵션으로 회귀를 검증할 수 있다. 프레임워크·의존성 추가는 없다.

## 불러온 스킬

중앙 snapshot `/Users/okand/SynologyDrive/asan-agent-policy/build/user-ui/codex-logic-d32f45d9c44e9fb5/policy`에서 task-role-routing·git-branch-strategy·logic·handoff-and-ownership·pipeline-roles, skill-index·coding-convention·type-definition·data-fetch-layer·data-dto·implementation-quality·documentation을 읽었다. 소비자 저장소의 정책 사본은 사용하지 않았다.

## 성능·의존성·제약과 미확인 사항

API endpoint와 네트워크 호출 횟수를 늘리지 않는다. 배경 조회 때 폼 재생성이 없어지고 두 안내 문자열이 응답에 추가된다. 실제 서버 계약은 미확정이며 기존 화면 기반 추정 DTO 원칙을 유지한다. 인계의 lint/build 성공과 시민참여 테스트 실패는 이전 세션 결과로만 기록한다. 현재 수정의 검증은 이후 실행한다.
