# 탐색 기록

## 기존 자산
- `.agents/skills/policy/portfolio/SKILL.md`: 전용 저장 경로와 문제·고민·결과·성과·회고 구조가 이미 존재한다.
- `.codex/logs/portfolio/`: 기존 portfolio entry 저장 위치가 존재한다.
- Planner/Generator/Refactorer 계약: portfolio를 일부 언급하지만 작성 책임과 종료조건이 서로 다르다.
- `.codex/hooks/require-documentation-stop.py`: source/package 변경의 세션 문서만 검사하고 portfolio와 harness 변경은 검사하지 않는다.

## 확인한 문제
- 필수 산출물 목록과 workflow 종료 단계에 portfolio가 연결되지 않았다.
- Generator/Refactorer의 직접 문서 작성 지시가 orchestrator 문서 책임과 충돌했다.
- 기존 hook은 `git diff --name-only`만 사용해 staged/untracked 파일과 AI 하네스 경로를 놓쳤다.
- portfolio template과 사실성·대화 근거 규칙이 없었다.

## 재사용 결정
- 새 policy를 만들지 않고 기존 `policy-portfolio`를 확장한다.
- 기존 `.codex/logs/portfolio/<slug>/portfolio-entry.md` 경로를 유지한다.
- session과 portfolio에 동일 slug를 사용해 hook이 결정적으로 연결한다.
- `.codex/logs/**`만 변경된 경우에는 재귀 gate를 발생시키지 않는다.

## 대안과 미채택 이유
- `final-summary.md`에 경험 기록 통합: 별도 필수 산출물 요구와 맞지 않아 미채택.
- session 폴더에 portfolio 중복 저장: 기존 전용 저장소와 중복되므로 미채택.
- 문서 규칙만 추가하고 hook 미적용: 누락을 실제로 차단할 수 없어 미채택.

## 공용 UI 탐색
- 현재 프로젝트에는 `src/components/`가 없고 이번 작업은 UI 자산을 변경하지 않는다.
