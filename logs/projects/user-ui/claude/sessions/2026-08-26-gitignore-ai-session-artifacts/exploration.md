# 탐색

## 재사용 자산

- 기존 `.gitignore`에 `.claude/logs/`가 이미 있음. `.codex/logs/`는 없었음
- 하네스 소스(`.agents/skills`, `.codex/agents`, `AGENTS.md`)는 계속 추적 대상으로 둠

## 제외한 커밋(재작성 전 `sy-main`, 미푸시)

| 해시 | 메시지 | 내용 |
| --- | --- | --- |
| `fb9d501` | docs : 포트폴리오에 세션·하네스 사고 근거 기록을 보강한다 | AGENTS.md, documentation/portfolio 스킬, portfolio-log 템플릿 |
| `d100961` | docs : 관리자 UI 하네스 비교와 세션 근거를 이관한다 | 2026-08-22/23 세션 로그, `docs/admin-ui-harness-gap-analysis.md` |
| `0876905` | docs : 시민참여 API 계약과 타입 수정 작업 근거를 남긴다 | 2026-08-25 시민참여 세션 로그 |

## 유지한 커밋

| 구 해시 | 신 해시 | 메시지 |
| --- | --- | --- |
| `397f7b6` | `1edafac` | fix : 날짜 범위 선택 팝오버 앵커와 날짜 숫자를 복구한다 |
| `0102a4d` | `4721e10` | feat : 시민참여 제안·투표 API 계약을 확정 스펙에 맞춘다 |

## 확인한 사실

- `origin/sy-main`은 `481c55c`
- 재작성 전 브랜치는 origin보다 5커밋 앞섰고 푸시되지 않음
- `git ls-files '.codex/logs'` 기준 origin 추적 파일은 122개(2026-08-05~08-20 세션)
