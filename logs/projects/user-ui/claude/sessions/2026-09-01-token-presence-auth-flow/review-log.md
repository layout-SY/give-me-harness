# 검토 로그

## Watcher 판정

PASS

## 검토 범위

- token presence와 URL bootstrap
- 보호 route direct redirect와 안전한 `returnTo`
- 기존 전역 401 Dialog 종료 계약
- Vote·Discussion·Policy 댓글의 `/me` 의존 제거
- 테스트, 타입 안전성, production UI 소유권, 문서 근거

## 점검 항목

| 점검 | 결과 | 근거 |
| --- | --- | --- |
| 목표 충족 | PASS | localStorage·URL token, direct login, 401 Dialog, 로그인 복귀 모두 연결 |
| 승인·scope | PASS | branch metadata와 실제 변경 경로 일치 |
| 타입 안전성 | PASS | 신규 `any`, assertion suppressor 없음; build 통과 |
| 중복 로직 | PASS | 기존 external store·error queue·returnTo 재사용 |
| 요청 데이터 | PASS | query token key `access-token`, `refresh-token` 정확히 처리 |
| 렌더링 비용 | PASS | boolean `useSyncExternalStore` 구독, 별도 query 제거 |
| 접근성·공용 UI | PASS | 기존 Dialog 확인·Escape 경로 재사용 |
| 정적 검증 | PASS | test 469, governance 20, lint, build 통과 |
| 문서화 | PASS | UI_COMPLETE 및 수정·검증 근거 갱신 |

## 발견 사항

| 심각도 | 경로 | 발견 사항 | 필수 조치 |
| --- | --- | --- | --- |
| 해결됨 | `src/main.tsx` | bootstrap이 `startMocks()` 뒤라 URL credential 제거가 지연됨 | 동기 startup 최상단으로 이동 완료 |
| 해결됨 | `handoff.md` | UI 완료 후에도 대기 중으로 기록됨 | 사용자 UI 완료 확인과 최종 검증으로 갱신 완료 |
| 비차단 | `useAuthTokenPresence.ts` | 다른 탭 `storage` 이벤트는 즉시 반영하지 않음 | 실제 요구가 생길 때 별도 검토 |
| 기존 비차단 | build output | 500kB 초과 chunk 경고 | 이번 작업 범위 밖 |

## 결론

- 초기 FAIL 두 건을 수정한 뒤 동일 Watcher가 관련 7 files, 55 tests, lint, build를 확인하고 최종 PASS를 판정했다.
