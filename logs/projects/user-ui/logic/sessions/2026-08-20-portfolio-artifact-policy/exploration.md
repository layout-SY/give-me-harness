# 탐색

## 확인한 현재 구조

- `require-documentation-stop.py`의 `REQUIRED_ARTIFACTS`가 기존 7종 문서를 강제한다.
- `artifact_issues`가 파일 존재·실질 내용과 Grill Me 구조를 검사한다.
- `.codex/hooks.json`은 entry script와 `hook_common.py` 결합 SHA-256을 검증한다.
- `hook_common.is_protected_path`는 `src`, `.agents`, `.codex`, `.harness`, `docs`를 보호하지만 `.claude`와 `CLAUDE.md`는 포함하지 않았다.
- `policy-portfolio`는 포트폴리오 기록을 선택 사항으로 설명했다.

## 불러온 스킬

- `customize-opencode`
- `policy-documentation`
- `policy-portfolio`
- `policy-harness`
- `programming`과 Python reference
- `debugging`과 Python·조사·수정·QA·정리 reference

## 결론

지침만 추가하면 누락을 막지 못하므로 정책, 템플릿, workflow, Stop hook, 테스트, 무결성 해시를 함께 변경해야 한다.
