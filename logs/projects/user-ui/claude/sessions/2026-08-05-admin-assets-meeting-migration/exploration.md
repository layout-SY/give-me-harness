# 탐색

## 요청

`asan-metaverse-admin-ui`의 현재 하네스 전체, 재사용 컴포넌트, 회의 관련 코드를 `asan-metaverse-user-ui`로 안전하게 이전한다.

## 대상 정보

- 실제 대상: `/Users/okand/SynologyDrive/asan-metaverse-user-ui`
- 초기 상태: 기존 Git 저장소의 깨끗한 Vite 시작 프로젝트이며 AGENTS/하네스/공유/회의 코드가 없음. 현재 Git 메타데이터를 유지하고 새로 초기화하지 않음
- 이전 전 기준선 린트와 TypeScript 검사를 통과함

## 불러온 스킬

- policy-harness, policy-documentation, policy-index
- reference-components, reference-custom-hooks
- programming TypeScript 규칙
- frontend, playwright, visual-qa
- policy-ui-library, policy-styles, policy-publishing

## `src/shared/ui/`의 재사용 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| 전체 공유 UI 목록 | 이전 | 탐색 당시 23개였으며 최종적으로 `date-range-picker`를 포함한 대상 디렉터리 24개를 `COMMON_COMPONENTS.md`에 등록함 |
| 공유 API/lib/config/assets | 이전 | UI와 훅에 필요한 전이 의존성 폐쇄임 |
| 관리자 엔티티/위젯/페이지 | 제외 | 공유 또는 회의 대상 영역에서 가져오지 않음 |
| 회의 훅/UI/API/모델 | 기능 내부로 이전 | 자체 완결된 `src/features/meeting` 폐쇄임 |

## 제약 사항과 미확인 항목

- 소스 작업 트리에 진행 중인 회의/FSD 및 공유 UI 변경이 있었으며, 사용자는 현재 작업 트리 내용을 요청했다.
- 선택한 폐쇄 밖의 소스 린트/타입 오류는 이전하지 않았다.
- 실제 참여/게시/구독에는 유효한 서버 및 Agora 자격 증명이 필요하다.

## 결론

저장소 전체 복사 대신 대상 맞춤형 이전을 적용한다. 현재 공유 및 회의 동작을 유지하고 대상의 이식성·품질·접근성 결함만 수정하며, 무관한 소스 이력과 도메인은 제외한다.
