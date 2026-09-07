# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 종료 lifecycle | 산출물 완성을 어느 시점에 강제해야 하는가? | 일반 Stop이 아니라 명시적 완료·보존 명령 | Stop block은 자동 continuation을 만들어 반복됨 | finish/verify/close/preserve에서 강제 |
| 읽기 전용 조사 | 어떤 Git 호출을 승인 없이 허용할 수 있는가? | 파서가 확정적으로 조회형으로 분류한 호출 | status/diff/log/branch list/worktree list는 저장소를 바꾸지 않음 | 공통 classifier, 미분류 fail-closed |
| 산출물 귀속 | 문서 최초 쓰기가 branch proposal 승인을 다시 요구해야 하는가? | 아니오. 현재 session/host 경로와 구조화된 Write 여부를 검증 | task 계약과 문서 귀속 계약은 별개 | 세션 binding 검증 후 허용 |
| 재시작 | 최신 중앙 정책 적용에 항상 sync가 필요한가? | sync mode만 필요, inject는 새 digest launcher 재실행 | inject는 소비자 파일을 쓰지 않음 | mode별 절차를 문서로 분리 |
| 승인 | `전부 승인`이 모든 명령 승인까지 포괄하는가? | 아니오 | Codex shell 승인은 정확한 명령별 1회 계약 | 구현 승인만 충족 |

## 결론

일반 종료와 완료 검증을 분리하고, 조회·변경 명령의 공통 분류를 재사용하는 현재 설계가 문제의 원인을 직접 제거한다. 보안 경계인 변경형 Git·정확한 명령 승인·branch 계약은 완화하지 않았다.
