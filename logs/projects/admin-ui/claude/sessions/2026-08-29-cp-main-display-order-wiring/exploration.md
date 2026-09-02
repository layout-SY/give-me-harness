# 탐색

## 요청

CP 메인 노출 항목의 순서 이동 기능을 기존 상태·저장 흐름에 연결하고 실제 저장 결과까지 검증한다.

## 대상 관련 사실

- `src/pages/cp-main-display/lib/cp-main-display.model.ts`가 항목 비교와 화면 상태 계산을 담당한다.
- `use-cp-main-display-process.tsx`가 조회 결과와 편집 draft, 저장 후 동기화를 조율한다.
- `use-cp-main-display-controller.tsx`가 process 결과를 화면 props로 전달한다.
- `cp-main-display.handlers.ts`가 브라우저 QA에서 사용되는 저장 응답을 제공한다.
- 기존 화면은 섹션별 항목 배열을 렌더링하지만 항목 순서를 변경하는 동작 계약은 연결되지 않았다.

## 불러온 스킬

- `policy-git-branch-strategy`
- `policy-coding-convention`
- `policy-type-definition`
- `policy-documentation`
- `policy-portfolio`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| 공용 Button | 미사용 | 기존 화면의 항목 액션 버튼 구조를 유지하는 편이 변경 범위가 작다. |
| 공용 Table | 미사용 | 현재 화면은 테이블 데이터 흐름이 아니라 섹션별 편집 목록이다. |
| 신규 순서 제어 컴포넌트 | 도입하지 않음 | 확인된 사용처가 CP 메인 노출 단일 화면이어서 공용 추상화 근거가 부족하다. |

## 제약 조건 및 미확인 사항

- 저장 API의 실제 백엔드 배포 환경은 이번 작업에서 호출하지 않았고 MSW 계약으로 검증했다.
- `lsp_diagnostics`는 linked worktree가 요청 cwd 밖으로 판정되어 실행되지 않았으며 TypeScript build와 변경 파일 ESLint로 보완했다.
- 전체 lint는 변경 범위 밖 기존 오류 73건과 warning 5건이 있어 변경 파일만 별도로 검증했다.

## 결론

기존 모델·process·controller·view 흐름에 작은 계약을 추가하고 MSW 저장 검증을 강화하는 방식이 가장 직접적이며, 신규 공용 추상화 없이 요구 동작을 구현할 수 있다.
