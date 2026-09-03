# Codex 프롬프트 경량화 탐색 기록

## 스킬 확인

- `policy-index`, `policy-harness`, `policy-documentation`, `policy-portfolio`, `policy-review-checklist`, `policy-refactoring`, `programming`을 확인했다.

## 재사용 자산 탐색

- 실제 공용 UI 루트: `src/shared/ui/`
- 실제 레이아웃·합성 루트: `src/widgets/`
- 도메인 기능 루트: `src/features/`, `src/entities/`, 대상 페이지
- 공용 hook 루트: `src/shared/lib/hooks/`
- reference 계약: `.agents/skills/reference/`
- 장기 인덱스: `.codex/memory/reusable-assets.md`

## 발견한 불일치

- 운영 프롬프트와 hook marker가 존재하지 않는 `src/components/`를 요구했다.
- 여러 reference가 이전 `src/hooks/` 및 `src/components/` 구현 경로를 가리켰다.
- OMO 계획이 API 검증에 fresh browser와 Playwright를 반복 요구했다.
- Watcher API 비가용을 표현하는 상태가 없어 반려·retry·Closure와 혼동될 수 있었다.

## 선택

- reference 문서 경로와 실제 source 경로를 분리해 기록한다.
- 브라우저 대신 Node API/module 또는 HTTP driver와 독립 MSW process/store를 사용한다.
- API 비가용은 `watcher_unavailable → paused_after_generator`로 기록하고 retry count를 증가시키지 않는다.
