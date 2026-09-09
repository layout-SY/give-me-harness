# 검토 로그

## Watcher 판정

PASS

## 검토 범위

- 중앙 공통 역할 계약과 Claude 하네스의 소유권·수명주기 일관성
- Codex/Claude/OpenCode 보호 명령 승인 경로
- 결정적 렌더링, managed file 보호, 미배포 상태

## 점검 항목

| 점검 | 결과 | 근거 |
| --- | --- | --- |
| 사용자 승인 범위 준수 | PASS | 중앙 원본과 dry-run만 변경, sync/legacy 퇴역 미실행 |
| 역할 명칭 일관성 | PASS | 중앙 실제 원본에서 `Hephaestus` 0건 |
| Planner/Evaluator 역할 분리 | PASS | 호출 단위·읽기 전용·중첩 위임 금지, 기본 세션 오케스트레이션 명시 |
| Logic/UI 파일 소유권 | PASS | 분석 권한이 쓰기 소유권을 확장하지 않음을 공통·Claude 계약에 반복 명시 |
| Codex 승인 안전성 | PASS | exact command, standalone phrase, one-shot, session isolation 테스트 |
| Claude 승인 경로 | PASS | 공식 `PreToolUse`의 `ask` JSON과 명령·분류 메시지 테스트 |
| OpenCode 승인 경로 | PASS | 1.18.19 effective config smoke에서 plugin 및 세 ask 규칙 확인 |
| 렌더·감사 | PASS | 26 tests, 두 프로젝트 각 128 managed files audit PASS |

## 발견 사항

| 심각도 | 경로 | 발견 사항 | 필수 조치 |
| --- | --- | --- | --- |
| 해결됨 | `.claude/agents/planner.md` | 도구가 없는 중첩 Explore 실행과 파이프라인 상주 요구가 서브 에이전트 계약과 모순 | 기본 Claude 세션 오케스트레이션·Planner 호출 단위 반환으로 수정 |
| 정보 | `opencode.json` | 현재 adapter는 OpenCode V1 스키마 전용 | V2 업그레이드 시 renderer·smoke 동시 마이그레이션 |
| 정보 | 소비 프로젝트 legacy 파일 | 세 호스트의 `harness_core.py` 고정 해시가 현재 파일과 불일치 | 별도 사용자 판단 전 `--retire-legacy` 금지 |

## 결론

- 현재 승인 범위의 중앙 변경은 PASS다.
- 소비 프로젝트에 적용하려면 별도 sync 승인과 세션 재시작이 필요하다.
