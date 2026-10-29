# 병합 검토 보고의 항목 형식 오류 안내

## 발생한 문제

2026-10-26 admin-ui의 orchest 세션(`8f30b034…`)에서 보호 실행기의 `complete --report-json`이 검토 보고를 두 번 거부했다. 세션은 형식을 찾지 못하고 사용자에게 중앙 세션 확인을 요청했다.

- 세션이 보낸 보고는 `comparisons`·`text_conflicts`·`contract_risks`·`unknowns`가 목록이었고, `validation`은 객체 또는 목록이었다.
- 거부 메시지는 "모두 작성하세요"뿐이었다. 어느 항목이 왜 거부됐는지, 값이 문자열이어야 한다는 사실이 없었다.
- `git-branch-strategy` 스킬도 항목 이름만 나열하고 값의 형식을 적지 않았다.

## 원인

`integration_review.require_report`는 `REPORT_FIELDS`의 각 값이 비어 있지 않은 문자열인지 검사한다. 목록·객체는 비어 있지 않아도 거부된다. 이 조건이 오류 메시지와 문서 어디에도 없었다.

## 수정 (사용자 선택)

| 항목 | 내용 |
| --- | --- |
| 오류 메시지 | 문자열이 아닌 항목과 받은 형식을 `확인할 항목: validation: object, unknowns: list`처럼 표시한다. 목록은 문장으로 이어 쓰라고 안내한다 |
| 스킬 문서 | `git-branch-strategy` 3단계에 "각 값은 비어 있지 않은 문자열이며 목록·객체는 받지 않으므로 여러 항목은 한 문자열에 이어 쓴다"를 추가했다 |

- 검사 기준(문자열만 받음)은 바꾸지 않았다.
- `--report <경로>`도 같은 JSON 객체를 받는다. Markdown 파일은 받지 않는다.

## 회귀 테스트

- `tests/test_relation_operations.py`
  - `test_merge_report_error_names_fields_that_are_not_text`: `unknowns`를 목록, `validation`을 객체로 보낸다. 수정 전에는 오류에 `문자열`과 항목별 형식이 없어 실패했다.

## 적용

- 커밋: `9dbbfaa`
- 후속: 보고 틀과 예시는 [오케스트레이션 승인 조회와 형식 안내](orchestration-approval-and-formats-2026-10-27.md)에서 추가했다.
