# 구현 로그

## 승인된 범위

프로젝트 및 AI 하네스 변경 작업의 필수 포트폴리오 산출물 정책과 자동 검증을 추가한다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `AGENTS.md` | 필수 8종 산출물과 경력 추합 단계 추가 | 모든 보호 대상 변경에 portfolio 기록 요구 |
| `.agents/skills/policy/{portfolio,documentation}/SKILL.md` | 근거 출처와 사례 구조 명문화 | 사용자 대화·테스트·설계 위험·AI 하네스 포함 |
| `.codex/templates/portfolio-log*.md` | schema와 작성 template 추가 | 문제→고민·선택→적용→기술 목적→결과 형식 제공 |
| `.codex/hooks/require-documentation-stop.py` | 필수 파일·사례 메타데이터·하위 제목 검사 | 누락·불완전 사례 완료 차단 |
| `.codex/hooks/hook_common.py` | `.claude/**`, `CLAUDE.md` 보호 | Claude 하네스 변경도 문서 gate 적용 |
| `.codex/hooks/test_governance_hooks.py` | RED/GREEN 회귀 테스트 추가 | 필수 artifact와 AI 경로 보호 검증 |
| `.codex/hooks.json` | 4개 hook 결합 hash 갱신 | bootstrap 무결성 유지 |
| `.gitignore` | governance 파일 제외 제거 | 정책·hook 변경이 저장소 전달 대상이 됨 |

## 결정 사항

- 각 `## 사례`는 메타데이터 3개와 필수 하위 제목 6개를 모두 가져야 한다.
- 사용자 후속 피드백이 없으면 `없음`으로 기록하고 추정하지 않는다.
- AI 하네스도 서비스 구현과 동일한 사례 구조를 사용한다.
- 기존 문서 7종을 대체하지 않고 `portfolio-log.md`를 여덟 번째 산출물로 추가한다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| portfolio 필수 artifact targeted test | RED: required tuple에 파일 없음 |
| AI 하네스 보호 targeted test | RED: `.claude/**`, `CLAUDE.md`가 false |
| targeted 3 tests | PASS |
| `python3 -I .codex/hooks/test_governance_hooks.py` | PASS, 22 tests |
| `python3 -m py_compile ...` | PASS |

## Watcher 인계

- 애플리케이션 코드는 변경하지 않았다.
- Python LSP는 설치되지 않아 compile과 governance suite로 검증했다.
