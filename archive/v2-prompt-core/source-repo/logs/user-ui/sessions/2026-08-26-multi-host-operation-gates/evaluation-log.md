# 평가 로그

## 현재 판정과의 경계

Watcher의 현재 변경 PASS를 다시 판단하지 않는다. 아래는 장기 운영 관찰과 후속 권고다.

## 장기 관찰 사항

- `Logic Session`은 Codex와 OpenCode 두 구현 호스트에 실제로 사용되므로 특정 제품명보다 안정적인 역할 이름이다.
- Claude의 전역 분석 역할과 UI 구현 역할을 분리하면 향후 기획 책임을 Claude로 옮겨도 파일 소유권을 다시 설계할 필요가 없다.
- 네 세션 동시 운용의 핵심 위험은 모델 수보다 동일 파일과 Git 상태 공유이며, 현재 사용자 중계·소유권·명령 승인 계약이 이를 제어한다.

## 목록에 등록할 재사용 가능 자산

- 보호 명령 분류와 Codex exact one-shot 승인 상태는 다른 프로젝트에도 재사용 가능한 중앙 guard 자산이다.
- OpenCode V1 권한 base와 effective config smoke는 OpenCode 소비 프로젝트 추가 시 재사용할 수 있다.

## 기술 부채

- OpenCode V1/V2 권한 스키마를 동시에 지원하지 않는다.
- Codex가 향후 `PreToolUse: ask`를 정식 지원하면 사용자 프롬프트 기반 상태 파일을 제거할 수 있다.
- 사용자별 overlay가 V1 범위 밖이라 OpenCode provider 또는 추가 권한 설정이 필요할 때 중앙 base를 직접 확장해야 한다.

## 프로세스 개선 사항

- OpenCode 업그레이드 전 `opencode --version`과 effective config smoke를 필수 호환성 게이트로 둔다.
- 소비 프로젝트 sync 전 legacy SHA mismatch 6건(프로젝트별 3건)의 처리 방향을 사용자가 별도로 결정해야 한다.
- 장시간 병렬 작업에서는 사용자 handoff에 수정 파일 목록과 pending Git/build/dev 명령을 포함하면 충돌 판단이 쉬워진다.

## 권고 사항

- 현재 V1은 그대로 유지하고 먼저 두 프로젝트에 중앙 정책을 안전하게 sync한다.
- Codex native `ask` 지원 여부는 버전 업그레이드 시 재확인하고 지원되면 공통 승인 UX를 단순화한다.
- 프로젝트별 차이가 필요해질 때만 overlay를 도입하고, OpenCode config 병합 요구를 그 시점의 근거로 삼는다.
