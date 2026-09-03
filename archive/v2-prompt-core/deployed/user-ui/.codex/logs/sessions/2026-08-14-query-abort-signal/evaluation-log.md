# 평가 로그

## 현재 판정과의 경계

Watcher PASS를 재평가하지 않는다.

## 장기 관찰 사항

- RQ mutation context에 signal이 생기면 mutation도 동일 헬퍼로 연결
- 전역 axios timeout과 병행하면 hang UX를 더 줄일 수 있음

## 목록에 등록할 재사용 가능 자산

- `src/shared/api/withAbortSignal.ts`

## 권고 사항

새 query/API 추가 시 `queryFn({ signal })` → `withAbortSignal(signal, config)` 패턴을 기본으로 둔다.
