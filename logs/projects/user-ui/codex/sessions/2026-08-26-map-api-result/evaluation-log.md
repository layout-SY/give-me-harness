# 평가 로그

## 현재 판정과의 경계

Watcher는 이번 리팩터링만 판정했다. 아래는 후속 후보이다.

## 장기 관찰 사항

- 훅의 `unwrapApiResult` + `schema.parse`와 API의 `mapApiResult`가 공존한다. mutation 파싱 위치를 API로 통일할지 나중에 정할 수 있다.
- `toApiResult`에 매퍼 오버로드를 넣으면 이름이 하나지만, unknown envelope와 `ApiResult` 매핑이 섞인다.

## 목록에 등록할 재사용 가능 자산

- `mapApiResult`: 성공 data만 변환하고 실패 `ApiResult`는 통과

## 기술 부채

없음. 동작은 유지했다.

## 프로세스 개선 사항

사용자가 “전역에 이미 있다”고 한 헬퍼가 없을 때, 가장 가까운 기존 함수(`toApiResult`) 위에 얇은 매퍼를 두는 선택을 기록으로 남긴다.

## 권고 사항

토론·댓글 like를 API 계층 `mapApiResult`로 옮길지는 타입 순환이 다시 생기는지 확인한 뒤 별도 작업으로 한다.
