# 구현 로그

## 승인된 범위

`CitizenParticipationDetailRoutes.tsx`의 barrel import를 깊은 경로로 바꿔 `useVoteDetailQuery` 결과 할당 오류를 제거한다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `src/pages/citizen-participation/ui/CitizenParticipationDetailRoutes.tsx` | `~/features/citizen-participation` barrel 대신 훅·페이지 깊은 import | `useVoteDetailQuery`와 `persistedChoice`가 오류 유형이 아님 |

## 결정 사항

- `voteMutation.data.choice` 분기는 그대로 두고 import만 고쳤다. 동작 변경이 아니다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| ReadLints 대상 파일 | 오류 없음 |
| `npx eslint src/pages/citizen-participation/ui/CitizenParticipationDetailRoutes.tsx` | exit 0 |
| `npx vitest run` CitizenCommentRoutes·CitizenResultRoutes | 2 files / 10 tests passed |

## Watcher 인계

타입/import 경계 수정이다. UI 시각 QA는 하지 않았다.
