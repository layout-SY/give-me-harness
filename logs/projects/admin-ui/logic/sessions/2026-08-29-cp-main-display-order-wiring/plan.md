# 계획

## 목표

CP 메인 노출 관리 화면에서 항목 순서를 위·아래로 이동하고, 변경 여부에 따라 저장 가능 상태를 제어하며, 저장 요청과 응답에 변경된 `order`가 일관되게 반영되도록 한다.

## 범위

- 순서 이동과 이동 가능 여부를 계산하는 도메인 모델
- process/controller와 화면 간 이동·저장 계약
- 위·아래 이동 버튼의 상태와 스타일
- MSW 저장 handler의 순열 검증 및 정렬 응답
- 이동·dirty·저장 round-trip 회귀 테스트

## 제외 사항

- 다른 CP 관리 화면의 정렬 방식 변경
- 공용 순서 제어 컴포넌트 신규 추상화
- 전체 저장 API 계약 개편
- 기존 전체 lint 오류 수정

## 제약 조건

- `task/cp-main-display-order-wiring`의 승인된 경로만 변경한다.
- production UI와 기능 로직의 기존 계약을 보존하면서 필요한 배선만 추가한다.
- screenshot, GIF, 화면 비교 없이 기능 동작으로 QA한다.
- commit과 `sy-main` 병합은 별도 사용자 승인을 받은 뒤 수행한다.

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 브랜치·범위 관리 | Hephaestus | `policy-git-branch-strategy` | 승인된 브랜치와 경로 유지 |
| 모델·hook·MSW 구현 | Hephaestus | `policy-coding-convention`, `policy-type-definition` | 순서 변경과 저장 계약 연결 |
| 검증 | Watcher | `policy-review-checklist` | 현재 변경의 PASS/FAIL 독립 판정 |
| 장기 평가 | Evaluator | 해당 역할 계약 | 비차단 개선 사항 분리 기록 |
| 문서화 | Hephaestus | `policy-documentation`, `policy-portfolio` | 필수 8종 산출물 작성 |

## 검증

- `node --test tests/*.test.mjs`
- `npm run build`
- 변경 파일 대상 `npx eslint ...`
- `GIT_MASTER=1 git diff --check`
- 브라우저에서 이동, 저장 요청, 저장 후 dirty 해제 확인

## 위험 요소 및 결정 사항

- 배열 위치와 `order` 값의 의미가 어긋나면 이동 후 저장 결과가 달라질 수 있으므로 이동 시 연속된 `order`를 다시 부여한다.
- 저장 handler가 ID·제목·순서 집합과 중복을 검증하도록 하여 잘못된 순열을 성공 처리하지 않는다.
- 공용 추상화는 현재 단일 도메인 사용만 확인되어 도입하지 않는다.

## 승인

- 상태: approved and implemented
- 사용자는 구현 및 문서 경로 확장을 승인했다.
