---
name: reference-custom-hooks
description: 재사용 가능한 대상 훅을 탐색하고 분리 전에 공용 또는 기능 소유권을 결정합니다.
---

<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/common/skills/reference/custom-hooks/SKILL.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 커스텀 훅 참고 자료

훅을 생성하기 전에 대상 프로젝트의 기존 훅을 조사합니다. 상태/효과 소유권, 입출력 계약, 취소 동작과 사용처를 기록합니다.

| 자산 | 경로 | 계약 |
| --- | --- | --- |
| `useApi` | `src/shared/lib/hooks/use-api.tsx` | `ApiResult` 또는 Promise API를 실행하고 로딩 상태를 노출하며 오래된 결과를 무시합니다. 요청한 경우 사용자에게 표시할 오류 처리를 Dialog에 위임합니다. |
| `useFetchAdapter` | `src/shared/ui/table/hooks/useFetchAdapter.ts` | `debounce`/`throttle`을 지원하며 페이지네이션 API 결과를 공용 Table 계약에 연결합니다. |
| 타입이 지정된 게시/구독 | `src/shared/lib/pub-sub/` | 분리된 오버레이 실행을 위한 타입 기반 게시/구독 구조이며 정리 과정에서 항상 구독을 해제합니다. |

`src/features/meeting/hook/` 아래의 미팅 RTC 훅은 기능 내부 생명주기를 소유하며 공용 훅이 아닙니다.
