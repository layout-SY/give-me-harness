# 시민참여 production UI 자체 검토

## 판정

지원되는 기능 범위 PASS, backend/UI 계약 불일치 기능 제한.

## 확인

- `/proposals/new`가 `/proposals/:proposalId`보다 먼저 선언된다.
- list filter/page/search가 URL search params와 query key에 반영된다.
- detail id는 route params에서 읽고 빈 id query는 기존 hook이 비활성화한다.
- PDF 기본 예시 대신 API projection 또는 빈 controlled value를 전달한다.
- vote/discussion 제출은 server status가 `open`이고 선택값이 있을 때만 실행한다.
- proposal category, comment report target, survey participation URL을 임의로 만들지 않았다.
- production UI 소유 경로를 수정하지 않았다.
