# 구현 로그

## 작업 요약
- 사용자 활동 상세를 vote 상세와 같은 page/controller/view 구조로 분해했다.
- 페이지는 fixture를 직접 읽지 않고 `useCpUserActivityDetailQuery`로 조회한다. 읽기 전용이라 process/mutation은 두지 않았다.

## 재사용 자산
- vote 상세의 조회 실패 Dialog, Loading, 빈 화면 `다시 조회`
- `PageHeader`, `KpiStrip`, `ActionBar`, `SectionCard`, `DefinitionList`, `Table`, `StatusBadge`, `TimelineList`, `Loading`, `useDialog`

## 신규 파일 / 수정 파일
- entity: `cp-activity-log.api.ts` ApiClient 전환, dto/parser/query-keys/`useCpUserActivityDetailQuery`, barrel 갱신
- mocks: `cp-activity-log.handlers.ts`, `handlers.ts` 등록
- page: config/types/controller/view, `cp-user-activity-detail-page.tsx` 결선만 유지

## 핵심 로직
- GET `/v1/cp/activity-logs/users/:userId` → unwrap ApiResult → zod parser
- 없는 사용자는 404. surface에서 Dialog + 다시 조회
- KPI/최근활동 컬럼은 순수 config

## 검증 / 요청 처리
- `yarn tsc --noEmit` 통과
- 변경 경로 eslint 통과
- 브라우저: U-0091 상세 조회, 목록 복귀, 목록에서 상세 보기, U-0092 이름 매핑, U-9999 조회 실패 UI

## 리스크
- 목록 페이지는 여전히 fixture 직접 import. 후속 작업
- 활동 로그 목록 API/MSW는 아직 없음

## 핸드오프 메모
- Watcher 미실행. 상태: `paused_after_generator`
