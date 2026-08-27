# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 기준 | 현재 작업 트리와 Git HEAD 중 무엇이 재현 가능한 기준인가? | Git HEAD | 현재 작업 트리 AI 파일에 기존 중앙 배포 흔적이 있었음 | commit을 고정하고 교정 사항을 별도 기록한다. |
| 공통화 | 실제 컴포넌트·hook 카탈로그가 두 프로젝트에서 같은가? | 같다고 보장할 수 없음 | `src/shared/ui` 공통 경로 65개 중 byte-identical은 3개였고 custom hook 경로도 프로젝트 사실임 | 검색 절차만 공통화하고 실제 목록은 중앙에서 제외한다. |
| host | host 선택과 model 선택은 같은 결정인가? | 별도 결정 | 각 CLI가 `--model`을 별도 지원함 | `start --host ... --model ...`로 분리한다. |
| 안전 삭제 | 기존 파일이 감사 뒤 바뀌면 자동 퇴역해도 되는가? | 안 됨 | 두 대상의 legacy 3개 hash가 감사 뒤 변경됨 | 사용자 확인 전 삭제를 거부한다. |
| 세션 갱신 | 중앙 변경을 실행 중 세션에 hot reload할 것인가? | 하지 않음 | Codex는 AGENTS chain을 세션 시작 시 구성함 | sync, handoff, 새 세션 순서를 강제한다. |

## 결론

중앙 구현은 요구사항을 충족한다. 실제 배포는 concurrent legacy 변경의 소유권과 폐기 여부가 해결될 때까지 보류하는 것이 안전하다.
