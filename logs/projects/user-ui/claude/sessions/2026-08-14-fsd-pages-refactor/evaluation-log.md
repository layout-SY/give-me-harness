# 평가 로그

## 현재 판정과의 경계

여기서는 Watcher 판정을 다시 평가하지 않는다. 아래 항목은 후속 구조 개선 후보이며 이번 완료 조건이 아니다.

## 장기 관찰 사항

- `app → pages → features → shared` 방향을 새 pages slice의 기준 패턴으로 사용할 수 있다.
- auth와 meeting의 page-like UI는 각 도메인의 상태·자격 증명 경계가 달라 별도 계획으로 다뤄야 한다.
- `presentation.ts`는 243 LOC로 경고 구간이며 mapper 추가 시 분리 신호로 삼는다.

## 목록에 등록할 재사용 가능 자산

- 이번 작업은 production UI 자산을 새로 만들지 않았으므로 `.codex/memory/reusable-assets.md` 등록 대상이 없다.
- `src/features/citizen-participation/testing.ts`는 앱 MSW 조합용 공개 경계지만 UI/공용 hook 자산은 아니다.

## 기술 부채

- Vite production bundle이 500 kB 경고 기준을 초과한다.
- routing test는 route component 전부를 렌더하지 않으며 build와 focused tests가 보완한다.
- TypeScript LSP가 설치되지 않아 파일별 LSP diagnostics를 실행하지 못했다.

## 프로세스 개선 사항

- 구조 리팩터링 탐색 시 route 경로뿐 아니라 mock/bootstrap 경계도 초기 레이어 검사에 포함한다.
- 전체 `npm test`가 Vitest 실패로 Python governance 검사를 건너뛰므로 실패 시 governance 명령을 별도로 실행한다.

## 권고 사항

- auth/meeting page 경계는 현재 변경과 분리된 승인 계획으로 진행한다.
- bundle code splitting은 성능 수치와 실제 route loading 요구를 수집한 뒤 별도 최적화한다.
- 전체 suite의 3개 실패와 governance 1개 실패는 각 소유 범위에서 수정한다.
