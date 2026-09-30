# 계획

## 목표

## 작업 유형

- feature | refactor | hybrid | publish-only | audit-only | documentation

## 범위

## 제외 사항

## 제약 조건

## 스킬 및 역할

- 제안 역할:
- 역할 판단 근거:
- 사용자 역할 확인:
- 승인할 Git 작업:
- 산출물 책임: owner | contributor

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |

## UI 자산 선정

UI 구현을 계획하면 `ui-library` 스킬에 따라 승인 요청 전에 작성한다. 해당하지 않으면 이유를 기록한다.

- 항목별 자산 선정 문서: [UI 자산 선정 계획](unknown/ui-asset-plan.md)
- 외부 UI 라이브러리 사용 스킬·세션 초안과 중앙 등록·갱신 계획:
- 미정 선택·계약과 사용자에게 확인할 결정:

## UI·Logic 연결 계약

UI와 API를 연결하면 `api-authoring/references/ui-controller.md`에 따라 작성한다.

- 선행 구현·계약 제공자와 확인 근거:
- 맞추는 방향: `controller <- UI` (Logic 선행) | `controller -> UI` (UI 선행)
- 기준 UI·controller·요청/응답 DTO 경로와 controller 공개 타입·구현 위치:
- 응답→UI 데이터·상태 / UI 입력·동작→요청 매핑:
- 불일치 항목과 확인할 질문·합의한 계약:

## 검증

## 위험 요소 및 결정 사항

## 승인

- 상태: awaiting approval
- 필수 문구: `이 역할과 계획대로 진행할까요, 아니면 조정할 부분이 있나요?`
