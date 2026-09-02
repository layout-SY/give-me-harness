# 탐색

## 요청

- CP 도메인의 반복된 validation/parser 패턴 불일치를 정렬한다.
- UI 관련 수정은 이번 branch에서 제외하고, 사용자 최신 지시에 따라 Claude Code를 사용하지 않고 GPT Sol로만 작업한다.

## 대상 관련 사실

- discussion/vote 입력 날짜는 문자열 형식만 확인해 불가능한 달력 날짜를 허용했다.
- comment/proposal/board/report의 지정된 query/process 입력 schema는 unknown key를 제거했지만 실패시키지 않았다.
- comment/proposal 응답은 extra key를 허용하며 board/report 응답은 이미 strict였다.
- board bulk-hide 응답 schema가 hook 내부에 있어 다른 board 응답 parser와 소유권이 달랐다.
- mutation의 상세 cache 갱신과 목록 invalidation은 기존 동작으로 보존해야 했다.

## 불러온 스킬

- `skill-index`, `policy-index`, `reference-index`, `recipe-index`
- `policy-validation`, `policy-type-definition`, `policy-coding-convention`
- `recipe-data-dto`, `recipe-api-authoring`, `policy-data-fetch-layer`, `policy-tanstack-query`
- `policy-review-checklist`, `policy-documentation`, `policy-portfolio`, `policy-abstraction-strategy`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| `src/shared/ui/**` | 사용하지 않음 | 이번 범위는 DTO/parser/hook 경계이며 production UI 수정이 없다. |
| `src/shared/lib/validation` | 재사용·확장 | discussion/vote가 동일한 ISO 달력 날짜 의미와 변경 압력을 공유한다. |
| `src/entities/cp-board/api/cp-board.parser.ts` | 재사용·확장 | board 응답 파싱의 기존 API 계층 소유권과 일치한다. |

## 제약 조건 및 미확인 사항

- CodeGraph는 linked worktree index가 없어 사용하지 않았다.
- Biome LSP는 설치되지 않았고 사용자가 설치를 거부해 ESLint/build로 대체했다.
- `package.json`에 `test` script가 없고 full lint에는 변경 범위 밖 기존 오류 73건과 경고 5건이 있다.
- UI Todo 5~7의 구현·검증 결과는 아직 없다.
- OpenCode의 Claude Code 호환 hook은 linked worktree에서 배포 파일을 찾지 못했으므로 공식 user-level 설정으로 호환 command만 임시 비활성화하고 native OpenCode guard는 유지했다.

## 결론

- 공용 날짜 schema 1개, 지정 입력 schema의 `.strict()`, 기존 API parser 확장만으로 요구를 충족할 수 있었다.
- 응답 schema, cache callback, UI, package/config는 변경할 이유가 없어 범위에서 제외했다.
