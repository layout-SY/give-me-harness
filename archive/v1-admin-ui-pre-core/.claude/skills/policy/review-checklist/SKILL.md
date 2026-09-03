---
name: policy-review-checklist
description: synthoria-admin-ui에서 구현 산출물을 품질 게이트 통과 여부로 판정할 때 사용하는 횡단 체크리스트. 검증·payload·중복·성능·재사용·SKILL diff 로그 점검이 필요할 때 사용.
---

# Review Checklist (Policy)

## 언제 이 스킬을 사용하나요?

- 구현/퍼블리싱/리팩터 산출물을 품질 게이트로 판정할 때
- 완료 직전 self-review로 누락 항목을 재확인할 때

## Scope

검토 단계 전용 체크리스트. 구현 중에는 self-review 참고용으로만 사용한다.

## Checklist

### 기능/품질

- **validation 적절성** — 필수값/형식/에러 메시지 누락 없음 (`policy-validation` 기준)
- **payload completeness** — 서버 DTO 필드 누락/오타 없음 (`recipe/data-dto` 기준)
- **duplicate implementation 여부** — 공용 컴포넌트/훅 재사용 가능 케이스를 새로 구현하지 않음
- **성능 리스크** — 무한 루프 가능 의존성, 불필요 re-render, N+1 fetch 등
- **reusable asset 재사용 여부** — `reference/components`, `reference/custom-hooks` 우선 사용
- **skill diff log 반영 여부** — 관련 SKILL 변경이 있었다면 명시적으로 반영/갱신
- **memory/reusable-assets.md 갱신 여부** — 신규 공용 컴포넌트/훅이 추가된 경우 `memory/reusable-assets.md`에 항목 추가 완료 여부 (구현·리팩터 산출물에만 해당)

### 아키텍처

- **FSD 레이어 위치 적절성** — 승인된 계획 문서의 FSD 정의 기준으로 파일이 올바른 레이어(`app/pages/widgets/features/entities/shared`)에 위치하는지 확인
- **의존 방향 준수** — 계획 문서에 명시된 레이어 제약 위반 없음 (상위 레이어 → 하위 레이어 단방향 의존, 동일 레이어 간 직접 의존 금지)
- **추상화 결정 일치 여부** — 구현 로그에 기록된 추상화 결정과 실제 구현 범위가 일치하는지 확인
- **공용화 수준 준수** — 계획 단계에서 결정한 공용화 수준(글로벌/도메인 내/로컬)과 실제 파일 위치 및 import 경로가 일치하는지 확인
- **추상화 4조건 충족 여부** — 추상화가 적용된 경우 `policy-abstraction-strategy` 4조건 중 하나 이상 충족하는지 확인. 미충족 시 과잉 추상화로 반려
- **hook 분리 기준 준수** — hook으로 분리된 경우 상태성(stateful) 여부가 근거인지 확인. 순수 변환/검증 로직이 hook으로 분리되었으면 반려 (`policy-hook-extraction` 기준)
- **interface vs type 준수** — props·콜백·hook 반환·경계 DTO 등 "두 관계 간 계약"을 `type`으로 선언했으면 반려. 유니온/매핑/파생을 interface로 우회했으면 반려 (`policy-type-definition` 기준)
- **도메인 전용 vs 공용 마이크로 hook 구분** — "공용이지만 도메인별로 다르게 동작"하는 hook이 있으면 반려. 도메인 전용 hook으로 분리해야 함

## 판정 원칙

- 체크리스트 중 하나라도 미흡하면 **반려**
- 반복 반려 시 escalation 규칙 적용 (역할 기반 엔진에서는 `.harness/roles/orchestration.md` 기준)
