---
name: project-ui
description: asan-metaverse-user-ui에서 Claude Code가 production UI를 계획·구현·리팩터링할 때 적용하는 프로젝트 진입 스킬입니다.
---

<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/hosts/claude/skills/project-ui/SKILL.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# Project UI

## 사용 조건

Claude Code가 `src/**/ui/**`, UI 전용 CSS·자산 또는 `src/shared/ui/**`를 작업할 때 사용한다.

## 필수 확인 순서

1. 루트 `CLAUDE.md`와 `AGENTS.md`
2. `DESIGN.md`
3. `.agents/skills/SKILL.md`
4. `.agents/skills/policy/SKILL.md`
5. `.agents/skills/reference/SKILL.md`
6. 대상 UI와 같은 디렉터리 및 인접 구현

작업에 필요한 세부 정책만 `.agents/skills/**`에서 추가로 읽는다. `.claude/skills/**`에 이전 프로젝트 자산을 다시 복제하지 않는다.

## 역할 경계

- Claude Code는 production UI, CSS, 접근성, 반응형 레이아웃과 props/callback 계약만 구현한다.
- hook, util, API, DTO, parser, validator, store와 도메인 상태 전이는 Hephaestus 작업으로 사용자에게 전달한다.
- 공용 통합 파일은 수정하지 않는다.
- 완료 시 `UI_COMPLETE` 형식으로 인계한다.

## 검증 제한

- 기존 테스트, `npm run build`, `npm run lint`만 사용한다.
- 리뷰 plugin/agent, 이미지 캡처, 화면 비교와 시각 QA를 실행하지 않는다.
