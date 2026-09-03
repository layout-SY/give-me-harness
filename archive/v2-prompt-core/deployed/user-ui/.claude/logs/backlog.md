# Backlog — 후속 작업 티켓

> 진행 중 세션에서 발생한 후속 티켓을 여기에 누적한다. 세션 단위 로그(`logs/sessions/*`)는 task가 끝나면 멈추지만, 본 문서는 다음 세션이 picking up할 표준 진입점이다.
> 처리 시: 해당 항목을 세션 task로 옮기고, 본 문서에서는 완료 표시(`[x]`) 후 origin 세션 로그를 링크.

## 우선순위 표기

- **P0** — 즉시 처리 권장 (ROI 높음 / 진행 중 작업 차단)
- **P1** — 이번 분기 내 처리 (구조 개선)
- **P2** — 검토/합의 필요 (라이브러리 도입 등 큰 결정)

---

## 1. Reason Prompt 트랙 후속

Origin: `.claude/logs/sessions/2026-05-07-reason-prompt-extraction/`

### [ ] F-01 — moderation 전용 i18n 키 분리 (P1)

- 배경: discuss-posts `handlePostModeration`에서 임시로 `_dao_msg_delete_success`를 재사용 중. 라벨도 `_dao_proposal_forceEndVote_reason_*`를 도메인 무관 의미로 재사용.
- 작업
  - `_dao_msg_moderation_hide_success`, `_dao_msg_moderation_restore_success` 신설 (현재 코드는 이미 새 키를 참조 중 → i18n 파일 등록만 필요)
  - 디스커션 게시글 숨김 전용 라벨 키 분리 검토 (`_dao_post_hide_reason_title/placeholder/submit`)
- 영향 파일
  - `src/assets/i18n/ko.json`, `src/assets/i18n/ja.json`
  - `src/pages/dao/discuss-posts-management/detail/_id.modal.tsx`(라벨 키 교체)
- 메모: tsc strict 키 검증이 활성화되어 있어 i18n 키 누락 시 빌드 에러. 라이브 빌드 깨짐 여부 확인 필요.

### [ ] F-03 — discuss-posts 도메인 try/finally setIsLoading 안티패턴 정리 (P1)

- 배경: `execute()` 호출 직후 finally에서 즉시 `setIsLoading(false)`. 비동기 onSuccess 이전에 로딩이 종료되어 인디케이터가 형식적.
- 영향 파일 (1차)
  - `src/pages/dao/discuss-posts-management/detail/_id.modal.tsx` — `requestGet`, `handleDeletePost` (`handlePostModeration`은 callback 내 setIsLoading만 있고 종료 처리는 누락 상태이므로 함께 정합)
- 후속(연계): `evaluation-log.md` BL-6 (코드베이스 전반 일괄 정리)

### [ ] reason-prompt 트랙 미작성 SKILL 링크 점검 (P2)

- generator가 known risk로 보고: `use-language` SKILL.md 실체 부재로 링크 깨짐 가능성.
- 작업: `.claude/skills/reference/custom-hooks/use-language/SKILL.md` 작성 또는 링크 제거.

---

## 2. Form 상태 관리 트랙 (form-state-evaluation 백로그)

Origin: `.claude/logs/sessions/2026-05-07-form-state-evaluation/evaluation-log.md`

### P0 (가장 높은 ROI, 즉시 효과)

#### [ ] BL-1 — `useSearchParamsState` 공용 훅 도입

- 위치: `src/hooks/use-search-state.ts` (신설)
- 책임: URL ↔ state 양방향 동기화. 도메인 무관.
- 부수 작업
  - 키 직렬화 규약(plain string, undefined 제거, page=1 default 등)을 SKILL.md로 사전 고정
  - 가장 단순한 list 1곳(예: `dao/dao-logs`)에 첫 적용하여 규약 확정
- 효과: enum FILTER_TYPES + handleFilter 거대 switch 단순화, 새로고침 시 필터 유실 해소

#### [ ] BL-2 — dao/proposal-manage 도메인 빌더 함수 분리

- 위치: `src/pages/dao/proposal-manage/model/payload.ts` (신설)
- 작업
  - `toProposalDraft(detail)` 이전
  - `buildCreateProposalPayload(form)`, `buildUpdateProposalPayload(form, prev?)` 분리
  - 단위 테스트 추가
- 효과: `Partial<Dto>` mode union 트릭 폐기, 테스트 가능성 확보

#### [ ] BL-3 — 검증 빌더 표준 시그니처 도입 (PoC)

- 시그니처: `validateXxxPayload(form): { ok: boolean; messageKey?: string }`
- 적용 대상 (PoC): `dao/proposal-manage/create`, `admin-settings/admins/create`
- 효과: 모든 inline if + Dialog.alert 패턴을 한 함수로 압축. zod 도입 시 1:1 교체 가능한 시그니처.

### P1 (구조 개선, 점진 가능)

#### [ ] BL-4 — `useProposalForm` hook 추출

- 대상: `src/pages/dao/proposal-manage/detail/_id.modal.tsx`
- 캡슐화: formState/dirty/mode/category 핸들러
- `JSON.stringify` dirty check 폐기 (필드별 비교 또는 ref baseline)

#### [ ] BL-5 — `useProposalDetailFetch` 인터페이스 정상화

- 변경: `setIsLoading` 외부 주입 폐기 → hook 자체가 `{ isLoading, run }` 반환
- 효과: 다른 mutation hook의 표준 템플릿으로 채택

#### [ ] BL-6 — try/finally setIsLoading 안티패턴 코드베이스 grep + 일괄 수정

- 작업: 패턴을 `await execute(...)` 또는 mutation hook 내부 useState로 통일
- 차단: SKILL.md(또는 ESLint custom rule) 추가하여 신규 진입 방지
- F-03(discuss-posts 1차)을 흡수 가능

### P2 (라이브러리 도입, 큰 결정 필요)

#### [ ] BL-7 — react-hook-form + zod 도입 (PoC)

- 파일럿 대상: `manage/items/_id.modal.tsx` (1006 lines)
- 사전 작업: 공용 RHF 어댑터(TextInput / Dropdown / DateRangeField / TextArea)
- 결정 필요: 라이브러리 도입 합의

#### [ ] BL-8 — TanStack Query 도입 (PoC)

- 파일럿 대상: 1개 도메인(예: `dao/dao-logs`)
- 작업
  - `useFetchAdapter`를 query 위임으로 단계 교체
  - `pubsub("refresh-xxx")` → `queryClient.invalidateQueries`로 이전
- 결정 필요: 라이브러리 도입 합의 + 마이그레이션 전략(어댑터 내부 위임 vs 직접 교체)

#### [ ] BL-9 — pubsub 모달 → Promise 모달 API 전환 설계

- 설계서 작성 + `forceEndVoteReasonModal` 패턴(이미 `useReasonPrompt`로 callback형 유지)을 Promise형으로 1건 PoC 이전
- 효과: 비동기 합성 비용 절감

---

## 3. 처리 절차

1. 처리 시작 시 본 문서에서 해당 항목을 in-progress 표기 (예: `[~]`)
2. `logs/sessions/<date>-<slug>/` 새 세션 폴더 생성, plan.md/implementation-log.md 작성
3. 완료 시 본 문서 항목을 `[x]` 표기 + origin 세션 폴더 링크 추가
4. 새로 발견된 후속 티켓이 있으면 본 문서에 append
