# 구현 로그

## 승인된 범위

결론: 사용자가 승인한 시민참여 FSD pages 리팩터링을 완료했다. 기존 URL, API 요청, route component 이름, UI 마크업과 CSS를 유지하면서 조합 책임과 표시 mapper만 상위 레이어로 이동했다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `src/pages/citizen-participation/` | route wrapper 5개, route state hook, presentation mapper와 테스트를 이동하고 공개 API를 추가 | page 조합 책임이 pages 레이어에 위치함 |
| `src/features/citizen-participation/index.ts` | pages가 사용하는 UI, query/mutation, parser, DTO와 표시 타입을 공개 | pages가 feature 내부 deep path 없이 소비함 |
| `src/app/routing.ts` | 시민참여 route import를 feature에서 pages 공개 API로 변경 | `app → pages → features` 방향이 성립함 |
| `src/app/mocks/` | MSW worker bootstrap을 shared에서 app으로 이동 | shared의 feature 상향 import가 제거됨 |
| `src/features/citizen-participation/testing.ts` | mock handler 전용 공개 API를 추가 | production barrel과 테스트 지원 경계가 분리됨 |
| `src/main.tsx` | `startMocks` import를 app 경계로 변경 | 앱 초기화 책임이 app에 위치함 |

## 결정 사항

- production UI 파일과 CSS는 이동하거나 수정하지 않았다.
- `entities`는 cross-feature 재사용 근거가 없어 추가하지 않았다.
- compatibility shim 없이 기존 integration/model 원본을 삭제하고 새 pages 경로를 단일 진실 공급원으로 사용했다.
- app MSW bootstrap만 이동하고 feature mock handler와 fixture는 feature에 유지했다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| focused `npx vitest run ...` 7 files | 7 files, 19 tests 통과 |
| `npm run build` | TypeScript 및 Vite build 통과; 기존 500 kB chunk 경고 존재 |
| `npm run lint` | 통과 |
| 레이어 상향 import 검사 | `shared → features/pages/app`, `features → pages/app` 위반 없음 |
| 금지 타입 패턴 검사 | `as any`, `as unknown`, suppress directive, enum 없음 |
| production bundle route 문자열 검사 | 시민참여 route 문자열 확인 |
| production preview + `curl` | 메인·제안 상세·설문 상세 URL 모두 HTTP 200 |
| `npm test` | 35 files 중 33 통과, 138 tests 중 135 통과; auth 1건·meeting 2건의 범위 밖 기존 실패 |
| `python3 -I .codex/hooks/test_governance_hooks.py` | 20 tests 중 19 통과; `.gitignore`의 `AGENTS.md` 항목 때문에 범위 밖 1건 실패 |

## Watcher 인계

`src/app/routing.ts`, `src/pages/citizen-participation`, `src/features/citizen-participation/index.ts`, `src/app/mocks`, `src/main.tsx`의 의존 방향과 focused 검증 근거를 기준으로 판정한다. unrelated worktree 변경인 `DESIGN.md`, `src/shared/api/common/dto.ts`, `.opencode/`, `docs/external-browser-deep-link-auth.md`는 이번 변경으로 평가하지 않는다.
