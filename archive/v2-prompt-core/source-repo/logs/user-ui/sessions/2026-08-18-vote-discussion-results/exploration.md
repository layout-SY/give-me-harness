# 탐색

## 결론

전체 집계 count는 이미 목록·상세 공통 API 응답에 포함돼 있어 새 집계 응답 형식은 필요하지 않았다. 누락 지점은 상세 presentation 매핑과 진행 중 Discussion 목록의 공개 정책이었다.

## 기존 API 계약

| 대상 | 응답 필드 | 상태 |
| --- | --- | --- |
| Vote 목록·상세 | `agreeCount?`, `disagreeCount?` | Zod parser와 MSW에 존재 |
| Discussion 목록·상세 | `agreeCount?`, `disagreeCount?`, `neutralCount?` | Zod parser와 MSW에 존재 |

## 발견된 결함

- `toVoteDetail`, `toDiscussionDetail`이 count를 버렸다.
- `toDiscussionListItem`은 `open` 상태에서도 ratio를 생성했다.
- Discussion route는 선택한 찬성·반대·중립 값을 POST body에 전달하지 않았다.
- generic MSW mutation은 성공만 반환하고 사용자 선택을 저장하지 않았다.
- route는 mutation의 `completed`를 Claude UI `hasSubmitted`에 전달하지 않았다.

## 확정 정책

- `closed`: 전체 투표·토론 종료이며 집계 공개 가능.
- `hasSubmitted`: 현재 사용자 제출 완료이며 전체 상태는 계속 `open`일 수 있음.
- `open + hasSubmitted`: 선택·제출 비활성화와 완료 문구만 표시하고 결과는 숨김.

## UI 준비 상태

Claude Code의 Vote·Discussion 목록·상세는 ratio props, ResultBar, `hasSubmitted`, 완료 문구와 disabled 계약을 모두 제공해 route 연결 가능한 상태였다.
