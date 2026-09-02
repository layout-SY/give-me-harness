# 계획

## 목표

소스 프로젝트의 운영 하네스, 재사용 가능한 전체 공유 계층, Agora 회의 기능을 소스 이력이나 무관한 관리자 도메인 없이 `asan-metaverse-user-ui`로 안전하게 이전한다.

## 범위

- 대상에 맞춘 AGENTS, 스킬, 역할, 작업 흐름, 훅, 템플릿, 메모리 구조
- 전체 `src/shared` 의존성 폐쇄와 패키지/빌드 구성
- 전체 `src/features/meeting` 기능과 대상 애플리케이션 연결
- 디자인 계약, 품질 보완, 브라우저/시각 품질 검증, 문서화

## 제외 항목

- 소스의 `.claude`, `.omo` 런타임 상태, 과거 로그, 관리자 엔티티/위젯/페이지
- 소스의 `.env` 값과 Git 이력
- 프로덕션 RTC 자격 증명

## 제약 사항

- 대상의 React 19, Vite 8, React Compiler, npm 잠금 파일과 소스 RTC 생명 주기를 유지한다.
- Git을 초기화하거나 비밀값을 노출하지 않는다.
- HeroUI는 `src/shared/ui` 어댑터 뒤에 둔다.

## 스킬과 역할

| 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 탐색 | Planner | policy-harness, reference-index | 의존성이 완결된 이전 경계 |
| 운영 지침 | Generator | policy-documentation, customize-opencode | 실행 가능한 대상 하네스 |
| UI 계약 | Publisher | frontend, policy-ui-library, policy-styles | `DESIGN.md`와 유지된 시각적 의도 |
| 공유/회의 | Generator | `programming`, `policy-coding-convention` | 검증을 통과하는 대상 코드 |
| 검증 | Watcher | visual-qa, policy-review-checklist | 근거 기반 판정 |

## 검증

- `npm run lint`
- `tsc -b --noEmit`
- `npm run build`
- `npm audit --json`
- 1280, 768, 375 너비에서 검증, 포커스, sticky, 메타데이터 스트레스 상태를 Playwright로 확인

## 위험과 결정

- 존재하지 않는 요청 대상 경로 `~/Synology`를 실제 경로 `~/SynologyDrive`로 바로잡았다.
- 과거 운영 지침 로그와 로컬 런타임 상태는 대상에 안전하지 않은 상태이므로 제외했다.
- 실제 RTC는 자격 증명에 의존하므로 QA용으로 임의 생성할 수 없다.

## 승인

- 상태: approved
- 사용자 승인: `진행`
