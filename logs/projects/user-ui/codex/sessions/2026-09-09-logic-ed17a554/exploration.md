# 탐색

## 결론

기존 ApiClient, parser, query hook과 controlled UI를 확장해 연결할 수 있다. 서버 명세는 없고 사용자가 최신 UI handoff의 추정 DTO를 mock 기준으로 지정했다.

## 조사 대상 및 사실

- UI 인계: reservation-detail-ui worktree의 `.claude/logs/sessions/2026-09-09-reservation-detail-ui/handoff.md`. 최신 HEAD `b5b07fa`는 상세 정렬과 취소 팝업을 포함한다.
- 예약 feature의 api/model/hook/mocks/ui, 예약 route, app routing·MSW 시작 코드, shared ApiClient/ApiResult와 dialog/loading/pagination을 읽었다.
- 신청과 옵션 조회는 있지만 목록·상세·취소·제한 조회는 없다.
- 기존 mock 날짜가 `2026-09-08`에 고정돼 현재 시각에서는 폼 제출이 불가능하다. 실행 시각에 맞는 fixture 및 테스트 시각 주입이 필요하다.
- 목록은 mine/invited와 페이지를 받고 상세는 표시 문자열과 cancelable, inviteCodeRevoked를 받는다. 취소 팝업은 기존 상세 데이터와 취소 응답으로 연결 가능하다.
- 워커는 `VITE_API_BASE_URL_STATUS=dev`에서 예약 testing export를 이미 등록한다.

## 재사용 결정

| 자산 | 목적 |
| --- | --- |
| shared ApiClient·ApiResult | 인증 옵션·응답 봉투·실패 경계 유지 |
| 기존 예약 query·mutation hook | key·AbortSignal·무효화 패턴 확장 |
| controlled 예약 화면과 취소·제한 팝업 | 최신 props/callback 연결 |
| shared Loading·dialog | 조회 대기와 요청 오류 전달 |
| MSW handler factory | 테스트별 상태 초기화 및 브라우저 mock |

상태 조율 hook은 예약 feature가 소유한다. key에 탭·페이지·상세 ID를 포함하고 AbortSignal을 전달한다. 공용 hook 추출과 새 패키지는 불필요하다.

## 스킬 및 검증 제한

policy-task-role-routing, policy-git-branch-strategy, skill-index, recipe-api-authoring, policy-data-fetch-layer, policy-type-definition, policy-coding-convention, policy-implementation-quality, policy-documentation, reference-custom-hooks를 읽었다.

실제 backend 호환성은 명세 부재로 확인할 수 없다. 10자리 코드, 시작 5분 전 취소 제한, 상태 6종은 화면 명세 근거를 따른다. 기존 시민참여 실패 보고는 실행 전까지 현재 실패로 단정하지 않는다.
