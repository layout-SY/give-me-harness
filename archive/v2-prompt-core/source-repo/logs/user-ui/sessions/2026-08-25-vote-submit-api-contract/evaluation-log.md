# 평가 로그

## 현재 판정과의 경계

여기서는 Watcher 판정을 다시 평가하지 않는다.

## 장기 관찰 사항

- 투표 POST 200 `data`가 상세의 숫자 `id`와 같아지면 `VoteResponseDto.id`를 맞춰야 한다.
- `VoteDetailPage`에 오류 문구 props가 생기면 409 코드를 사용자 메시지로 매핑할 수 있다.
- `ApiError.code`가 `number \| string`인 상태는 숫자 코드 API와 문자열 코드 API가 공존하는 동안의 계약이다.

## 목록에 등록할 재사용 가능 자산

없음. 새 공용 UI를 추가하지 않았다.

## 기술 부채

- 클라이언트는 종료·시작 전·중단에서 POST를 보내지 않아, 화면에서 409를 보기 어렵다. 직접 API 호출·레이스에서만 코드가 드러난다.

## 프로세스 개선 사항

POST 스펙에 200 예시를 같이 주면 submit 응답을 두 번 설계하지 않아도 된다.

## 권고 사항

409 안내 UI가 필요하면 Claude Code가 `VoteDetail`에 notice props를 두고, Hephaestus가 코드→문구 매퍼만 연결한다.
