# 최종 요약

## 제공 사항

- 제안 목록 「내 활동 보기」가 `/me/activity?content=proposal&page=&size=`를 호출한다.
- 응답을 확정 목록 DTO로 파싱해 같은 제안 카드에 제목/상태/작성자/날짜를 표시한다.
- 내 활동 화면의 제안 필터도 같은 본문을 깨지 않게 매핑한다.

## 제외 사항

- 다른 콘텐츠 타입 토글 응답
- 목록 카드 요약 UI 변경

## 검증

| 명령어 | 결과 |
| --- | --- |
| `npx vitest run src/pages/citizen-participation src/features/citizen-participation` | 56 passed |
| `npm run build` | 성공 |
| `npm run lint` | 성공 |

## 산출물

`.codex/logs/sessions/2026-08-25-proposal-my-activity-display/`

## 남은 제한 사항

activity 응답 스펙이 아직 없어 확정 목록 `data` 형태를 재사용한다.

## 다음 단계

activity 응답이 확정되면 parser를 그 계약으로 교체한다.
