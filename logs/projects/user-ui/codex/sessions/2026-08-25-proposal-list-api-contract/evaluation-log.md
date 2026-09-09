# 평가 로그

## 현재 판정과의 경계

여기서는 Watcher 판정을 다시 평가하지 않는다.

## 장기 관찰 사항

- proposal 상세·작성 응답이 확정되면 목록의 숫자 `id`와 상세 path 계약을 한 번에 맞춰야 한다. 지금은 MSW/상세가 문자열 id를 유지한다.
- `/me/activity` 응답이 목록과 같은 `{ items, total, page, size }`가 되면 `ActivityListResponseDto`를 다시 나눠야 한다.
- `toApiResult`가 `SUCCESS`와 `success: true`를 함께 받는 상태는 백엔드 envelope가 도메인마다 다를 때의 임시 공존이다. 시민참여 전체가 SUCCESS로 통일되면 공용 `ServerResponse` 타입을 재검토할 수 있다.

## 목록에 등록할 재사용 가능 자산

없음. 새 공용 UI/훅을 추가하지 않았다.

## 기술 부채

- `ProposalListPage`는 응답에 없는 `summary`를 빈 문자열로 받아 빈 `<p>`를 그릴 수 있다.
- `REJECTED`는 목록 API 상태값이나 기존 UI 매퍼가 카드를 숨긴다.
- 전체 vitest에서 auth/meeting 테스트 3건이 실패했다. 이번 변경 경로 밖의 기존 실패로 보이며 별도 추적 대상이다.

## 프로세스 개선 사항

목록 계약과 필터 계약을 한 번에 주지 않고 대화 중에 바뀌었다. 이후에는 요청 필드와 별도 필터 API를 같은 확정 문서에 묶어 전달하면 DTO를 두 번 설계하지 않아도 된다.

## 권고 사항

activity 응답과 proposal 상세가 확정되면 목록 매퍼의 이중 경로(`toProposalListItem` / `toProposalActivityListItem`)를 줄일 수 있다.
