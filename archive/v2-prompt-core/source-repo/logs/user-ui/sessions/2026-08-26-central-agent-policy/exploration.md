# 탐색

## 요청

- user-ui의 정책을 기준으로 별도의 최소 중앙 정책 프로젝트를 만들고 두 프로젝트가 공유하게 한다.
- 소비 프로젝트 세션에서 정책 추가·수정을 거부하고 중앙 프로젝트 이동 및 세션 재시작을 안내한다.

## 대상 관련 사실

- 실제 user-ui 스택은 React 19.2.8, Vite 8.2.0, TypeScript 6.0.2, Zustand, React Router 7.18.2다.
- 전달된 외부 지침의 `synthoria-admin-ui`, React 18, Vite 6, TypeScript 5.8, Jotai 정보는 실제 user-ui와 불일치한다.
- Agora SDK는 user-ui와 admin-ui 양쪽 소스에서 실제 사용한다.
- admin-ui의 기존 AI 지침에는 현재 존재하지 않는 yarn 명령과 오래된 재사용 탐색 경로가 있다.
- Codex 공식 문서상 `AGENTS.md`는 세션 시작 시 instruction chain으로 로드되며, 프로젝트 hook은 신뢰된 저장소에서 `PreToolUse` 차단을 지원한다.

## 불러온 스킬

- `skill-index`
- `policy-index`
- `policy-harness`
- `policy-documentation`
- `policy-abstraction-strategy`
- `policy-review-checklist`
- `policy-portfolio`
- `openai-docs`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| user-ui `src/shared/ui/` | 프로젝트 전용 유지 | 73개 파일이며 실제 구현 카탈로그는 프로젝트 상태에 종속됨 |
| admin-ui `src/shared/ui/` | 프로젝트 전용 유지 | 79개 파일이며 user-ui와 동일 경로 65개 중 내용까지 동일한 파일은 3개 |
| `src/shared/ui/` 우선 탐색 정책 | 중앙화 | 두 프로젝트에서 동일한 의미와 생명주기를 공유함 |

## 제약 조건 및 미확인 사항

- 실제 호스트 smoke test는 설치된 CLI와 프로젝트 신뢰 상태에 영향을 받는다.
- Claude Code의 UI 전담 계약은 이번 버전에서 유지한다.
- 프로젝트별 overlay는 후속 기능으로 남긴다.

## 결론

- 공통 행동 정책만 중앙화하고 프로젝트 사실·카탈로그는 최소 manifest 또는 프로젝트 소유 파일로 남긴다.
- 기존 `asan-harness` 대신 중앙 원본, 얇은 어댑터, 해시 manifest, guard만 새로 구현한다.

