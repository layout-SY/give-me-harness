# 최종 요약

## 제공 사항

- CP 메인 노출 항목의 위·아래 순서 이동
- 경계 항목 이동 버튼 비활성화
- `order` 변경을 포함한 dirty/save 상태 제어
- 저장 후 응답 기준 상태 동기화
- MSW 저장 payload 순열·중복 검증
- 이동·저장 회귀 테스트

## 제외 사항

- 다른 화면의 순서 제어 공용화
- 실제 백엔드 환경과의 통합 호출
- 기존 전체 lint 오류 수정

## 검증

| 명령어 | 결과 |
| --- | --- |
| `node --test tests/*.test.mjs` | 20/20 통과 |
| `npm run build` | 통과 |
| 변경 파일 대상 `npx eslint ...` | 통과 |
| `GIT_MASTER=1 git diff --check` | 통과 |
| 브라우저 기능 QA | 이동·저장·응답 반영·dirty 해제·console error 0건 확인 |

## 산출물

- 순서 이동 모델과 타입 계약
- process/controller/view 배선
- MSW 저장 검증 강화
- `tests/cp-main-display-order-control.test.mjs`
- 본 세션의 필수 8종 문서

## 남은 제한 사항

- `lsp_diagnostics`는 linked worktree cwd 제약으로 실행하지 못했다.
- 전체 lint는 변경 범위 밖 기존 오류 73건과 warning 5건이 남아 있다.
- 실제 백엔드 저장 연동은 이번 범위에서 검증하지 않았다.

## 다음 단계

사용자의 별도 승인을 받은 뒤 승인 범위만 commit하고 `sy-main`에 merge한 다음 동일 검증을 재실행한다.
