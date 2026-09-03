# 계획

## 목표

- 중앙 정책에서 `Hephaestus` 고유 명칭을 제거하고 Codex 또는 OpenCode가 담당하는 `Logic Session` 계약으로 일반화한다.
- Claude의 기본 구현 세션은 UI 소유권을 유지하되 Planner와 Evaluator 서브 에이전트가 코드베이스 전체를 읽고 구현 계획·장기 평가를 수행할 수 있도록 역할 경계를 확장한다.
- Codex, Claude Code, OpenCode에서 Git 명령과 빌드·개발 서버 명령을 실행하기 전에 사용자가 명령 단위로 판단하도록 중앙 지시문과 실행 게이트를 제공한다.

## 범위

- `/Users/okand/SynologyDrive/asan-agent-policy`의 공통 지침, Claude 역할 계약, 세 호스트 adapter, 공통 guard, 렌더러, 테스트와 README
- 중앙 프로젝트의 렌더 결과와 감사 결과 확인
- 현재 작업의 필수 세션 산출물 작성

## 제외 사항

- `user-ui`, `admin-ui`로 `sync` 또는 legacy 퇴역 실행
- `start` 명령에 별도 `--role` 인자 추가
- production UI·애플리케이션 코드 변경
- UI/로직 파일 소유권의 기계적 경로 차단

## 제약 조건

- 중앙 원본만 수정하며 소비 프로젝트의 동시 변경을 보존한다.
- Claude Planner/Evaluator의 전역 읽기 권한은 구현 파일 쓰기 권한으로 확장하지 않는다.
- 명령 승인 범위는 Git 명령 전체와 build/dev/start/preview 계열 명령이다. lint/test는 이번 게이트 범위가 아니다.
- Codex는 현재 `PreToolUse`의 `ask`를 지원하지 않으므로 동일 명령 해시를 한 번만 허용하는 명시적 승인 왕복을 사용한다.
- Claude와 OpenCode는 각 호스트의 네이티브 승인 UI를 사용한다.

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 정책·호스트 조사 | Planner | `policy-harness`, `policy-documentation`, `openai-docs` | 공식 훅 계약과 로컬 버전 근거 |
| 역할 경계 설계 | Planner | `policy-abstraction-strategy` | 구현 소유권과 분석 역할이 분리된 계약 |
| 중앙 원본 구현 | Generator | `policy-harness`, `policy-documentation` | 공통 guard와 세 adapter 변경 |
| 검토 | Watcher | `policy-review-checklist` | 테스트·렌더·감사 근거 기반 PASS/FAIL |
| 장기 평가·정리 | Evaluator | `policy-portfolio` | 제한 사항과 포트폴리오 근거 |

## 검증

- `python3 -m unittest discover -s tests -v`
- `bin/agent-policy audit`
- `bin/agent-policy diff --project all`
- 렌더 임시 프로젝트에서 Codex/Claude/OpenCode 승인 계약 확인
- 설치된 OpenCode 1.18.19의 local plugin/config load smoke 확인

## 위험 요소 및 결정 사항

- OpenCode V1과 V2의 권한 스키마가 다르므로 현재 설치본 1.18.19용 V1 `permission.bash`를 생성하고 업그레이드 주의사항을 문서화한다.
- Codex 승인 상태는 세션 ID와 저장소 경로로 격리하고, 거부된 명령과 완전히 같은 명령만 1회 허용한다.
- 세션 네 개가 동시에 실행되어도 승인 상태와 호스트 네이티브 권한이 각 세션에 격리되도록 한다.

## 승인

- 상태: approved
- 근거: 사용자가 `1번 내용 타당하니 수정해`와 `이렇게 다음 작업 진행`으로 중앙 수정 및 후속 연구·구현을 명시적으로 승인했다.
