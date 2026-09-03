# 탐색

## 요청

기존 이력서·포트폴리오 기록에 OpenCode의 token 낭비 내역, compaction으로 유실된 사용자 prompt, 해당 세션의 오작동을 더 명확히 작성하고 향후 작성 정책·템플릿에도 같은 근거와 이번 사례 예시를 추가한다.

## 대상 관련 사실

- 기존 `portfolio-log.md`는 하네스 격차와 compaction 문제를 요약했지만 사용자 지시 원문, 시간순 compaction 변화, message·transcript·token·cache·child session 수를 포함하지 않았다.
- first admin session `ses_fed718db7ffeH34R6D3MMPOQ5X`는 1,614 messages, 5,477 transcript entries이며 사용량 집계는 입력 약 13,346,508 tokens, cache read 약 280,103,680 tokens, child session 188개다.
- second admin session `ses_fdda42f14ffex0tqSJNWSonin8`는 558 messages, 1,936 transcript entries이며 사용량 집계는 입력 약 4,487,734 tokens, cache read 약 98,748,160 tokens, child session 66개다.
- second session에서 14:15 UTC compaction은 UI·CSS·브라우저 목표를 보존했고, 14:21 UTC 사용자 중단 직후 14:21:01 UTC compaction도 같은 목표를 복원했다.
- 사용자는 반복 위반 때문에 불필요한 token 소비가 커지고 코드 수준이 떨어졌다고 직접 평가했다.

## 불러온 스킬

- `skill-index`: 관련 policy 범위 선택
- `policy-index`: 포트폴리오·문서화·하네스 정책 식별
- `policy-portfolio`: 문제→선택→적용→결과와 수치 근거 계약
- `policy-documentation`: 필수 8종 산출물과 현재 근거 제한
- `policy-harness`: 승인·Watcher gate
- `coding-agent-sessions`: OpenCode session 원본 근거 확인
- `git-master`: 공유 worktree 상태와 diff 검증

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| `src/shared/ui/` 25개 하위 UI 자산 | 사용하지 않음 | 문서·하네스 prompt만 변경하며 application UI를 수정하지 않음 |

## 제약 조건 및 미확인 사항

- token·cache 수치는 OpenCode main session 전체 총량이다.
- 브라우저·캡처·Oracle·재작업 경로만의 token 소비량은 분리 측정되지 않았다.
- user-ui OpenCode·Claude hard deny adapter 구현은 이번 범위가 아니다.
- `src/shared/ui/date-range-picker/date-range-picker.tsx`의 기존 변경은 다른 작업 소유이므로 수정하지 않는다.

## 결론

정확한 기록을 위해 기존 사례에 `세션·하네스 사고 근거`를 추가하고, root 정책·skill·schema·복사 템플릿에 동일 필드를 의무화한다. 현재 OpenCode 사례는 실제 값과 인과 한계를 함께 보여주는 예시로만 제공한다.
