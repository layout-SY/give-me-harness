# 계획

## 요청 요약
- `SESSION_HANDOFF.md`를 기준으로 현재 Agora 회의 이식 변경을 기존 커밋 관례에 맞춰 작업 단위별로 커밋한다.

## 작업 유형
- publish-only

## 범위
- Agora RTC 및 아이콘 의존성
- `src/features/meeting/**` 이식 초안
- `SESSION_HANDOFF.md`

## 제외 범위
- 2026-07-06~09의 별도 미커밋 변경: `src/ARCHITECTURE.md`, Dropdown, form/validation placeholder
- 라우터 연결, 공용 UI/Axios 적용, 스타일 이식
- push 및 PR 생성

## 섹션
1. 대상 스냅샷 검증
2. Watcher 및 Evaluator 검토
3. 의존성, 기능 초안, 문서 순서의 명시적 staging 및 커밋

## 필요 에이전트
- Planner: 커밋 경계 검토
- Watcher: 현재 스냅샷 품질 게이트
- Evaluator: 장기 구조 리스크 진단
- Orchestrator: 검증, 문서화, staging, commit

## 필요 스킬
- `github:yeet`
- `policy-orchestration`
- `policy-harness`
- `policy-review-checklist`
- `policy-codex-native-quality`
- `policy-documentation`

## 리스크 / 가정
- 기능은 라우터에 연결되지 않은 이식 초안이다.
- 전체 저장소 lint/typecheck에는 이번 범위 밖의 선행 오류가 있다.
- 커밋 대상만 복원한 임시 스냅샷 검증 결과를 품질 근거로 사용한다.

## 승인 요청
- 2026-07-22 사용자 승인: `작업 진행`
