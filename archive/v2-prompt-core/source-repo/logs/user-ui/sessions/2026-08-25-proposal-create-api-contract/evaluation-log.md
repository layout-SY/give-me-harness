# 평가 로그

## 현재 판정과의 경계

여기서는 Watcher 판정을 다시 평가하지 않는다.

## 장기 관찰 사항

- Axios interceptor가 `response.data`만 넘기면 REST 201 Location을 잃는다. 생성처럼 헤더가 계약인 API가 늘면 unwrap 단계에 헤더 보존이 필요하다.
- proposal 생성 필드명(`background`/`content`/`expectedEffect`)과 상세 GET 필드명(`body`/`detail`/`effect`)이 다르다. 상세 계약이 확정되면 MSW 내부 매핑을 제거해야 한다.

## 목록에 등록할 재사용 가능 자산

- `src/shared/api/unwrap-axios-response.ts`: 201 Location을 SUCCESS `data.location`으로 옮겨 `toApiResult`가 성공으로 읽게 한다. 테스트 Axios 인스턴스도 같은 함수를 쓴다.

## 기술 부채

- `CitizenAuxiliaryRoutes.tsx`는 `ui/**`인데 기능 연결 한 줄이 Hephaestus 범위에 들어 있다. 소유권을 문서화하지 않으면 다음 세션에서 같은 충돌이 난다.
- 작성 폼 UI 필드명(`detail`/`effect`/`reference`)과 API 필드명이 다르다. 매퍼가 유일한 번역 지점이다.

## 프로세스 개선 사항

생성 POST처럼 성공 본문 예시가 없고 헤더만 확정된 경우, JSON `{ id }`를 추측하지 않고 Location을 파싱하는 쪽이 사용자 계약과 맞았다.

## 권고 사항

proposal 상세 GET이 확정되면 생성 저장 필드와 상세 응답 필드를 같은 이름으로 맞춘다. 작성 라우트 컨테이너의 소유권을 Claude Code `UI_COMPLETE` 또는 Hephaestus 소유로 명시한다.
