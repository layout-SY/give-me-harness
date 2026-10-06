# 중앙 정책 실행 구조와 보강 검토

2026-09-30 중앙 원본 V4, 실제 guard·launcher·adapter 코드, 현재 소비자 Git 상태와 인계 문서를 대조했다. 실행 중인 소비자 세션은 시작 당시 bundle을 사용한다. 중앙 수정과 기존 세션의 즉시 복구를 같은 것으로 보고하지 않는다.

## 반영 상태

| 항목 | 이번 반영 | 남은 경계 |
| --- | --- | --- |
| 스킬·탐색 적합성 | 공통 지침과 review-checklist에 선택 이유·재사용 비교·근거 확인 의무 | hook은 성공한 호출/읽기와 경로만 확인하며 의미적 적합성을 평가하지 않는다 |
| 계획 승인 | 승인 영역/진행 기록 분리, 해시 비교, source 변경 전 plan 존재·빈 문서·잘못된 표식 검사 | 계획의 품질·구현과의 일치, UI 자산 문서의 항목 대응은 에이전트 리뷰 의무 |
| 포맷 | 복구 후 정상 저장의 대체 근거 영구 보존, 중복 대상 제거, 명시적 patch 실패 인식, Stop/idle 실제 포맷 | 결과 미확인·부분 실패·타 작성자 변경·stage 파일은 계속 차단 |
| 병합 | 검토 이후 바뀐 branch의 기대/현재 HEAD·변경 파일과 다음 조치 출력, 직접 부모 검사 유지 | 의미적 계약 위험과 영향 판단은 에이전트가 설명 |
| 기준 branch 동기화 | 미반영 commit의 현재 작업 영향을 먼저 검토하고 무관하면 merge하지 않도록 스킬 보강 | 무관 여부를 경로 겹침만으로 판정하는 자동 gate는 아님 |
| inquiry-ui 삭제 기록 | 실제 ref·worktree·graph를 대조하고 퇴역 절차 보강 | 조사 시 이미 deleted=true여서 실제 state를 다시 수정하지 않음 |
| worktree별 준비 | 세션 안에서도 worktree·branch·HEAD·역할별 스킬·탐색 근거 분리 | 계획의 대상·범위가 적절한지는 문서·리뷰로 확인 |
| Git 승인 재개 | 같은 주체의 미실행 일반 Git에 저장 동의로 새 ticket 발급, 철회 검사 | 부분 실행·다른 주체·주체 없는 과거 승인·completion 자동 반복은 제외 |
| host 쓰기 경로 | Codex·Claude launcher가 등록 worktree와 설정된 생성 루트를 `--add-dir`로 전달 | 호스트의 추가 deny·관리자 sandbox 제한은 유지, OpenCode는 기존 native 외부 경로 권한 확인 |
| agent별 격리 | 현재 정책의 재사용 범위·변경 필요·수용 검사를 문서화 | 사용자 결정에 따라 orchestration runtime 구현과 실제 실행은 후속으로 미룸 |

코드와 문서의 보장 범위를 구분한다. 필수 산출물을 만들었다는 사실만으로 실제 작업 범위·품질을 증명했다고 간주하지 않는다.

## 2026-09-30 판매자 UI의 반복 포맷 차단

관리자 `feature/ec-seller-ui`, Claude assignment `67bb25959468413fb94f579f2eaecd4a`, native session `c4cc0ffa-4df7-4879-960f-951115025535`의 중앙 writes와 실제 native JSONL을 대조했다. 06:02–06:15 UTC에 남은 Write 17건은 모두 `toolDenialKind=automode-unavailable`, `is_error=true`였다. 같은 세션의 기본 worktree에는 실행 전 거절된 타입 검사 Bash 1건도 남았다. 파일이 나중에 정상 작성됐다는 사실과 별개로, 이 원래 호출들은 실행 전에 거절됐다.

Claude 2.1.285는 실행 전 auto-mode 거절을 `PermissionDenied` 이벤트로 통지한다. 기존 adapter는 `PostToolUse`/`PostToolUseFailure`만 연결해 이 종료를 놓쳤다. 중앙이 PreTool에서 만든 예약이 남으므로 formatter의 `assert_idle` 차단은 상태에 맞는 동작이었다. 이번 결함은 Prettier 실행 실패나 사용자의 강제 종료가 아니라 **native 거절 이벤트 누락**이다. [공식 이벤트 계약](https://code.claude.com/docs/en/hooks#permissiondenied).

반영: `PermissionDenied → write-denied` 연결, 원본 예약·거절 근거 receipt 보존, 해당 call의 예약만 종료, 최신 성공 저장과 다른 주체의 writer 보존. 실패한 호출의 파일을 성공·포맷 완료로 기록하지 않으며, 거절된 동작의 자동 재승인·재실행을 요청하지 않는다. 단순 실행 실패는 부분 변경 가능성이 있어 이 경로를 사용하지 않는다.

중앙 `writes --project ... --assignment ...`는 기록 ID·경로·거절 확인 여부를 출력한다. `--reconcile-denied`는 원래 Claude 대화의 session·source assistant UUID·call·명시적 classifier 거절·파일 경로를 대조해 과거 예약만 복구한다. 대화 원본이 없거나 중복·불일치하거나 일반 도구 실패면 예약을 유지한다. 쓰기 전후 코드 변경을 추정해서 지우지 않는다. 복구 receipt는 `branch-relations/v1/write-receipts/`에 남긴다.

회귀 범위: 거절 이벤트 후 정상 포맷, 후속 성공 저장 보존, 다른 미확인 호출 유지, 역순 거절의 writer 복원, native 근거 불일치·symlink 거부, 셸 검증 예약 복구, inject hook 등록. 기존 bundle 파일은 수정하지 않는다. 신규 이벤트 처리는 새 inject부터 적용하며 과거 state 복구는 별도다. orchestration의 주체 분리는 여전히 후속 범위다.

실제 복구 결과: 18건(판매자 worktree Write 17 + 기본 worktree 타입 검사 Bash 1)을 원본 거절 근거로 종료했다. 복구 직후 해당 assignment의 writes는 0건이고 정상 저장 receipt 89개는 현재 파일 SHA·writer와 모두 일치했다. 원래 세션 bundle의 명시적 포맷 트리거로 89개 파일 처리, `npm run lint`, `npm run build`, 마지막 `formatting.py check` 모두 통과했다. 빌드의 tsconfig-paths 안내와 chunk 크기 경고는 남아 있다. 실행 결과는 중앙 `state/recovery-runs/ec-seller-format-20260930.json`, 개별 거절 근거는 `write-receipts`에 보존했다. 원래 handoff의 포맷 미완료 기록은 당시의 이력이므로 덮어쓰지 않았다.

함께 인계된 [TrendBadge](../policy/common/skills/reference/components/trend-badge/SKILL.md), [lucide-react](../policy/common/skills/reference/libraries/lucide-react/SKILL.md), [HeroUI](../policy/common/skills/reference/libraries/heroui/SKILL.md) 초안은 실제 코드·lockfile·설치본과 대조해 중앙에 등록했다. HeroUI는 선언 `^3.2.3`과 실제 `3.2.4`를 구분했고, TrendBadge에 direction prop이 없고 null 처리는 호출부 책임임을 명시했다. 등록 당시 TrendBadge·line-icons는 판매자 브랜치의 미커밋 자산이었다. 2026-10-02 판매자 커밋 `b6fc92d2eed80a4920cc4681bda7f44a3565a8f5`에 포함된 것을 재확인해 스킬을 갱신했다. 기본 관리자 브랜치의 가용 자산으로 단정하지 않는다. 별도 overlay나 감사 예외 없이 공통 reference에 관리자·작업 브랜치 한정 확인 범위를 적고, 기존 KpiCard 안내에서도 실제 슬롯 존재를 확인하게 했다. 세션 초안의 당시 미등록 표시는 이력으로 유지하며 중앙 정본과 카탈로그를 새 inject 세션에서 사용한다.

최종 검증: 기본 unittest discovery와 같은 388개를 24개 파일별 subprocess로 실행했다. 초기 실행에서 공통 reference 하위 문서를 모두 관리자 overlay로 간주하던 렌더링 테스트 1건이 실패했다. 실제 overlay 원본 목록을 확인하도록 수정한 뒤 렌더링 24개를 재검증했고, 마지막 변경이 있는 거절·조회·포맷 검사 2개도 재검증해 모두 통과했다. 중앙 contract와 두 프로젝트 audit, diff 공백 검사도 통과했다. 결과 집계는 `state/recovery-runs/ec-seller-policy-verification-20260930.json`에 남겼다. 아래 기존 381개 검증 기록은 이전 보강의 이력이다.

## 2. 계획 해시: 세션 폐쇄가 아니라 승인 범위 변경 감지

도입 이력: `e60ade9`의 [당시 개선 보고 F04·F05](runtime-remediation-2026-09-08.md)는 compact·resume·질문에는 승인을 유지하고 task·role·계약·계획 변경에 재승인을 요구했다. 계획 전체 바이트를 선택하거나 진행 표시까지 승인을 해제해야 한다는 별도 요구는 확인하지 못했다. `3184d3b`의 [V4 전환](shared-git-access-2026-09-10.md)은 branch/worktree 소유권을 없애되 계획 비교와 다른 worktree에 로그를 쓰는 경우의 기존 계획 fallback을 유지했다.

이번 [계획 템플릿](../policy/common/templates/plan.template.md)은 다음으로 나뉜다.

| 해시 포함: 승인 영역 | 해시 제외: 진행 기록 |
| --- | --- |
| 목표, 작업 유형, 대상 repository·branch·worktree | 단계 진행·완료 상태 |
| 포함·제외 범위, 역할 책임·선택한 스킬 | 실제 실행 명령·검증 결과·근거 |
| UI 자산 선정 계획, 변경할 UI/controller·DTO 계약 | 스킬 등록 상태, 질문 답변 원문 |
| 제약, 검증·완료 기준, 합의한 위험·결정 | 장애, 인계, 승인 상태 표시 |

`asan-plan:approval:start:v1`과 `asan-plan:approval:end:v1` 사이를 추출하고 줄바꿈·줄 끝 공백을 정규화해 SHA-256을 계산한다. 기존 표식 없는 문서는 기존 전체 파일 해시를 유지한다. 새 형식으로 옮길 때는 비교 대상이 바뀌므로 한 번 재승인이 필요하다.

[approval_policy.py](../policy/guards/approval_policy.py)의 `plan_fingerprint`, `load_harness_state`, `implementation_gate_denial`이 실제 구현이다. 승인 영역이 바뀌면 다음 source 변경의 구현 승인만 해제된다. **같은 세션에서 변경분을 보고하고 재승인받아 계속한다.** 읽기·자기 계획 수정은 가능하다. plan이 없을 때 받은 Proceed를 이후 새로 작성한 계획의 승인으로 재사용하지 못한다.

진행 영역에 새로운 범위·계약을 적어서 승인 영역 변경을 피하면 안 된다. hook은 그 문장의 의미를 분류하지 못하므로 에이전트와 Watcher가 승인 범위와 실제 diff를 대조한다. 계획 파일 존재는 작업 범위의 경로별 ACL이 아니다.

## 3. 세션·worktree별 준비와 인계

세 준비 기록은 문서 세 개가 아니라 다음 이벤트 상태다.

1. `implementation_approved`: 현재 계획에 대한 구현 승인.
2. `skill_confirmed`: 성공한 스킬 호출 또는 허용된 SKILL.md 읽기.
3. `exploration_completed` 또는 UI 역할의 `ui_exploration_completed`: 대상 경로를 성공적으로 탐색한 근거.

V4의 일반 프로젝트 파일에 대한 구조화된 변경 전에 이 기록과 plan 존재를 확인한다. 자기 세션 산출물 작성과 읽기 조사, 기존 변경의 Git 작업만 맡은 산출물 예외는 별도다. 일반 프로젝트 문서도 source gate 대상이 될 수 있으므로 “source 변경”이 TS/TSX만 뜻하지는 않는다.

**다른 세션 → 같은 worktree:** 각 세션은 자기 계획·승인·준비를 갖는다. 다른 세션의 plan이 존재해도 자기 계획과 준비를 만들 수 있다. 다른 사람의 계획을 수정하거나 승인·스킬 확인 상태를 자동 승계하지 않는다. 같은 host·role이어도 같다. 세션 산출물 경로는 `.<host>/logs/sessions/<이름>/`이며 worktree마다 하나뿐인 plan이 아니다.

**같은 세션 → 다른 worktree:** 계획·구현 승인은 assignment에 연결하고, 성공한 스킬·탐색은 `readiness-worktree-<경로 해시>.json`에 따로 기록한다. [approval_policy.py](../policy/guards/approval_policy.py)의 `load_preparation`·`record_preparation`과 [shared_git.py](../policy/guards/shared_git.py)의 변경 대상별 gate가 검사한다.

- 읽기·참고 목적의 다른 worktree 접근은 현재 준비 상태를 바꾸지 않는다.
- 첫 source 쓰기 전에 대상 common directory·실제 worktree·역할·계획 승인 영역을 확인한다. 여러 worktree를 한 patch로 고치면 각각 확인한다.
- 대상 worktree의 준비 근거를 별도로 기록하고, 해당 코드·인접 자산·적용 스킬을 다시 확인한다. 이전 탐색을 무조건 완료 상태로 복사하지 않는다.
- 기존 계획이 새 대상과 같은 작업을 명시하면 링크로 재사용할 수 있다. 새 요구·계약이면 승인 영역을 수정한다. worktree가 다르다는 이유만으로 새 세션을 강제하지 않는다.
- branch·HEAD·역할이 달라지면 그 worktree의 스킬·탐색을 다시 확인한다. 스킬 읽기의 shell workdir와 소스 탐색의 실제 경로를 사용한다. 기존 assignment 전체의 준비 flag는 새 worktree 기록으로 복사하지 않는다.
- 미커밋 코드·설정의 모든 내용 변경을 준비 해시에 넣지는 않는다. 매 편집마다 준비가 해제되는 구조를 피하고 변경 영향·스킬 적합성은 리뷰한다. 계획 승인 영역 변경은 별도 승인 해시로 잡는다.

handoff는 host 내부 대화 복제에 의존하지 않는 공통 전달 문서로 사용한다. 수신자는 출처, 실제 HEAD·diff, 맡을 작업과 보존할 UI를 자기 계획에 기록한다. Claude UI → Codex Logic 인계는 UI 수정 권한까지 넘기지 않는다. Logic 선행은 UI가 controller 계약에 맞추고, UI 선행은 controller가 UI 계약에 맞춘다. 후자는 DTO/controller와 UI 항목이 맞지 않으면 사용자의 결정을 받는다.

현재 role gate는 Logic의 JSX/CSS 변경을 경로별로 막지는 않는다. 역할 문서와 리뷰가 지켜야 할 경계다. UI 자산 문서는 사용자가 “내용이 남아 있으면 생성”으로 확정했으므로 `unknown/ui-asset-plan.md` 지침을 유지한다. 별도 문서의 존재·항목 대응을 자동 검증하는 기능까지 이번 plan 존재 검사에 포함됐다고 설명하지 않는다.

## Claude orchestration: 문서상 역할과 실제 실행 주체

현재 설치 버전은 Codex CLI 0.157.1, Claude Code 2.1.285다. 실제 native orchestration을 실행한 검증은 하지 않았다. 아래는 중앙 코드와 공식 이벤트 계약의 대조 결과다.

**판정: 세션 정책을 에이전트 정책으로 이름만 바꾸어 적용할 수 없다.** 정책의 판단 원칙은 재사용할 수 있지만 동일 세션의 자식들은 승인·산출물·포맷 작성자 등의 주체를 공유한다. 이번 세션 보강 이후에도 이 결론은 같다. 에이전트 구현은 후속으로 미루고 아래 변경·검증 조건만 유지한다.

| 평가 항목 | 실제 현재 구현 | 판단 |
| --- | --- | --- |
| 역할·평가 항목 | agent-output-schema의 planner/publisher/generator/refactorer/watcher/evaluator 필드, 역할 reference, native agent 정의 | 문서상 평가 기준은 있음 |
| 주체 식별 | runtime_state.session_path/owner_id는 assignment, 없으면 host+session 사용 | 같은 session의 agent_id를 구분하지 않음 |
| 준비·계획·산출물 | 준비는 assignment 안의 worktree별, 계획·산출물 binding은 assignment별 | 같은 worktree의 다른 agent는 여전히 준비를 공유하며 agent별 출처 보장 없음 |
| Git 승인 재개 | host·native session·assignment·operation·철회 세대 | agent_id가 없으므로 부모·형제의 동의를 독립된 권한으로 분리하지 못함 |
| 쓰기·포맷 기록 | 주체는 assignment, 호출은 call ID로 구분 | 도구 호출은 나뉘지만 에이전트 간 역할 경계·동시 파일 편집 격리는 아님 |
| 역할 차단 | 부모 실행 환경의 ASAN_AGENT_POLICY_ROLE | 자식 역할로 자동 전환되지 않음 |
| 주입된 agent | orchest에는 planner만, generate에는 publisher/generator/refactorer/watcher | orchest 한 세션의 완전한 구현 파이프라인으로 볼 수 없음 |
| 종료 처리 | SessionStart/PreTool/PostTool/Stop, SubagentStart/SubagentStop 미등록 | 이번 Stop 포맷을 자식 종료별 검증으로 확대 해석하면 안 됨 |
| 검토 결과 | schema·Watcher 지침은 있음, runtime에서 각 agent 보고 schema/PASS를 강제한 근거 없음 | agent 평가의 내용 지침과 실행 gate를 분리해야 함 |

근거: [runtime_state.py](../policy/guards/runtime_state.py), [shared_git.py](../policy/guards/shared_git.py), [역할 bundle 구성](../lib/agent_policy/role_profiles.py), [Claude 이벤트](../adapters/claude/events.json), [agent 출력 스키마](../policy/common/templates/agent-output-schema.yaml).

수정 전 임시 hook 입력 재현에서는 agent A의 Skill, agent B의 Read, root의 Proceed 뒤 agent C의 다른 worktree Edit가 허용됐다. 이번 보강으로 **다른 worktree의 미준비 쓰기**는 차단한다. 그러나 같은 worktree에서 agent A/B/C가 근거를 공유하는 문제는 `session_path/owner_id`에 agent_id가 없어서 남는다. native Watcher 도구 제한을 우회했다는 실험은 아니며, 실제 에이전트를 실행하거나 소비자 소스를 편집하지 않았다.

Claude의 하위 에이전트 도구 호출에는 `agent_id`와 `agent_type`을 제공하며 SubagentStart/Stop도 있다. 따라서 중앙에서 구분할 기반은 있다. 다만 플러그인 agent의 hooks/permissionMode 설정에는 제약이 있어 agent 문서에 필드를 추가하는 것만으로 권한 격리를 구현했다고 볼 수 없다. [Claude hook 공식 문서](https://code.claude.com/docs/en/hooks), [subagent 공식 문서](https://code.claude.com/docs/en/sub-agents).

후속 설계는 `assignment → agent actor → worktree 준비` 구조다. root의 승인 영역을 복사 승인하지 않고 각 자식에게 명시적으로 위임한 부분을 연결한다. 시작 이벤트의 신뢰된 agent_id/type과 부모 관계, 기여 범위, 역할 capability를 함께 기록한다. 하위 agent의 자기 승인·범위 확대를 금지한다. Watcher는 구현 쓰기를 못 하고 검토 산출물만 작성하며, publisher/generator/refactorer의 출력·검증 근거를 agent 단위로 연결한다. root의 공유 plan 변경과 최종 보고는 root가 맡고 자식 기여 기록은 구분한다.

| 정책 | 전환 시 유지할 판단 | 에이전트 도입 전 필요한 변경·수용 검사 |
| --- | --- | --- |
| 계획·승인 | 승인 영역 해시, 진행 갱신 제외, 동일 범위의 반복 질문 방지 | 부모 승인과 자식의 위임 범위 연결; 형제의 승인·계획 변경을 자동 승계하지 않는지 검사 |
| 스킬·탐색·UI 자산 | 항목별 자산 선택, 스킬 적합성·재사용 근거, worktree별 준비 | agent별 증거와 공통 조사 인용을 구분; 공유 자료를 읽었다고 독립 준비·평가가 생기지 않는지 검사 |
| UI/controller·DTO | 선행 계약 제공자에 따라 맞추는 방향 결정, UI 선행 불일치는 사용자 질문 | publisher→generator/refactorer 인계에서 계약 버전·불일치·답변 추적; 에이전트가 임의로 계약을 확대하지 못하도록 검사 |
| 역할·산출물 | 구현 책임, 다른 주체의 기록 보호, 중앙 아카이브 | agent type→capability, 기여 기록 경로·작성자, root plan 병합 책임; watcher/evaluator의 source 쓰기 거부 검사 |
| 쓰기·포맷 | 호출 ID·실제 결과·최종 내용 확인, 미확인 상태 보존 | owner에 agent 주체 연결; 형제 agent의 같은 내용 저장·부분 실패·동시 포맷·Git·취소를 섞어 검사 |
| Git·병합 | 동일 변경 승인, 직접 부모, 현재 snapshot, 기준 branch 영향 검토 | Git 담당 agent에 제한된 위임; 부모/형제 ticket 차용 거부, 취소 전파, 부분 실행 반복 방지 검사 |
| 완료·검토 | 검증 근거로 완료, Watcher 현재 판정과 Evaluator 장기 권고 분리 | SubagentStop/최상위 Stop 순서, 누락·중복·background 이벤트; 실제 diff와 연결된 출력 schema·PASS 검사 |
| 재개·호환성 | 미확인 결과를 추정하지 않고 동일 승인 범위 재검사 | agent 재시작·부모 종료·handoff에서 주체 재연결; agent 정보 없는 기존 host의 세션 회귀 유지 |

현재 schema에는 각 역할의 평가 필드가 있지만 runtime이 에이전트별 보고와 실제 diff·검증을 결합해 PASS를 강제하지는 않는다. 후속 작업은 먼저 별도 임시 저장소에서 위 검사를 실패 사례부터 만들고, 실제 Claude 이벤트 계약에 맞춘 native smoke 검증까지 수행해야 한다. 현재 세션용 회귀 통과를 이 검증의 대체로 쓰지 않는다.

## 4·6. 공유 접근과 실제 쓰기 권한, 구조화된 도구

중앙 V4는 같은 Git common directory를 공유하는 linked worktree 접근을 허용한다. remote가 같은 다른 clone은 다른 프로젝트다. HEAD 변경 자체가 세션 접근을 막지는 않지만 이미 승인한 Git operation의 HEAD가 달라지면 재검토 대상이다. 동적 wrapper·실행 위치가 모호한 Git 옵션은 경로 판정을 못 하므로 차단한다.

호스트 sandbox는 별도다. 예를 들어 기본 checkout만 writable인 세션은 중앙 hook이 형제 linked worktree를 허용해도 OS/호스트가 그곳의 쓰기를 거부할 수 있다. 이번 [launcher](../lib/agent_policy/injection.py)의 `_additional_workspaces`·`_host_command`는 Codex·Claude의 로컬 CLI help에서 확인한 `--add-dir`로 등록된 실제 linked worktree와 존재하는 프로젝트 설정의 `worktree_root`를 전달한다. 전체 사용자 홈·중앙 state·다른 프로젝트의 상위 폴더는 추가하지 않는다. 생성 루트 안의 작업도 중앙 same-repository 검사와 Git 승인은 계속 적용한다.

`--resume-assignment`는 현재 등록 worktree 경로를 다시 계산하면서 원래 assignment·native session·bundle을 유지한다. 실행 도중 생성 루트 밖에 새 worktree가 생기면 호스트의 경로 추가 또는 launcher 재개가 필요할 수 있다. 존재하지 않는 생성 루트를 임의 생성하거나 관리자 sandbox·명시적 deny를 해제하지 않는다. OpenCode는 `--add-dir`를 가정하지 않고 기존 native 외부 경로 승인 동작을 유지한다. `external_directory`를 allow로 덮어써 개인의 deny 설정을 완화하지 않았다. [OpenCode 권한 문서](https://opencode.ai/docs/permissions/).

“일치시키기”는 사용자 요청 대상의 실제 worktree 경로를 호스트의 승인된 쓰기 범위에도 반영하고 도구 cwd를 정확히 전달하자는 뜻이다. 모든 디렉터리를 무제한 writable로 만드는 것이 아니다. 같은 worktree 안의 checkout과 형제 디렉터리로 이동하는 worktree 작업도 구분한다.

Edit/Write/apply_patch는 대상 파일 경로와 변경 내용을 도구 입력에 담는다. hook은 이 입력과 host·session·call ID로 보호 경로·산출물 출처·포맷 대상을 검사한다. 이 도구도 파일을 직접 수정한다. `>`/ `>>`는 shell 출력의 덮어쓰기/추가 연산자이고 대상이나 효과의 정적 판정이 어려운 쓰기는 구조화된 도구로 요청하도록 한다. 도구 자체가 승인·사람의 서명을 제공하지는 않는다.

관련 실제 기록은 [inquiry-controllers](../logs/projects/admin-ui/codex/sessions/inquiry-controllers/handoff.md)의 linked worktree sandbox·mkdir/patch 차단, [maintenance-api](../logs/projects/admin-ui/codex/sessions/maintenance-api/final-summary.md)의 완료된 npm ci 위치 불일치, [event-reward-object-name](../logs/projects/admin-ui/codex/sessions/event-reward-object-name/plan.md)의 hook workdir 누락, [citizen-proposal-vote-connection](../logs/projects/admin-ui/codex/sessions/citizen-proposal-vote-connection/final-summary.md)의 정리 잔여 디렉터리 차단이다. 모든 사례를 같은 apply_patch 실패로 묶지 않는다.

## 7·8. 실행 예약과 병렬 쓰기

| 구분 | 목적 | 다른 세션의 처리 |
| --- | --- | --- |
| 도구 쓰기 기록 | 해당 호출의 성공/실패/미확인 결과 추적 | 다른 주체가 결과를 성공으로 간주하거나 가져다 쓰지 않음 |
| Git grant | 승인한 특정 operation을 현재 host/assignment에서 실행 | 다른 세션은 자기 주체와 현재 실제 변경을 근거로 Git 승인을 받음 |
| plan 승인 해시 | 구현 목표·범위·계약 변경 감지 | 다른 세션의 구현 승인으로 자동 전환되지 않음 |

A의 쓰기 기록이 남았다고 A만 반납할 수 있는 것은 아니다. 정상 PostTool 결과로 종료하거나, 종료 근거를 확인하고 승인된 `write-recovery`로 복구한다. B가 A의 실행 중 호출을 인수하거나 성공을 추정해서는 안 된다. 실제 실행 중이면 끝날 때까지 기다려야 한다.

일반 코드 쓰기는 B도 자기 계획·역할·준비·승인을 갖추면 같은 worktree에서 할 수 있다. **현재 reserve_write는 일반 소스 쓰기끼리의 상호 배제 잠금이 아니다.** A가 apply_patch 중이라는 이유만으로 B의 apply_patch를 모두 차단하지 않는다. Git·포맷·정리 단계의 assert_idle 등은 미확인 쓰기를 차단한다. 파일 범위 분리 또는 별도 worktree가 여전히 필요하다.

“실행 결과 미확인”은 현재 실행 중이라는 뜻일 수도 있고, 이미 종료됐지만 callback/해석이 누락됐다는 뜻일 수도 있다. 별도의 사람 서명을 매 편집 후 받지 않는다. 정상 도구 결과 이벤트로 종료 기록을 처리한다.

예: patch가 `const pageSize = 10`을 찾는데 실제 파일에는 15가 있으면 적용이 실패한다. 여러 파일 중 일부를 쓴 뒤 새 디렉터리 생성이 sandbox에서 실패할 수도 있다. 정상 결과가 전달되면 실패로 처리하고, 일부 변경 또는 결과 누락이면 내용 확인이 필요하다. 강제 종료·OS 오류에만 한정되지 않는다. 도구 호출 완료와 사용자 요청 전체 완료는 별개의 시점이다.

추가 보강 과제는 host 완료/실패 이벤트와 cwd 연결, 종료 증거를 바탕으로 한 복구, 필요 시 파일 버전 비교·상호 배제다. 시간 경과만으로 종료를 확정하거나 부분 변경을 자동 되돌리지 않는다.

## EC 구매자 포맷 차단: 원인·현재 상태·수정

원본 인계 문서는 `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-user-ui-worktree/ec-buyer-ui/.codex/logs/sessions/ec-buyer-logic/handoff.md`다. 9월 30일 최신 기록은 **같은 세션에서 정상 저장 후 포맷·lint·대상 테스트 59개·build·diff 검사를 완료하고 55194e6으로 commit, clean**이라고 보고하며 “새 세션에서만 해결”이라는 이전 안내를 정정한다. 이번 중앙 작업에서 소비자 검증을 재실행하거나 해당 commit을 만든 것은 아니다.

과거 실패 call `exec-eddc9579-5267-4562-a18e-bb76a4f95850`의 쓰기 복구는 완료됐지만 포맷 calls 기록은 남았다. 기존 unconfirmed_calls는 후속 정상 저장 token이 현재 global writer와 같을 때만 옛 기록을 잠시 무시했다. 다른 UI assignment가 같은 EcRoutes.tsx를 수정해 writer가 바뀌면 이전 오류가 다시 나타났다. 동일 path가 중복 등록돼 오류에도 두 번 출력됐다.

이번 [formatting.py](../policy/guards/formatting.py)는 원래 호출의 활성 쓰기 부재와 같은 주체의 후속 정상 저장·writer 근거가 모두 확인되면 대체 call/token/hash를 옛 기록에 영구 보존한다. 다른 주체의 수정만으로 미확인을 해소하지 않는다. 중복 target은 token 생성 전에 합치고 과거 중복 진단도 한 번 표시한다. [event_protocol.py](../policy/guards/event_protocol.py)는 apply_patch의 명시적인 검증 실패를 실패로 인식한다. 부분 변경이 있으면 여전히 unconfirmed다.

기존 Stop은 **포맷 필요 여부만 검사**했다. 이번 [managed_policy_guard.py](../policy/guards/managed_policy_guard.py)는 Stop/idle에서 성공이 확인된 자기 변경을 실제 Prettier에 전달한다. events lock 밖에서 계산하고 다시 잠근 뒤 내용·작성자·HEAD·설정·staged·진행 중 쓰기를 재확인한다. host timeout도 맞췄다. 첫 Stop 실패는 차단 사유를 알리고, 반복 Stop은 미완료 안내로 종료 순환을 막는다. 심볼릭 링크 등 검사 자체의 예외도 반복 Stop에서 다시 종료를 막지 않으며 파일 보호는 유지한다. OpenCode idle은 오류를 알림으로 표시한다. 포맷 성공이 test/build 성공을 의미하지 않는다. SubagentStop은 아직 이 경로에 연결되지 않았다.

재현 테스트는 “미확인 호출 → 종료 복구 → 정상 저장·포맷 → 다른 세션 수정·commit → 원래 세션의 새 MSW 파일 포맷”을 포함한다. 단순히 pending 상태를 전부 지우거나 다른 작성자의 파일을 덮어쓰는 해결은 하지 않는다.

## 9. 병합 검토·사용자 선택·기준 branch 동기화

[integration_review.py](../policy/guards/integration_review.py)는 실제 Git 상태·관계·diff·텍스트 병합 미리보기를 수집한다. 에이전트는 여기에 계약 위험·검증·미확인 범위를 작성한다. complete와 execute는 보고가 참조한 snapshot이 현재 실제 상태와 같은지 다시 확인한다. “문서 문장과 코드의 의미를 자동 비교”하는 구현은 아니다.

계약 위험은 타입·props·상태·UI/controller·API 요청/응답 호환성이고, 검증은 텍스트 충돌만이 아니라 필요한 lint·test·build와 동작 확인이다. 미확인 사항은 미커밋 파일 외에도 수행하지 못한 테스트·실환경 API 등까지 포함한다. 보고된 의미적 위험은 사용자가 이해하고 승인할 수 있지만 직접 부모·미처리 자식·dirty·현재 snapshot 불일치·미해결 충돌·미확인 쓰기 같은 실행 조건은 승인 한 번으로 해제되지 않는다.

차단 보고는 원인, 기대값/현재값, 실제 실행 단계, 가능한 선택을 제공해야 한다. 이번 runtime은 검토 후 바뀐 branch별 이전/현재 HEAD와 commit 간 변경 파일, worktree/관계 변동을 출력하고 **새 검토 후 승인 또는 보류**를 안내한다. 에이전트는 그 commit과 관련 계약을 읽어 영향을 설명한다. assignment/grant/sandbox 오류는 중앙 복구가 필요한 별도 문제로 표시한다. 병합 뒤 검증만 실패했다면 “병합 미실행”이라고 보고하지 않는다.

`sy-main`을 작업 branch로 가져오기 전에는 현재 HEAD에 없는 commit과 공용 의존 관계를 조사한다. 가져오지 않을 때 작업의 구현·계약·검증에 영향이 없으면 merge를 시도하지 않는다. 영향이 있으면 필요한 변경과 병합 순서를 보고·승인받는다. 관련성을 모르면 조사 또는 보류를 선택하게 한다. 이 절차는 [Git 스킬](../policy/common/skills/policy/git-branch-strategy/SKILL.md)에 반영했다. **완료 병합의 직접 부모 검사는 유지한다.**

## 10. Git 승인 재개 결함은 세션 강제 종료 때문인가

조사한 inquiry-controller-completion operation `c18ac37c5b7fd609a4ad94d6a508c658`은 prepared 상태, Git 결과 없음, 승인/준비/재계산 fingerprint 동일이었다. 오래된 handoff patch 예약 복구 후에도 재승인을 요구했다. 파일·범위 변경이 확인된 사례가 아니다.

수정 전 [git_operations.py](../policy/guards/git_operations.py)의 _execute는 grant를 지운 뒤 validate·assert_idle을 검사했다. 따라서 사용자가 세션을 닫지 않아도, 미확인 쓰기를 발견해 **Git 실행 전에 정상적으로 예외가 발생하는 것만으로** 실행 예약이 소모됐다. 이어서 shared_git의 PreTool은 저장된 authorized를 재개 근거로 사용하지 않았다.

이번에는 지속 동의와 호출 ticket을 분리했다. 실제 runner 진입에서 host·native session·assignment·fingerprint·철회 세대를 저장하고, `resumable`은 **일반 Git·prepared·결과 없음·동일 주체·동일 변경·미철회**일 때만 새 ticket 발급을 허용한다. Claude의 native 승인 요청 전에 생긴 grant만으로 동의가 성립하지 않는다. 실행기 안에서 ticket의 철회 세대도 다시 검사한다. 취소 후 새 승인은 가능하다.

검증된 Claude 재시도는 `hookSpecificOutput.permissionDecision: allow`를 반환한다. 일반 안내만으로 native 권한 질문을 제거했다고 간주하지 않는다. 호스트의 명시적 deny·ask 규칙은 계속 평가되므로 해당 규칙에서 막히면 별도 원인으로 보고한다. 재시도 전 실패 이유는 `previous_failure`로 보존하며 성공한 실행에 현재 차단 이유가 남지 않게 한다. [Claude PreToolUse 계약](https://code.claude.com/docs/en/hooks#pretooluse-decision-control).

다른 세션 또는 주체 필드가 없는 과거 authorized 기록은 자동 승계하지 않는다. `executing` 이후이거나 부분 실행이면 stage와 `show` 안내를 보고 결과부터 대조한다. 완료 병합은 기존 recover 경로를 유지하며 일반 Git 재시도 로직으로 전체 merge를 반복하지 않는다. 실제 과거 operation의 state를 고치거나 다시 실행하지 않았다.

## inquiry-ui 삭제 관계와 로그 수집

조사 당시 실제 `feature/inquiry-ui` ref와 linked worktree는 없고, 중앙 graph UUID `9de70896d3924c1bbd43955a9c395c76`도 이미 `deleted: true`였다. resolution은 merged, verification은 passed, 완료 operation은 `c50cbcead1a843d4bc88c7baa7016403`이다. 인용한 “삭제되지 않음으로 남을 수 있음”은 현재 상태와 일치하지 않는다. 추가 retire 또는 중앙 JSON 편집은 수행하지 않았다.

일반 절차에는 ref·worktree·graph를 함께 확인하도록 보강했다. 활성 기록만 남고 ref가 사라졌다면 완료/취소 근거와 미처리 자식 부재를 확인해 정식 retire를 준비·승인·실행한다. 같은 이름의 새 branch는 새 UUID이며 과거 작업에 묶지 않는다. 포맷 문제와 별개의 branch lifecycle 확인 항목이다.

[log_mirror.py](../lib/agent_policy/log_mirror.py)는 assignment에 연결된 원본 세션 문서를 Stop/idle·완료 workflow 시 중앙에 추가·갱신한다. 모든 worktree/branch 파일을 저장 즉시 복사하는 기능이 아니다. 중앙 사본을 자동 삭제·stage·commit하지 않는다. agent별 기록 아카이브는 향후 agent binding 설계와 함께 검증해야 한다.

## 검증과 적용

실패 재현 후 수정한 회귀 검사: 진행 문구 변경의 승인 해제, plan 없이 source 허용, 잘못된 승인 표식, 계획 생성 전 승인 재사용, 복구 호출의 재발, 중복 patch 대상, Stop 포맷 미실행, 오래된 병합 검토의 불명확한 진단, Git 미실행 차단 후 재승인 요구, Claude 재시도의 native 허용 응답 누락, worktree 준비 공유, launcher 추가 경로 누락. 임시 저장소와 현재 renderer를 사용한다.

- 전체 unittest: **381/381 통과**, 실패 없음. 동일 discovery 집합을 23개 파일별로 4개 프로세스에 분배해 검증했다(967.873초). 각 실행은 `python3 -B -m unittest discover -s tests -p <test 파일명> -v`이며 전체 수집 건수와 합계가 일치한다. 테스트 프로세스 분산이며 orchestration agent 실행이 아니다.
- 포맷 25개, 계획 승인 5개, Git 관계 40개, 공유 접근 32개를 유지하고 Git 승인 재개 5개·worktree 준비 3개·launcher 경로·동일 세션 재개 검사를 추가했다. 구현 승인 유지와 대상별 준비 갱신을 구분하도록 기존 fixture의 탐색 위치를 맞췄다. 다중 worktree patch, 다른 주체·철회·부분 실행·변경된 Git 대상의 거부도 검사한다.
- 중앙 audit: central-contract/admin-ui/user-ui PASS. `git diff --check`와 이 문서의 로컬 근거 링크 23개도 확인했다.
- 호스트 추가 경로는 설치된 CLI 계약·실제 생성 인자·재개 명령을 검증했다. 실제 사용자 호스트 세션에서 sandbox 쓰기를 실행하거나 native orchestration을 구동한 결과로 확대하지 않는다.
- 소비자 코드·실행 중 bundle·실제 assignment 상태와 소비자 Git 이력은 수정하지 않았다. 중앙 정책 변경의 작업 단위 커밋은 후속 사용자 요청에 따라 별도로 수행한다.
- 새 정책은 중앙 변경 검토 후 새 inject 세션에서 적용한다. 기존 세션 재시작이 포맷 오류의 유일한 해결책이라는 뜻은 아니다.
