# 최종 요약

## 제공 사항

제안하기 POST가 `title`/`background`/`content`/`expectedEffect`/`referenceCase`를 보내고, 성공 시 201 `Location: /citizen/proposals/{id}`에서 숫자 id를 읽어 상세로 이동한다. 빈 참고 사례는 `null`로 저장된다.

## 제외 사항

- `ProposalWritePage` 마크업
- proposal 상세 GET DTO 재설계
- 201 JSON body 발명
- 다른 mutation의 `MutationResponseDto` 일괄 변경

## 검증

| 명령어 | 결과 |
| --- | --- |
| `npx vitest run src/features/citizen-participation src/pages/citizen-participation` | 12 files / 71 tests passed |
| `npm run lint` | exit 0 |
| `npm run build` | `tsc -b && vite build` 성공 |

## 산출물

`.codex/logs/sessions/2026-08-25-proposal-create-api-contract/`

## 남은 제한 사항

생성 후 상세 조회는 여전히 `ContentDetailDto`의 `body`/`detail`/`effect`/`reference`를 쓴다. 앱 상세 URL은 `/citizen-participation/proposals/:id`이고 Location 값은 `/citizen/proposals/{id}`다.

## 다음 단계

proposal 상세 GET 계약이 오면 생성 저장 필드와 상세 응답을 맞춘다.
