# 실행 세션의 필수 산출물·포트폴리오 생산 조사

2026-09-17 관찰. 결론: **소비자 프로젝트에서 실행 중인 6개 세션 모두 plan.md와 final-summary.md를 생산했지만, portfolio-log.md는 0/6개다.** 포트폴리오가 없어서 내용의 충실성도 평가할 수 없다. 현재 작업의 포트폴리오는 별도로 작성했다.

## 조사 근거와 대상 확정

- `bin/agent-policy sessions --project user-ui --json`, admin-ui의 동일 명령으로 assignment, host, native session, binding, 정책 bundle을 읽었다. resumable은 실행 중이라는 뜻이 아니므로 이것만으로 활성 여부를 판정하지 않았다.
- 프로세스 목록의 PID·시작 시각과 실제 환경의 `ASAN_AGENT_POLICY_ASSIGNMENT`, `ASAN_AGENT_POLICY_PROJECT`를 대조했다. 환경 전체나 대화 원문은 저장하지 않았다.
- 확인한 7개 codex/claude 프로세스 중 6개가 소비자 assignment와 일치했다. PID 28934는 중앙 저장소 작업으로 소비자 집계에서 제외했다. item-category-api는 최근 세션 목록에 있지만 이 6개 활성 프로세스와 연결되지 않아 활성 표에서 제외했다. 초기 진행 보고의 7개 추정치를 최종 확인으로 정정한다.
- binding이 가리키는 **실제 consumer/worktree의 host 로그 폴더**를 읽었다. 중앙 `logs/projects/...` 복사본만으로 누락을 판정하지 않았다. bundle의 runtime-policy 계약도 각 세션별로 확인했다. 과거 bundle은 현재 정책을 실행하기 위해서가 아니라 해당 세션의 의무를 확인하기 위한 증거로만 읽었다.
- [최종 관찰 JSON](operations/2026-09-17-session-portfolio-audit.json)에 시각, 정확한 경로, 주입 계약, 파일 크기·SHA-256·제목을 남겼다. 파일명과 본문 존재를 확인했으며 다른 세션의 테스트 실행을 이번 작업에서 재현한 것으로 간주하지 않는다.

## 실제 생산 상태

`있음`은 비어 있지 않은 문서가 존재한다는 뜻이다. 모든 기술 주장이 독립적으로 검증되었다는 인증은 아니다. 세션의 프로세스 생존은 해당 작업이 지금 연산 중이라는 뜻이 아니라 대화 세션이 열려 있다는 뜻이다.

| 프로젝트 / host   | PID / assignment 앞 8자리 | 실제 세션 폴더                                                      | plan | final-summary | handoff | portfolio |
| ----------------- | ------------------------- | ------------------------------------------------------------------- | ---- | ------------- | ------- | --------- |
| user-ui / codex   | 19707 / 2a4aa4cf          | `.codex/logs/sessions/reservation-media-check`                      | 있음 | 있음          | 있음    | **없음**  |
| user-ui / claude  | 79715 / 88f1e078          | `.claude/logs/sessions/전역-모달-팝업-계약-통일`                    | 있음 | 있음          | 없음    | **없음**  |
| admin-ui / codex  | 23869 / bf0bc87a          | event worktree `.codex/logs/sessions/event-attendance-roulette-api` | 있음 | 있음          | 있음    | **없음**  |
| admin-ui / codex  | 65325 / 75be0ed6          | video worktree `.codex/logs/sessions/video-api`                     | 있음 | 있음          | 있음    | **없음**  |
| admin-ui / codex  | 66762 / d0a30c3b          | `.codex/logs/sessions/usage-api`                                    | 있음 | 있음          | 없음    | **없음**  |
| admin-ui / claude | 21628 / 91a69efa          | `.claude/logs/sessions/2026-09-14-ui-91a69efa`                      | 있음 | 있음          | 있음    | **없음**  |

첫 파일 조사에서는 reservation-media-check와 event 세션에 plan만 있었다. 최종 재확인 시 둘 다 final-summary와 handoff가 추가되어 위 표를 갱신했다. 따라서 진행 중이라 아직 생성하지 않은 최종 산출물을 완료 작업의 누락으로 단정하지 않았다. portfolio는 두 관찰 모두 없었다. handoff가 없는 두 owner 세션은 그것만으로 위반이 아니다.

## 왜 포트폴리오가 자동으로 생산되지 않는가

6개 세션에 주입된 runtime-policy의 artifacts 계약은 모두 다음과 같다.

- required: `plan.md`, `final-summary.md`
- handoff: `handoff.md`
- optional: exploration, implementation, grill-me, review, evaluation, **portfolio-log.md**

현재 중앙 `policy/common/skills/policy/documentation/SKILL.md`와 `portfolio/SKILL.md`도 포트폴리오를 작업 규모나 사용자 요청에 따라 선택한다. 그러므로 **사용자가 기대하는 포트폴리오 생산과 현재 기본 정책은 일치하지 않는다.** 단순히 파일이 없다는 이유로 이 세션들이 주입 정책을 위반했다고 말할 수는 없다. 사람이 별도로 요청한 요구는 정책 기본값보다 우선한다. 각 세션의 확인 가능한 사용자 메시지에서 관련 요청 검색도 했지만, 모든 과거·압축 대화의 요구 부재를 증명한 것은 아니다.

검사 구현에도 범위 차이가 있다. `policy/guards/artifact_policy.py`의 `artifact_issues`는 `REQUIRED_ARTIFACTS`만 읽고, 이어 `texts.get("portfolio-log.md")`가 있을 때에만 `_portfolio_issues`를 적용한다. 현재 optional인 portfolio는 이 required-only 경로에서 내용 검사를 받지 못한다. `artifact_has_content`도 최소 본문 존재 기준이므로 결과의 사실성이나 포트폴리오 서술 품질을 증명하지 않는다. 같은 파일에는 “필수 산출물 8종”이라는 이전 안내 문자열도 남아 있어 현재 required 2종 계약과 혼동될 수 있다. 이번에는 이 동작을 조사·문서화했으며 런타임 필수 목록이나 guard를 임의로 변경하지 않았다.

## 개선 방향과 근거

1. **이번 작업에는 명시적 요청을 적용한다.** 조사·문제·근거·개선·검증을 기록하고, 실제 수행한 사례별 portfolio를 생산한다. 이번 작업 폴더는 `.codex/logs/sessions/api-pattern-standardization/`이다.
2. **기존 세션에는 담당 세션에서 작성할 근거를 남긴다.** 각 owner가 본인의 대화·구현·검증을 이용해 사례를 작성해야 한다. 다른 세션의 내용을 추정하여 대신 채우면 성과·선택·테스트 결과를 조작할 위험이 있다. 이번에는 다른 세션의 산출물을 수정하거나 외부 메시지를 발송하지 않았다.
3. **항상 생산하려는 정책이라면 별도 정책 변경으로 결정한다.** required 목록, documentation·portfolio skill, 템플릿, guard, 호스트 안내를 함께 맞춰야 한다. commit·merge-only 면제와 일반 기능 작업을 구분하고, portfolio가 선택되어 파일이 존재할 때 구조 검사를 수행하도록 개선할 수 있다. 이는 제안이며 이번에 모든 작업의 portfolio를 강제한 것은 아니다.
4. **형식 검사와 내용 리뷰를 구분한다.** 검증기는 사례 metadata와 필수 6개 제목, 빈 placeholder를 검사한다. 사람/에이전트 리뷰는 문제→대안→선택 이유→수정 경로→실제 검증→한계를 확인한다. 성능 수치나 사용자 만족을 실제 측정 없이 만들지 않는다.
5. **새 정책은 새 inject 세션에서 적용한다.** 중앙 source를 바꾸어도 기존 assignment의 bundle은 고정된다. `--resume-assignment`는 원래 bundle을 유지한다. 각 담당 세션이 handoff를 남기고 필요한 worktree·role·host·model을 유지해 새 launcher 세션으로 이어야 한다. 실행 중인 다른 대화를 임의 종료하거나 같은 작업을 맡는 새 세션을 중복 기동하지 않는다.

새 세션의 실제 명령 형태는 `bin/agent-policy start --project <user-ui|admin-ui> --host <codex|claude> --mode inject --role <logic|ui> --responsibility owner --worktree <현재 작업 worktree>`다. 모델 선택은 독립 인자로 보존한다. 실행 전 `--print-only`로 bundle과 경로를 확인할 수 있다. 이번 작업에서는 적용 가능한 handoff와 재시작 절차를 문서로 제공했으며, 6개 기존 세션의 재시작이나 새 정책 수신 완료를 주장하지 않는다.
