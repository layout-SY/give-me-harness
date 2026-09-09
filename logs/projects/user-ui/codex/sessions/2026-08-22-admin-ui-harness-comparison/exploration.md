# 탐색

## 요청

admin-ui 전체 하네스와 user-ui 하네스를 비교해 세션 동작 차이의 구조적 원인을 제시하고, 결과를 문서화한 뒤 user-ui 반영 상태를 확인한다.

## 대상 관련 사실

- admin 첫 OpenCode session `ses_fed718db7ffeH34R6D3MMPOQ5X`는 UI 금지 지시 후에도 browser·visual QA와 UI 변경을 반복했다.
- admin 두 번째 session `ses_fdda42f14ffex0tqSJNWSonin8`는 compaction 전후 UI/CSS와 browser QA 목표를 복원했다.
- user-ui session `ses_0066fec2effe4lzg9D1jdycHJY`의 main QA는 test, lint, build, Python governance 중심이었다.
- admin 하네스 관련 Git tracked file은 0개, user-ui는 251개였다.
- admin package에는 test script가 없고 user-ui는 Vitest와 governance test를 연결한다.

## 불러온 스킬

- `coding-agent-sessions`
- `policy-index`
- `policy-harness`
- `policy-documentation`
- `policy-portfolio`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| `src/shared/ui/**` | 사용하지 않음 | 문서화 전용 작업이며 application UI를 변경하지 않는다. |

## 제약 조건 및 미확인 사항

- `.codex/hooks.json`은 Codex 경계이며 OpenCode에서 자동 실행되는 adapter는 저장소에서 확인되지 않았다.
- user-ui Python Hook도 승인 후 UI/CSS·browser·Watcher를 직접 hard deny하지 않는다.
- 세션 전체에서 Watcher가 전혀 없었다는 사용자 평가는 현재 main QA에는 부합하지만 전체 child 이력에는 예외가 있다.

## 결론

user-ui에는 역할·파일 소유권·QA 제한과 identity-bound Codex governance가 반영돼 있다. admin-ui의 반복 위반을 모든 호스트에서 물리적으로 차단하려면 공통 policy core와 Codex·Claude·OpenCode adapter가 추가로 필요하다.
