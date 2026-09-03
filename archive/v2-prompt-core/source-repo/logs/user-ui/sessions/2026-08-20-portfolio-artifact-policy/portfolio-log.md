# 이력서·포트폴리오 기록

## 사례 1 — 경력 추합 산출물의 필수화

- 작업 유형: AI 하네스
- 관련 도메인/서비스: 프로젝트 거버넌스와 작업 문서화
- 문제 출처: 사용자 요구

### 문제 상황

사용자는 작업 완료 후 구현 내용만 나열하지 않고, 사용자 요구·기획 변경·테스트 실패·잠재 구조 위험·상호 제안과 선택·적용 전후 결과를 이력서와 포트폴리오에 재사용할 수 있도록 추합하라고 요청했다. 기존 `policy-portfolio`는 이 기록을 선택 사항으로 두고, 기존 필수 7종 문서와 Stop hook에도 포트폴리오 artifact가 없었다. 이 상태에서는 기술을 도입한 구체적 목적과 문제 해결 과정이 작업 종료 후 유실될 수 있었다.

### 고민과 선택

- 사용자 제안: 서비스 구현과 AI 하네스 변경 모두를 문제 상황 → 고민 → 적용 → 결과 구조로 기록하고, 대화에서 확인된 사용자·에이전트 제안과 선택을 포함한다.
- 에이전트 제안: 지침 문구만 추가하지 않고 정책, template, workflow, Stop hook, 회귀 테스트를 함께 변경하는 3층 강제를 적용한다.
- 검토한 대안: `final-summary.md` 확장, 선택적 portfolio 문서 유지, 별도 데이터베이스 저장.
- 최종 선택: 기존 7종과 책임을 분리한 `portfolio-log.md`를 여덟 번째 필수 artifact로 추가한다.
- 선택 이유와 제외한 방식의 이유: final summary는 인계 요약이어서 대화·대안·경력 문구를 모두 담기 과도하고, 선택 규칙만으로는 누락을 막을 수 없다. 별도 저장소는 현재 Markdown 기반 harness보다 복잡하다.

### 적용

- `AGENTS.md`에 경력 추합 단계를 추가하고 변경 작업의 필수 artifact를 8종으로 확장했다.
- `policy-portfolio`에 근거 출처, 추정 금지, 사례별 필수 구조를 정의했다.
- `portfolio-log.md` schema와 `.template.md`를 추가했다.
- feature/refactor/hybrid workflow의 완료 단계에 portfolio 기록을 포함했다.
- Stop hook이 파일 존재와 각 사례의 메타데이터·필수 하위 제목을 검사하도록 구현했다.

### 사용 기술과 구체적 목적

| 기술·구조·패턴 | 해결하려는 구체적 문제 | 적용 위치와 방식 |
| --- | --- | --- |
| Markdown schema/template | 작업자마다 다른 서술 구조와 필수 정보 누락 | `.codex/templates/portfolio-log*.md` |
| Python Stop hook | 선택적 지침만으로 생기는 artifact 누락 | `REQUIRED_ARTIFACTS`와 `portfolio_issues` |
| 정규식 구조 parser | 사례 메타데이터와 단계별 제목의 기계 검증 | 각 `## 사례` 구간을 독립 검사 |
| TDD | 기존 7종 계약을 깨뜨리거나 검사 누락 가능성 | required artifact와 incomplete case RED/GREEN 테스트 |
| 결합 SHA-256 | hook 또는 common source의 비인가 변경 실행 위험 | `.codex/hooks.json` 4개 entry hash 갱신 |

### 결과

- 적용 전: 포트폴리오 기록은 선택 사항이고 완료 gate가 검사하지 않았다.
- 적용 후: 모든 보호 대상 변경은 8종 문서를 요구하며, portfolio 사례 구조가 불완전하면 Stop이 차단한다.
- 검증 결과: 신규 targeted tests와 governance 전체 22개 테스트, Python compile 통과.
- 사용자 후속 피드백: 없음.
- 추가 요청 및 남은 제한: 자연어 사실성은 자동 판별하지 않으며 현재 대화·실행·코드 근거를 작성자가 확인해야 한다.

```mermaid
flowchart LR
  Before[선택적 경력 기록] --> Policy[필수 정책과 템플릿]
  Policy --> Hook[Stop hook 구조 검사]
  Hook --> After[검증된 8종 산출물]
```

### 이력서·포트폴리오 문구

- 이력서 bullet: 프로젝트·AI 하네스 변경의 문제 해결 근거를 자동 보존하도록 Markdown 사례 schema와 Python Stop hook을 설계하고, governance 22개 회귀 테스트로 완료 gate를 검증했다.
- 포트폴리오 서술: 선택적 포트폴리오 기록으로 인해 구현 이유와 사용자 피드백이 유실될 수 있는 문제를 확인했다. 기존 final summary 확장과 별도 저장 방식을 비교한 뒤, 현재 Markdown harness와 일치하는 필수 `portfolio-log.md`를 선택했다. 정책·템플릿·workflow·Stop hook을 함께 적용해 문제 상황부터 기술 목적과 검증 결과까지 구조적으로 남기도록 바꿨고, 전체 governance 테스트 통과로 기존 gate와의 호환성을 확인했다.

## 사례 2 — AI 거버넌스 파일의 저장소 전달성 복구

- 작업 유형: AI 하네스
- 관련 도메인/서비스: Git 전달성과 hook governance
- 문제 출처: 테스트·런타임 실패

### 문제 상황

전체 governance 테스트에서 `DeliveryTests.test_governance_is_tracked_portable_and_aggregated`가 실패했다. 현재 `.gitignore`가 `AGENTS.md`, `.agents/`, `.codex/`, `.harness/`, `CLAUDE.md`, `.claude/*`를 제외해 새 정책과 hook 변경이 저장소에 전달되지 않을 수 있었다. 포트폴리오 자동 강제를 구현해도 관련 파일이 추적되지 않으면 다른 환경에서 규칙이 사라지는 구조적 결함이었다.

### 고민과 선택

- 사용자 제안: AI 하네스의 추가·수정·삭제도 서비스 구현과 동일하게 기록한다.
- 에이전트 제안: AI 하네스 경로를 Stop hook 보호 대상에 포함하고, governance 파일을 `.gitignore`에서 제거한다.
- 검토한 대안: 테스트 실패를 기존 문제로 남김, hook 파일만 예외 처리, 모든 `.claude` 로컬 파일 추적.
- 최종 선택: 공유 governance 파일은 추적하고 `.claude/settings.local.json`, `.claude/logs/` 같은 로컬 파일만 계속 제외한다.
- 선택 이유와 제외한 방식의 이유: 테스트를 무시하면 정책 전달성을 보장할 수 없고, 로컬 설정·로그까지 추적하면 개인 환경과 로그가 저장소에 섞인다.

### 적용

- `.gitignore`에서 공유 governance 경로 제외 규칙을 제거했다.
- `is_protected_path`에 `.claude/**`와 `CLAUDE.md`를 추가했다.
- 보호 경로와 저장소 전달 계약을 회귀 테스트에 추가했다.

### 사용 기술과 구체적 목적

| 기술·구조·패턴 | 해결하려는 구체적 문제 | 적용 위치와 방식 |
| --- | --- | --- |
| Git ignore allowlist 정리 | 공유 정책이 로컬 전용으로 남는 문제 | governance ignore 제거, local settings/log ignore 유지 |
| 보호 경로 predicate | Claude 하네스 변경이 문서 gate를 우회하는 문제 | `hook_common.is_protected_path` 확장 |
| 회귀 테스트 | 향후 ignore 규칙 재도입과 보호 경로 누락 | Delivery/CommonAndStop tests |

### 결과

- 적용 전: governance suite 1건 실패, Claude 하네스 경로는 보호 대상 아님.
- 적용 후: 공유 AI 거버넌스 파일이 전달 대상이 되고 Claude 하네스 변경도 8종 artifact gate를 적용받는다.
- 검증 결과: governance 전체 22개 테스트 통과.
- 사용자 후속 피드백: 없음.
- 추가 요청 및 남은 제한: 기존 untracked governance 파일의 실제 commit 여부는 사용자의 Git 작업에서 결정한다.

### 이력서·포트폴리오 문구

- 이력서 bullet: AI 거버넌스 파일을 제외하던 Git ignore 충돌을 회귀 테스트로 발견하고, 공유 정책과 로컬 Claude 설정의 추적 경계를 재설계해 hook 규칙의 환경 간 전달성을 복구했다.
- 포트폴리오 서술: Stop hook 확장 후 전체 suite에서 governance 파일이 `.gitignore`에 의해 제외되는 실패를 확인했다. 모든 Claude 파일을 추적하는 방식 대신 공유 정책과 로컬 설정·로그를 구분했다. 공유 파일 ignore를 제거하고 `.claude/**` 보호 predicate를 추가한 결과 22개 governance 테스트가 통과했으며, AI 하네스 변경도 서비스 코드와 같은 문서 gate를 거치게 됐다.
