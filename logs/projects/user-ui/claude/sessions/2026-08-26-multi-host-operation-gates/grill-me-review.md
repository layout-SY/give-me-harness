# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 역할 | Planner/Evaluator가 전체 코드를 읽으면 Claude의 구현 소유권도 넓어지는가? | 아니다. 분석 도구만 보유하고 쓰기·구현·PASS/FAIL을 금지했다. | agent frontmatter와 `CLAUDE.template.md` | 읽기 권한과 쓰기 소유권을 별도 계약으로 유지한다. |
| 수명주기 | Planner 서브 에이전트가 파이프라인 전체를 오케스트레이션할 수 있는가? | 기존 계약은 불가능했다. | `Agent` 도구 부재와 호출 단위 서브 에이전트 구조 | 기본 Claude 세션이 오케스트레이션하고 Planner는 계획 결과만 반환한다. |
| 동시성 | 같은 프로젝트 또는 다른 프로젝트의 Codex 승인이 섞일 수 있는가? | 저장소·호스트·session_id 해시로 분리되어 섞이지 않는다. | 세션 격리 단위 테스트 PASS | 현재 격리 키를 유지한다. |
| 승인 | 사용자의 포괄적 문장이 다른 명령까지 승인할 수 있는가? | Codex는 독립 문구와 동일 명령 해시를 모두 요구하고 1회 후 소비한다. | 독립 문구·변경 명령·1회성 테스트 PASS | 현재 exact one-shot 계약을 유지한다. |
| OpenCode | OpenCode도 Python 훅으로 승인 UI를 흉내 내야 하는가? | 아니다. 설치본의 native permission이 사용자 once/always/reject를 직접 제공한다. | OpenCode effective config smoke PASS | drift/managed 편집은 plugin, 실행 승인은 native permission으로 분리한다. |
| 버전 | OpenCode V2로 바로 업그레이드해도 되는가? | 아니다. 권한 스키마 이름과 구조가 다르다. | V1/V2 공식 문서 비교 | renderer 마이그레이션과 smoke 갱신을 같은 변경으로 수행한다. |

## 결론

- 승인·세션 격리·역할 소유권은 요청한 네 세션 동시 운용과 양립한다.
- 발견한 Planner의 중첩 위임·상주 모순은 기본 세션 오케스트레이션 구조로 수정했다.
- 현재 남은 위험은 소비 프로젝트 미동기화와 OpenCode V2 업그레이드 시 설정 변환이다.
