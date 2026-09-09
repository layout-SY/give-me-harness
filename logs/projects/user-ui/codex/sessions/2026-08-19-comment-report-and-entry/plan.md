# 계획

## 목표

로그인한 사용자가 투표·토론 참여 여부와 무관하게 투표·토론·정책반영 상세에서 댓글을 작성하고 선택한 댓글을 신고할 수 있게 한다. 제안 등록은 5개 UI 필드를 검증해 POST하고 생성된 상세로 이동시킨다.

## 범위

- Claude Code: 신고 아이콘, 댓글 입력 UI, 제어형 props/callback 계약.
- Hephaestus: 댓글·신고 DTO, mutation 조율 hook, MSW 상태, 상세 route 연결.
- 공통: 댓글 목록 갱신, 로그인 상태에 따른 작성 가능 여부, 신고 대상 식별.
- Hephaestus: 제안 DTO·Zod/useForm 모델·mutation·route·MSW 영속화 및 오류 접근성 연결.

## 제외 사항

- 투표 또는 토론 참여 여부에 따른 댓글 작성 제한.
- 새 UI 라이브러리 및 브라우저 캡처 기반 시각 QA.
- 실제 backend가 확정하지 않은 별도 신고 endpoint 신설.
- 제안 등록 UI의 시각 재설계.

## 제약 조건

- production UI는 Claude Code가 소유하며 `UI_COMPLETE` 확인 전 Hephaestus가 연결하지 않는다.
- 기존 `ReportPopup`, `Popup`, `TextArea`, `IconButton`을 재사용한다.
- 신고 요청은 기존 content-level endpoint를 유지하고 `commentId`를 body에 포함한다.
- 제안 payload는 `{ title, body, detail, effect, reference? }`를 사용한다.

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| UI 계약 | Claude Code | `project-ui`, `reference-components`, `policy-styles`, `policy-publishing` | 아이콘·입력·팝업 props 제공 |
| DTO·hook·mock | Hephaestus | `programming`, `recipe-api-authoring`, `policy-data-fetch-layer`, `policy-validation` | 타입 지정 요청과 상태 전이 구현 |
| 검토·문서 | Hephaestus/Watcher | `policy-review-checklist`, `policy-documentation` | 검증 근거와 PASS/FAIL 기록 |

## 검증

- 댓글 POST 후 목록 선두 반영 테스트.
- 선택 댓글 ID가 포함된 신고 POST 테스트.
- 비로그인 제출 차단과 로그인 댓글·신고 상태 hook 테스트.
- `npm run lint`, `npm run build`.
- 제안 빈 제출 오류 4개, trim된 POST payload, 생성 상세 이동 및 목록·상세 mock 조회 테스트.

## 위험 요소 및 결정 사항

- 현재 시민참여 route는 인증 route guard가 없으므로 UI 활성 상태는 route에서 `/me` 성공 여부를 주입한다.
- backend 신고 계약이 다르면 `ReportRequestDto.commentId` 위치를 backend 계약에 맞춰 조정해야 한다.

## 승인

- 상태: approved
- 승인 문구: `작업 진행..`
