# Multi-Agent Execution Specification

사용자 지시와 루트 `CLAUDE.md`가 이 명세보다 우선한다. 이 명세의 Claude Code 역할은 production UI 범위로 제한한다.

상세 명세는 100줄 이하 단위로 분리되어 있으며, 아래 순서대로 읽는다.

## Spec Index

1. `./multi-agent-spec/01-common-and-planner.md`
   - 공통 운영 원칙
   - 기획자(Planner)
2. `./multi-agent-spec/02-publisher-and-generator.md`
   - 퍼블리셔(Publisher)
   - 생성자(Generator)
3. `./multi-agent-spec/03-refactorer-and-watcher.md`
   - 리팩터(Refactorer)
   - 감시자(Watcher)
4. `./multi-agent-spec/04-evaluator-and-harness.md`
   - 평가자(Evaluator)
   - 하네스(Harness)
5. `./multi-agent-spec/05-pipeline-and-status.md`
   - 권장 파이프라인
   - 상태 전이 규격
6. `./multi-agent-spec/06-documentation-and-core-rules.md`
   - 문서화 규격
   - 핵심 운영 규칙

## Notes

- 각 분할 파일은 100줄 이하를 유지한다.
- 역할/게이트/산출물 기준 변경 시 해당 섹션 파일만 수정한다.
- 최상위 진입점은 계속 이 파일(`.claude/multi-agent-spec.md`)을 사용한다.
