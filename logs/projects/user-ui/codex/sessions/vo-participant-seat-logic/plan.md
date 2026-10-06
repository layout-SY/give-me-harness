# 회의실 좌석 배정·유지 연결 계획

## 승인 대상

- 목표: 회의실 참여자에게 빈자리 중 가장 작은 번호를 배정하고 퇴실할 때까지 유지한다. 중간 퇴장 후에도 남은 참여자의 번호는 이동하지 않는다.
- 역할: 확인된 `logic`. 기존 UI에 상태 결과만 연결한다.
- 작업 위치: `/Users/okand/SynologyDrive/asan-worktrees/vo-participant-status`, branch `task/vo-participant-status`, 확인 HEAD `ed63b192ae8a70b6dbb9aca384fdff96ea4619bd`.
- 직접 부모: 인계 문서상 `sy-main`. 동일 Git common directory를 확인했다. Git 변경은 이번 계획에 포함하지 않는다.
- 사용자 확정: 재입장 시 빈자리 중 가장 작은 번호를 새로 배정한다. 참여자 목록에는 역할만 표시한다.
- 입력: 기존 `MeetingEntryRoute`에서 구성하는 참여자 ID 목록(Agora uid 문자열). 초기 목록은 전달된 순서로 배정하며, 이후 새로 관찰된 ID에 빈자리를 배정한다. 현재 UI는 좌석 번호만 표시하며 참여자 이름과 좌석을 연결해 표시하지 않는다.
- 출력: `readonly number[]` 형태의 사용 중인 좌석 번호. 정원 기본 10, 정원 초과 참여자는 좌석 표시에서 제외한다는 인계 계약을 따른다.
- 상태 수명: 회의 진입 컴포넌트 안에서 유지하고 참여자가 목록에서 사라지면 해당 배정을 해제한다. 방 변경 시 기존 `MeetingEntryContent`의 key에 따라 초기화한다.

## 조사 근거와 재사용 결정 제안

- UI 인계: `.claude/logs/sessions/vo-participant-status-ui/handoff.md`. 미커밋이라고 기록된 UI 변경은 이후 `ed63b19`에 커밋됐고 현재 작업 트리는 깨끗하다.
- `src/features/meeting/hook/agora/useAgoraParticipants.ts`: 원격 참여자 추가·삭제와 미디어 상태를 관리한다. 목록을 데이터 출처로 재사용하며 좌석 전용 상태는 이 RTC hook에 넣지 않는다.
- `src/features/meeting/hook/agora/useAgoraMeeting.ts`: Agora 이벤트를 위 hook에 연결하고 로컬 uid와 원격 참여자 목록을 제공한다. 기존 흐름을 재사용한다.
- `src/pages/meeting-reservation/ui/MeetingEntryRoute.tsx`: 로컬·원격 참여자를 `RoomParticipant[]`로 구성하지만 좌석 배정 hook 호출과 `occupiedSeats` 전달은 없다. 이 조립 결과를 재사용한다.
- `src/features/meeting/ui/room/MeetingRoomView.tsx`: `occupiedSeats` 표시 계약이 이미 있다. UI 구조 변경 없이 기존 prop에 연결한다.
- 조사 범위 `src/features/meeting/hook/`, `src/shared/`에서 좌석 배정 상태를 관리하는 기존 hook은 확인하지 못했다. 공용 API·table hook은 요청·페이지네이션을 위한 것으로 좌석 상태 계약과 맞지 않는다.
- 제안: 회의 기능 내부에 `useSeatAssignment`를 새로 작성한다. 대안은 `useAgoraParticipants` 확장이지만 RTC 미디어 책임에 표시용 배정 규칙이 결합된다. 신규 feature hook 방식을 승인 대상으로 제시한다.
- 신규 hook은 네트워크 요청이나 이벤트 구독 없이 기존 목록만 입력받으므로 요청 취소·구독 해제 책임을 추가하지 않는다.

## 예상 변경

1. `src/features/meeting/hook/useSeatAssignment.ts`: 참여자별 번호를 상태로 유지하고 삭제·추가·빈자리 재사용을 처리한다. 목록 내용이 같으면 배정을 유지한다.
2. `src/features/meeting/hook/useSeatAssignment.test.tsx`: 입장 순서, 중간 퇴장 후 유지, 재입장과 빈자리 재사용, 정원 초과, 빈 목록 초기화, 같은 ID 목록의 재렌더링을 검증한다.
3. `src/features/meeting/index.ts`: page에서 사용할 hook을 노출한다.
4. `src/pages/meeting-reservation/ui/MeetingEntryRoute.tsx`: hook 결과를 기존 `MeetingRoomView.occupiedSeats`에 연결한다.
5. 기존 라우트 테스트 배치와 mock을 확인해 실제 연결을 검증하는 최소 회귀 테스트를 추가한다. 필요 경로는 `src/pages/meeting-reservation/ui/MeetingReservationRoutes.test.tsx` 또는 인접 `MeetingEntryRoute.test.tsx`다.

## 적용 스킬

- `policy-task-role-routing`, `policy-git-branch-strategy`: Logic 경계, 인계와 실제 상태 대조, Git 변경 별도 승인.
- `reference-custom-hooks`: 기존 hook 재사용 조사, 좌석 상태를 회의 기능 내부에 배치.
- `policy-coding-convention`, `policy-type-definition`: arrow function hook, 엄격한 타입, 명시적인 입력·출력, type alias 우선.
- `policy-documentation`: 현재 세션의 계획과 구현·검증 결과 기록. 다른 세션 기록은 읽기 전용.

## 수행 순서와 완료 기준

- [x] 위 worktree에서 승인된 hook과 route 연결을 구현하여 입·퇴장 후 남은 좌석 번호가 유지되게 한다.
- [x] 같은 위치에서 중앙 `formatting.py apply`를 실행하여 수정 파일을 실제 포맷한다.
- [x] hook·연결 테스트와 `npx vitest run src/features/meeting src/features/meeting-reservation src/pages/meeting-reservation src/app/routing.test.ts`를 실행하여 상태 전이와 기존 회의 기능을 검증한다.
- [x] `npm run lint`, `npm run build`를 실행한다. 실패는 원인과 이번 변경 관련 여부를 구분한다.
- [x] 변경과 검증 결과를 현재 세션 산출물에 기록한다. 실제 다자간 Agora 접속은 로컬 자동 테스트의 검증 범위에 포함되지 않는다.

## 진행 기록

- 사용자에게 미확정이었던 재입장 방식과 역할 표시에 대한 답변을 받았다.
- 사용자가 `진행`으로 계획을 승인했다. hook, route 연결과 단위·연결 테스트를 구현했다.
- hook과 연결 구현 완료. 정원 초과·중복·목록 재정렬·초기화 등을 포함하는 hook 테스트 6건과 실제 MeetingRoomView를 사용하는 route 연결 테스트 1건을 추가했다.
- 중앙 포맷 실행기는 최초 sandbox에서 events.lock 접근이 차단됐고 권한 승인 후 수정 소스 5개를 포맷했다. build와 Vitest도 linked worktree 임시 파일 쓰기 차단 후 권한 승인으로 재실행했다.
- lint와 build 통과. build는 500 kB 이상 chunk 경고가 있다.
- 관련 42개 파일의 최초 병렬 테스트: 320건 통과, 예약 라우트 테스트 파일에서 16건 실패. 첫 테스트가 5000 ms를 초과한 뒤 act 경고와 연쇄 실패가 발생했다. 새 테스트 7건은 모두 통과했다.
- 테스트 코드나 시간 제한은 변경하지 않고 `--maxWorkers=1`로 동일 범위를 재검증하여 42개 파일 336건 전부 통과했다(93.40초). 최초 실행은 lint·build와 병행했고 재검증은 다른 검증 프로세스 종료 후 수행했다. 병렬 실행 안정성 문제의 근본 원인까지 확정한 것은 아니다.
- 최종 결과는 [final-summary.md](./final-summary.md)에 기록했다. 이후 사용자 명령 실행 승인으로 소스 5개를 `0215029`에 커밋했고 worktree가 깨끗함을 확인했다.
- 사용자 승인으로 문서 2개를 stash `a0bd482`에 보관하고 EC 삭제 관계 기록을 정리한 뒤, source `0215029`를 sy-main `f5ab12d`에 병합했다. 병합 commit은 `5df71dc`, source branch·worktree는 유지했다.
- primary worktree에서 병합 후 lint·build 및 인증·회의·예약·라우팅 테스트 48개 파일 418건이 모두 통과했다. 문서 복원 작업 `6ba99d79e7d622478bb061a16b338d17`은 보호 실행기의 별도 명령 승인을 기다린다.
- 이후 사용자 명령 실행 승인으로 위 복원 작업을 완료했다. 문서 2개의 파일 내용·diff가 stash와 정확히 일치하며 primary에는 기존 문서 변경만 남았다. 로컬 병합·검증·복원 완료, 원격 push 및 stash·branch·worktree 삭제는 수행하지 않았다.
