# 전역 모달 팝업 계약 통일 결과

- 역할: ui
- 작업 위치: `/Users/okand/SynologyDrive/asan-metaverse-user-ui`
- 브랜치 `task/unify-popup-modal`(부모 `sy-main`, fork `63eda3b`), 커밋 `3f80258`
- `sy-main`에 ff-only 병합 완료. 병합 후 형제 `task/meeting-entry-ui`도 다른 세션에서 병합되어 현재 `sy-main`은 `71ba983`이다.

## 실제 변경

신설
- `src/shared/ui/popup/parts/popup-parts.tsx` — `PopupBody` `PopupIcon` `PopupHeading` `PopupMeta` `PopupNotice` `PopupCallout` `PopupFootnote` `PopupActions`
- `src/shared/ui/popup/parts/popup-parts.css` — meeting-reservation의 `vo-*` 값을 값 변경 없이 `popup-*`로 이관
- `src/shared/ui/popup/index.ts`에서 컨테이너와 표준 파트를 함께 export

연결
- `ReserveCompletePopup` / `ReservationRestrictedPopup` / `ReservationCancelConfirmPopup` / `ReservationCancelCompletePopup`: `vo-*` 마크업 → 표준 파트. 문구·필드 구성은 그대로
- `MeetingReservePage`, `MeetingReservationDetailPage`: `NoticeBox` → 공용 `PopupNotice`
- `features/citizen-participation/ui/report/ReportPopup.tsx`: 헤더·안내문·액션을 표준 파트로 교체. `citizen-report.css`는 팝업 안에서 필요한 `--cp-*` 토큰 선언과 `.cp-report__target`만 남김
- `shared/ui/image-upload/image-upload.tsx`: `h1` + `hr` → `PopupHeading`
- `shared/ui/reason-prompt/reason-prompt.tsx`: HeroUI `CustomModal` → `Popup` + 표준 파트 + 공용 `Button`. `reason-prompt.css`는 textarea 규칙만 남기고 하드코딩 hex를 디자인 토큰으로 교체

정리
- `meeting-reservation-parts.css`에서 `vo-notice` / `vo-complete` / `vo-restricted` / `vo-cancel` 34줄 삭제

테스트
- `ReservationCancelConfirmPopup.test.tsx`, `ReservationCancelCompletePopup.test.tsx`: `.vo-cancel__meeting-meta` → `.popup-meta__detail`
- `MeetingReservationRoutes.test.tsx`: `.vo-notice` → `.popup-notice`, `.vo-cancel__actions` → `.popup-actions`
- `reason-prompt-host.test.tsx`: `vi.mock("../modal")` 제거 후 `HTMLDialogElement` 스텁으로 실제 `Popup`을 렌더, `h3` → `h2`

## 검증 결과

- `npx eslint .` — 통과(출력 없음)
- `npx tsc -b` — 통과
- `npx vite build` — 성공
- `npx vitest run src/shared/ui src/features/meeting-reservation/ui src/pages/meeting-reservation src/pages/citizen-participation/ui/CitizenCommentRoutes.test.tsx src/App.test.tsx` — 15 파일 81 테스트 통과
- 전체 `npx vitest run`에서는 29개 실패가 있으나 모두 citizen MSW 계층(`mocks/browserHandlers`, `mocks/handlers`, `api/http/citizenParticipation.api`, `CitizenResultRoutes`)의 `[MSW] Cannot bypass a request when using the "error" strategy` 오류와 그 여파다. 이 파일들은 이번 작업에서 수정하지 않았고, `browserHandlers.test.ts`는 단독 실행에서도 실패한다. `MeetingReservationRoutes.test.tsx`는 단독 실행 시 16개 전부 통과한다.
- 포맷: 중앙 포맷 트리거가 차단되어 프로젝트 `.prettierrc` 설정으로 `npx prettier --write`를 변경한 `.ts`/`.tsx`에 직접 적용했다. CSS는 저장소의 기존 한 줄 규칙 양식을 유지했다.

## 병합

- 관계 등록: `task/unify-popup-modal` 부모 `sy-main`, fork `63eda3b`
- 검토 `ba2e1153596c48c3bb9dcf63c95dc98e` → 완료 작업 `0d63525906ec4f939015d93dca38b38b`
- ff-only 병합 성공. `sy-main` `63eda3b` → `3f80258`
- 실행기 검증: `npm run lint` exit 0, `npm run build` exit 0, `verification_passed: true`
- 정리 보류: `기본 worktree는 자동 삭제하지 않습니다`. `task/unify-popup-modal`이 현재 체크아웃 중인 기본 worktree라 로컬 브랜치를 남겼다.

## 형제 병합 후속 확인

검토 보고에서 위험으로 남긴 형제 `task/meeting-entry-ui`가 이후 다른 세션에서 `sy-main`에 병합됐다(`71ba983`). 병합 후 `sy-main`을 확인한 결과 통일 계약이 유지됐다.

- `NoticeBox.tsx`, `shared/ui/modal/`, `shared/ui/side-modal/` 모두 부활하지 않음
- `NoticeBox` / `vo-notice` / `vo-complete` / `vo-cancel` / `vo-restricted` 참조 0
- 형제의 새 팝업 4종이 표준 파트를 사용: `entry/EntryDeniedPopup.tsx`, `entry/EntryWaitPopup.tsx`, `meeting/ui/room/MeetingEntryNoticePopup.tsx`, `meeting/ui/room/MeetingExitConfirmPopup.tsx`
- `meeting-entry.css`의 `vo-entry*`는 팝업이 아니라 그 브랜치의 페이지 레이아웃 클래스로 이번 계약과 무관하다

## 정리

형제 병합을 수행한 Codex 세션(PID 71697)이 종료되면서 linked worktree `/Users/okand/SynologyDrive/asan-worktrees/sy-main-entry-merge`가 `sy-main`을 점유한 채 남아 있었다. 그 때문에 기본 worktree를 `sy-main`으로 되돌릴 수 없어 브랜치 정리가 막혀 있었다.

- 잔여 worktree는 clean이었고 미보존 파일은 재생성 가능한 `dist/`·`node_modules/`뿐임을 확인한 뒤 사용자가 직접 제거했다.
- 기본 worktree가 `sy-main`(`71ba983`)으로 복귀했다.
- `task/unify-popup-modal`(`3f80258`)은 `sy-main`에 완전히 포함됨을 확인하고 사용자가 `git branch -d`로 삭제했다. guard가 에이전트의 직접 삭제를 막고, 이 세션의 완료 정리 `recover`는 병합 이후 `sy-main`이 `71ba983`으로 이동해 대조가 불가능했기 때문이다.
- 관계 그래프에 `relation --action retire --name task/unify-popup-modal`로 퇴역 처리했다(작업 `dbbed591eb41446a8f9d30de13e324f7`).

최종 상태: worktree 1개(기본), 브랜치 `sy-main` `71ba983`, 작업 트리 clean.

## 남은 사항

1. 관계 그래프에서 `task/meeting-entry-ui`는 `71ba983`으로 병합되고 로컬 ref도 사라졌는데 `resolution: null`, `deleted: false`로 남아 있다. 그 병합의 검토 근거가 이 세션에 없어 대신 기록하지 않았다. 해당 작업의 완료 절차로 처리해야 한다.
2. citizen MSW 계층 테스트 실패 13건은 이번 작업과 무관한 기존 상태로 그대로 남아 있다.
3. `ReserveCompletePopup`의 초대코드 문구는 형제 병합 결과 `영문·숫자 10자리`로 확정됐다. 서비스 정책상 어느 쪽이 맞는지는 확인하지 못했다.
