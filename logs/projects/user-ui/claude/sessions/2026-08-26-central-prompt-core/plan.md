# 계획

## 목표

user-ui의 시스템 프롬프트를 단일 기준으로 삼는 중앙 프롬프트 프로젝트 `asan-prompt-core`를 신설하고, user-ui와 admin-ui가 동일한 프롬프트를 사용하도록 배포 및 편집 차단 체계를 구축한다.

## 범위

| 단계 | 내용 |
| --- | --- |
| P0 | user-ui 프롬프트 교정 (D1~D8) |
| P1 | `asan-prompt-core` 생성 및 `source/` 이관 |
| P2 | `bin/sync.py` 구현 (deploy / check / status) |
| P3 | 편집 차단 및 문서 강제 훅 3호스트 구현 |
| P4 | admin-ui 첫 배포 |

## 제외 사항

- 프로젝트 고유 오버레이(Agora RTC, TanStack Query). 이후 기능으로 추가한다.
- `.agents/skills/**` 얇은 스킬 본문 보강. 외부 프롬프트 참고 후 별도 작업한다.
- `asan-harness` 코드 재사용. 설계 아이디어만 차용한다.
- 애플리케이션 소스 변경.

## 제약 조건

- 사용자가 이번 작업에 한해 하네스 경로 소유권을 Claude Code에 이전했다.
- admin-ui의 기존 프롬프트는 배포 시 교체되므로 사전 백업이 필요하다.
- 편집 차단은 사용자가 중앙에서 수정 후 세션을 재시작하는 흐름을 전제한다. 자동 반영을 수행하지 않는다.

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| P0 프롬프트 교정 | Refactorer | `policy/harness`, `policy/documentation` | 내부 모순이 제거된 `AGENTS.md`, `CLAUDE.md` |
| P1 중앙 이관 | Generator | `policy/harness` | `asan-prompt-core/source/` |
| P2 동기화 도구 | Generator | `policy/codex-native-quality` | `bin/sync.py` |
| P3 훅 | Generator | `policy/harness`, `policy/hook-extraction` | 호스트별 훅 3종 |
| P4 배포 | Generator | `policy/harness` | admin-ui 동기화 |
| 검증 | Watcher | `policy/review-checklist` | `review-log.md` PASS/FAIL |

## 사용자 확정 결정 사항

| 항목 | 결정 |
| --- | --- |
| D1 강제력 비대칭 | 기존 codex 훅 폐기. codex/opencode는 8종 문서 강제, claude는 UI handoff 문서만 강제 |
| D2 산출물 규칙 | 8종으로 통일. `hookify` 부분집합 폐기 |
| D3 로그 경로 | `AGENTS.md` 기준인 `.codex/logs/sessions/` 정본 |
| D4 명령어 | `test`, `preview` 추가 |
| D5 에이전트 | 6종 유지, 리뷰 에이전트 실행 금지 조항도 유지 |
| D6 한국어 조항 | admin-ui에서 역수입 |
| D7 스킬 본문 | 이번 범위 제외 |

## 검증

- `npm run lint`
- `npm run build`
- `python3 bin/sync.py check --target all` 이 배포 직후 exit 0
- 훅 단위 테스트: managed path 편집 시도 거부, 문서 누락 시 차단
- admin-ui 배포 전후 `AGENTS.md` 해시가 user-ui와 일치

## 위험 요소 및 결정 사항

| 위험 | 대응 |
| --- | --- |
| admin-ui 고유 프롬프트 소실 | 배포 전 전량 백업, 고유 자산은 별도 보관 후 P5에서 오버레이로 복원 |
| 기존 codex 훅 제거로 강제력 공백 | 신규 훅 배포와 동일 단계에서 교체 |
| 중앙-프로젝트 양쪽 편집으로 인한 재드리프트 | 배너 주입과 PreToolUse 차단으로 프로젝트 측 편집을 봉쇄 |

## 승인

- 상태: approved
- 승인 근거: 사용자가 기획 검토 후 소유권 이전과 함께 작업 진행을 지시함
