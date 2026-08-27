# 최종 요약

제안 생성의 `toCreatedProposalResult`와 투표의 `toVoteResponseResult`를 제거하고, 공용 `mapApiResult`가 실패 `ApiResult`는 통과시키고 성공 data만 변환하게 했다. 성공 envelope는 기존 `toApiResult`가 만든다. Location→id와 vote schema parse는 각 도메인 API에 남는다.

## 제공 사항

- `mapApiResult`
- 제안·투표 POST가 공용 매퍼 사용

## 제외 사항

- 훅 `unwrapApiResult` 변경
- 토론·댓글 like mutation 파싱 위치

## 검증

| 명령어 | 결과 |
| --- | --- |
| eslint 변경 파일 | 성공 |
| `tsc -b` | 성공 |
| vitest API+pages | 33 passed |
| vitest handlers (`all`) | 18 passed |

## 산출물

`.codex/logs/sessions/2026-08-26-map-api-result/` 8종

## 남은 제한 사항

저장소에 동일 역할의 기존 함수 이름은 없었다. `toApiResult`를 재사용하는 `mapApiResult`를 추가했다.

## 다음 단계

없음
