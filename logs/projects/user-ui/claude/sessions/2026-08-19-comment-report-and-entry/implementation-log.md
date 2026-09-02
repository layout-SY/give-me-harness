# 구현 로그

## 승인된 범위

로그인 사용자 공통 댓글 작성·선택 댓글 신고의 DTO·hook·MSW·상세 route 통합과 제안 등록의 검증·POST·상세 이동·mock 영속화를 완료했다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `api/comment/comment.dto.ts` | 댓글 request Zod schema 추가 | 공백-only 댓글 거부 및 trim |
| `api/report/report.dto.ts` | `commentId`, 신고 사유 schema 추가 | 신고 대상과 허용 사유를 타입으로 고정 |
| `mocks/commentHandlers.ts` | 댓글·좋아요·신고 전용 MSW 상태와 handler 추가 | 댓글 저장 및 대상별 신고 응답 |
| `mocks/handlers.ts` | 댓글 책임을 전용 모듈로 분리 | 250줄 초과 방지 및 범용 handler 충돌 제거 |
| `hook/useCitizenCommentActions.ts` | 댓글·신고 제어 상태와 mutation 조율 | 인증 여부만으로 작성 허용 |
| `index.ts` | 기능 hook·mutation·신고 사유 타입 공개 | route 연결 준비 |
| `CitizenParticipationDetailRoutes.tsx`, `CitizenReadDetailRoutes.tsx` | 댓글 작성과 `ReportPopup` 연결 | 투표·토론·정책 상세에서 동일 흐름 제공 |
| `proposal.dto.ts`, `proposalForm.ts` | 5개 UI 필드 Zod/useForm 계약과 API mapper 구현 | 필수값 검증 및 trim된 payload 생성 |
| `ProposalWritePage.tsx`, `FieldGroup.tsx` | 필드 오류와 `aria-invalid`·`aria-describedby` 연결 | 오류 문구를 필드별로 접근 가능하게 표시 |
| `CitizenAuxiliaryRoutes.tsx` | form과 POST mutation 연결 | 성공 시 생성 제안 상세로 이동 |
| `mocks/handlers.ts` | 생성 제안 상태 저장 | POST 뒤 목록·상세 조회 가능 |

## 결정 사항

- 댓글 작성 가능 여부는 `isAuthenticated` 하나로 결정한다.
- 댓글 작성 성공 시 입력을 비우고 기존 query invalidation으로 목록을 갱신한다.
- 신고 성공 시 대상, 사유, 상세 내용을 초기화한다.
- report endpoint는 유지하고 body에 `commentId`를 추가한다.
- 제안 `background`는 API `body`로 매핑하고 공백-only 선택 reference는 생략한다.
- 제안 POST 성공 시 응답 ID를 사용해 상세 route로 이동한다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| 시민참여 focused Vitest 5 files | 25개 통과 |
| route 재검증 Vitest 2 files | 6개 통과 |
| `npm run build` | production build 통과, 기존 chunk 크기 경고만 발생 |
| `npm run lint` | 통과 |
| `npm test` | 이번 범위 174개 포함 통과, 범위 밖 auth 1개·meeting API 2개 기존 실패 |
| `lsp_diagnostics` | TypeScript LSP 미설치 및 사용자 설치 거절 상태로 실행 불가 |

## Watcher 인계

- Claude Code `UI_COMPLETE` 뒤 최신 props/callback 계약을 읽고 route를 연결했다.
- 필수 Watcher 호출은 외부 Anthropic API 크레딧 부족으로 실행되지 않아 공식 에이전트 판정은 확보하지 못했다.
- 체크리스트와 정적 검증 결과는 `review-log.md`에 기록한다.
