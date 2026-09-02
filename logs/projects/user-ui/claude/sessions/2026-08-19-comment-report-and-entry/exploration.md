# 탐색

## 요청

댓글 카드 신고 아이콘과 PDF 38쪽 신고 모달을 제공하고, 정책 변경에 따라 로그인한 모든 사용자가 서비스 참여 여부와 무관하게 댓글을 작성하도록 한다.

## 대상 관련 사실

- `CommentList`에는 `onReport`와 텍스트 신고 버튼이 있었지만 상세 route가 callback을 전달하지 않았다.
- `ReportPopup`은 PDF 38쪽의 신고 대상, 사유, 상세 사유, 취소·접수 구조를 이미 구현한다.
- `useCommentMutation`과 `useReportMutation`은 존재하지만 상세 route에서 사용하지 않았다.
- 기존 `ReportRequestDto`에는 신고 대상 댓글 ID가 없었다.
- 기존 MSW 범용 POST handler는 댓글을 저장하지 않고 content ID만 반환했다.
- 시민참여 route는 인증 guard가 없으며 `useMeQuery`와 auth-required mutation이 인증 경계로 존재한다.

## 불러온 스킬

- `skill-index`, `project-ui`, `policy-harness`, `reference-index`, `reference-components`
- `policy-coding-convention`, `policy-type-definition`, `policy-data-fetch-layer`, `policy-validation`
- `policy-styles`, `policy-publishing`, `policy-documentation`, `policy-review-checklist`
- `programming`, `refactor`, `policy-hook-extraction`, `policy-abstraction-strategy`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| `Popup` | 재사용 | 기존 `ReportPopup`이 사용하며 PDF 오버레이 구조 충족 |
| `TextArea` | 재사용 | 신고 상세 사유와 댓글 입력에 적합 |
| `IconButton` | 재사용 | 아이콘 전용 버튼과 접근 가능한 이름 지원 |
| `ReasonPrompt` | 제외 | 신고 사유 단일 선택과 대상 미리보기를 지원하지 않음 |
| `CustomModal` | 직접 사용하지 않음 | 기존 `ReportPopup`이 `Popup` 어댑터를 이미 사용 |

## 제안 등록 추가 탐색

- `ProposalWritePage`는 `title`, `background`, `detail`, `effect`, `reference`를 노출했지만 기존 form 모델은 `category`, `content`를 사용해 계약이 불일치했다.
- `ProposalWriteRoute`는 제어 상태를 직접 보관하고 제출 시 `console.log`만 호출했다.
- `useCreateProposalMutation`과 proposal API는 이미 존재했으므로 새 데이터 계층 없이 form mapper와 route 연결만 필요했다.
- 기존 제안 POST MSW는 고정 ID만 반환하고 생성 항목을 목록·상세 fixture에 저장하지 않았다.

## 제약 조건 및 미확인 사항

- 신고 전용 아이콘 자산은 현재 없어 Claude Code가 UI 자산으로 추가해야 한다.
- 실제 backend의 댓글 신고 request shape는 저장소에 별도 계약 문서가 없다.
- Claude Code `UI_COMPLETE` 확인 뒤 최신 UI 계약을 다시 읽고 route 통합을 수행했다.

## 결론

UI를 새로 설계하지 않고 기존 `ReportPopup`과 공용 입력·아이콘 어댑터를 재사용했다. 기능 계층은 로그인 boolean만 받으며 참여 상태를 참조하지 않는다. 제안 등록은 UI의 `background`를 API의 `body`로 명시적으로 매핑하고 선택 reference의 공백 값은 생략한다.
