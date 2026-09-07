# 계획

## 목표

Codex에서 관찰된 SessionStart JSON 오류, deprecated feature 경고, 읽기 전용 Git 조회 차단, 산출물 쓰기 교착과 Stop hook 무한 재개를 중앙 정책에서 수정한다. 이전 작업에서 도입한 V3 자손 branch 권한 상속과 함께 동작하도록 회귀 검증한다.

## 작업 유형

- hybrid

## 범위

- 공통 system prompt와 운영 문서
- Codex·Claude·OpenCode adapter의 lifecycle hook 등록
- 공통 guard의 SessionStart 출력, 승인 문구, Git 조회 분류, 산출물 lifecycle
- Codex agent TOML schema
- 단위·렌더·감사 테스트

## 제외 사항

- 소비자 저장소에 대한 `sync`
- 소비자 애플리케이션 소스 변경
- 사용자 전역 `~/.codex/config.toml` 수정
- 별도 승인이 필요한 main 병합과 배포

## 제약 조건

- 중앙 원본과 테스트만 변경한다.
- 일반 대화 종료에서는 산출물 완성을 강제하지 않고 명시적 완료 lifecycle에서만 검증한다.
- 알 수 없는 Git 명령은 fail-closed하되 검증된 조회 명령은 승인 없이 허용한다.

## 스킬 및 역할

- 제안 역할: 정책 구현 및 검토
- 역할 판단 근거: Codex lifecycle hook과 중앙 런타임 guard 수정
- 사용자 역할 확인: `작업 시작해`를 앞서 제시한 수정안에 대한 구현 승인으로 사용
- Git 통합 담당자: 현재 Codex 세션, main 병합·sync는 별도 승인
- 산출물 책임: owner

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 공식 계약 확인 | 정책 조사 | openai-docs | Codex hook JSON과 feature key 기준 확정 |
| guard·adapter 수정 | 구현 | 기존 공통 guard 재사용 | 호스트별 중복 없이 차단 오류 수정 |
| 회귀 검증 | 검토 | 기존 unittest·audit | 문제별 자동화된 재현과 통과 근거 |

## 검증

- `python3 -m unittest discover -s tests -v`
- `bin/agent-policy audit`
- `bin/agent-policy diff --project all`
- `git diff --check main...HEAD`

## 위험 요소 및 결정 사항

- Stop hook이 `decision: block`을 반환하면 Codex가 자동 continuation을 생성하므로 산출물 강제를 Stop에서 제거한다.
- 소비자 diff가 누적 정책 전체를 포함하므로 sync는 구현과 분리해 승인받는다.
- 사용자 전역 설정의 deprecated key는 중앙 sync 대상이 아니다.

## 승인

- 상태: approved
- 근거: 사용자 메시지 `작업 시작해`
