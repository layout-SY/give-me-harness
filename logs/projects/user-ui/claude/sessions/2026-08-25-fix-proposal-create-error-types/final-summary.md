# 최종 요약

## 제공 사항

`proposal.api.ts`의 error 유형 할당을 제거했다. 생성 DTO를 별도 모듈로 두고, 남은 feature barrel 소비를 깊은 경로로 바꿨다.

## 제외 사항

- 투표 `parseVoteResponse` mutations 정리
- barrel 파일 삭제

## 검증

| 명령어 | 결과 |
| --- | --- |
| ReadLints `proposal.api.ts` | 오류 없음 |
| 변경 경로 eslint | 성공 |
| `npx vitest run` citizen-participation | 12 files / 71 tests passed |

## 산출물

`.codex/logs/sessions/2026-08-25-fix-proposal-create-error-types/`

## 남은 제한 사항

`index.ts`가 훅/parser를 계속 재export하면, 새 barrel import가 같은 오류를 다시 만든다.

## 다음 단계

시민참여 라우트·테스트는 barrel 대신 깊은 경로를 기본으로 둔다.
