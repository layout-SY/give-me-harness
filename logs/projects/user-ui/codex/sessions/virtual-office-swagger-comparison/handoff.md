# 가상 오피스 실 API 연결 및 최초 입장 UI 인계

## Assignment 이동

- 보내는 host/session/role: Codex / virtual-office-swagger-comparison / logic.
- 받는 host/session: 미정. UI 작업은 새 `--role ui` 세션에서 수행한다.
- 요청 목적: 사용자 확정 계약을 보존하고 회의 정보 확인 페이지와 최초 입장 안내 팝업을 한 페이지로 합치는 UI 작업을 인계한다.

## 역할 라우팅

- requested_roles: logic, ui.
- confirmed_roles: 현재 세션 logic. 사용자는 UI 변경을 별도 UI 세션으로 인계하도록 명시했다.
- completed_roles: Logic 비교 분석 완료. API 연결 구현·UI 구현은 미완료.
- next_role: ui(화면 통합), logic(미확정 계약 해소 후 실 API 연결).
- 현재 Logic 세션은 UI 마크업·레이아웃 구현을 수행하지 않는다.

## 목표 및 현재 상태

Swagger에서 발췌된 `/meeting/rooms` 계열 8개 API를 기존 `ApiClient → DTO/parser → Query/Mutation → controller → UI` 패턴으로 연결하는 것이 전체 목표다. 현재 앱은 기존 임시 API를 사용한다. 이 문서를 실제 API 연결 또는 controller 구현 완료의 증거로 사용하지 않는다.

사용자 결정은 아래에 확정/미확정으로 나누었다. 미확정 ID 관계를 임의로 연결하거나 임시 값을 만들어 다음 단계에 전달하면 안 된다.

## 완료된 작업

- Swagger 발췌와 현재 소스·문서 비교: `final-summary.md`.
- proposal 생성, vote 수정·삭제, inquiry query/mutation/controller 및 shared ApiClient 재사용 패턴 조사.
- 사용자 추가 답변의 UI·Logic 요구사항 정리.
- 애플리케이션 소스 변경·커밋 없음.

## 사용자 확정 사항

| 항목 | 계약 |
| --- | --- |
| 회의 안건 | 현재 표시 문구인 `미입력` 사용. channelName을 안건으로 사용하지 않는다. |
| 최초 입장 UI | `CodeMeetingConfirmPage`와 `MeetingEntryNoticePopup`의 내용을 한 페이지로 통합하고 `firstEntry`로 표시 여부를 결정한다. firstEntry=true이면 표시, false이면 통합 안내 페이지 생략. |
| firstEntry | 서버가 최초 요청 시 true, 퇴장 후 다시 조회하면 false로 관리한다. 클라이언트가 최초 입장 여부를 별도로 영속화하지 않는다. |
| 역할·상태 | 확인된 HOST, INVITED를 각각 해당 상수 객체에 `as const`로 선언한다. 다른 서버 값은 원문 표시. 미확정 enum 값을 만들어 추가하지 않는다. 전체 상태 enum을 가정한 참여자 필터링 금지. |
| UID | 새 서버 UID로 연결한다. 기존 임시 userSeq의 숫자 해시로 대체하지 않는다. |
| 회의실 이름 | 사용자는 theme를 회의실 이름으로 사용하도록 지정했다. themeName과 혼동하거나 임의로 다른 필드로 대체하지 않는다. |
| 예약자명 | entry 응답 nickname을 표시하도록 지정했다. 이 표시 매핑을 nickname의 서버상 신원 의미가 검증되었다는 뜻으로 확대하지 않는다. |
| 인증·응답 | 기존 VITE_API_BASE_URL, Bearer 인증, 성공 code=SUCCESS 패턴 사용. |
| 토큰 갱신 | `/meeting/rooms/{meetingRoomId}/join` 재호출. |
| 장치 검사 | 검사 전에 join으로 토큰을 받는다. 취소 또는 Agora 연결 실패 시 leave(finalExit=false)로 정리하는 제안을 승인했다. |
| 실패 안내 | 입장을 시도했지만 Agora 연결 실패로 정리된 경우와, 입장 성공 후 사용자 요청으로 퇴장한 경우의 안내를 구분한다. 같은 leave endpoint를 사용해도 UI 결과는 같지 않다. |
| 주기적 갱신 | 참여자·채팅 5초 갱신 제안을 승인했다. 임시 heartbeat endpoint를 실제 서버에 새로 가정하지 않는다. |
| 채팅 | content, senderUid, 서버 메시지 ID 및 afterId 조회 계약 적용. 중복 발송 대책은 사용자가 보류했다. 조회 데이터의 ID 중복 병합과 발송 멱등성은 구분한다. |
| 기존 이용 규칙 | 영문·숫자 10자리 코드, 시작 5분 전 코드 인증, 시작 시각부터 입장, 종료 10분 전부터 최종퇴실 확인 등 기존 이용 규칙 유지. |

## 미확정 계약과 보류 범위

1. 사용자가 문의 후 알려주기로 한 세션 응답 id와 path meetingRoomId 및 기존 reservationId의 관계. UUID uid와 숫자 id를 동일시하지 않는다. ID 기반 실제 호출 연결은 답변 대기.
2. `/sessions/current`에 인증된 회의 세션이 없을 때의 HTTP 상태·code·data. 현재 제공된 발췌에는 정상 세션 응답만 있다. 무세션을 null/404 등으로 임의 정의하지 않는다.
3. 입장 거절 등의 오류 code 전체 목록은 미제공. 현재 임시 EntryReason과 서버 code를 임의로 동일시하지 않는다. 기존 공통 오류 처리와 서버 메시지 사용을 우선하되 특정 상태 분기가 필요하면 계약을 확인한다.
4. 회의 제목의 기존 meetingName 매핑은 서버의 같은 필드가 있어 재사용 후보다. 사용자 답변은 안건을 미입력으로 확정했으며 channelName의 제목 의미를 새로 확정한 것이 아니다.

## 보내는 작업의 위치와 변경 상태

- project/repository: asan-metaverse-user-ui / `/Users/okand/SynologyDrive/asan-metaverse-user-ui`.
- branch: `sy-main`.
- HEAD: `5df71dc0aed38ba793f5cb413b9bd2e2ce070bc1`.
- worktree/실행 디렉터리: `/Users/okand/SynologyDrive/asan-metaverse-user-ui`.
- 확인 시점: 2026-10-06 사용자 추가 계약 수신 후.
- 현재 작업의 완료 commit: 없음.
- staged: 없음.
- unstaged 기존 변경: `README.md`, `docs/meeting-api-contract.md`. 현재 세션의 소스 변경이 아니며 보존한다.
- git status에 표시된 untracked: 없음. 자기 세션 산출물은 별도로 존재한다.
- 다른 linked worktree: reservation-media-check, vo-participant-status가 존재한다. 해당 작업의 완료물을 이 checkout에 포함된 것으로 가정하지 않는다.

## 인계 대상 작업 공간

### 작업 공간: virtual-office-shared

- 기능: 가상 오피스 실 API controller와 최초 입장 통합 페이지의 순차 연결.
- 역할: Logic과 UI가 순차 사용.
- 목적지 repository/worktree/실행 디렉터리: `/Users/okand/SynologyDrive/asan-metaverse-user-ui`.
- 목적지 branch/확인 HEAD: `sy-main` / `5df71dc0aed38ba793f5cb413b9bd2e2ce070bc1`.
- 기존 공간이며 git status, rev-parse, worktree list로 확인했다.
- 직접 부모: 기준 branch sy-main이므로 이 작업의 자식→부모 병합 대상 없음.
- 공유 이유: 같은 UI/controller 계약을 순차 연결한다. 새 branch/worktree 생성은 요청되지 않았다.
- 진입 전 status/HEAD를 다시 확인하고 새 변경을 덮어쓰지 않는다. 기록 HEAD로 복원하지 않는다.
- Git 변경 승인: 없음. stage/commit/merge/worktree 생성은 별도 승인 대상이다.

## 역할별 상세 작업

### UI: 최초 입장 통합 페이지와 결과 안내

- 작업 공간: virtual-office-shared.
- `src/features/meeting-reservation/ui/entry/CodeMeetingConfirmPage.tsx`: 기존 회의 정보와 표시 구조를 통합 페이지의 재사용 후보로 조사한다.
- `src/features/meeting/ui/room/MeetingEntryNoticePopup.tsx`: 이용 가능 기능·최초 입장 안내 콘텐츠를 통합 페이지에 반영한다. 팝업의 모든 사용처를 확인한 뒤 예약 입장 흐름에서 중복 표시를 제거한다.
- `src/pages/meeting-reservation/ui/MeetingEntryRoute.tsx`: 통합 페이지와 controller를 연결한다. 기존 confirm 및 notice 분기를 독립적으로 중복 실행하지 않는다.
- `DeviceCheckView`, `MeetingRoomView`, 기존 공용 버튼·페이지 레이아웃을 재사용 후보로 조사한다. 디자인 선택·자산 선정은 UI 세션의 ui-library 문서에서 확정한다.
- 응답→표시 계약: firstEntry가 확정되어 true인 경우만 통합 페이지를 표시한다. 조회 중/실패를 false로 취급하여 건너뛰지 않는다. 회의 정보는 서버 필드 및 위 사용자 매핑을 따른다. 안건은 미입력이다.
- 입력→동작 계약: 통합 페이지의 확인/계속 동작은 controller가 제공하는 다음 단계 action에 연결한다. UI가 API 또는 join/leave를 직접 호출하지 않는다.
- firstEntry=false 재입장에서도 장치 검사 자체를 자동 생략하지 않는다. 사용자는 통합 안내 페이지의 표시 여부만 firstEntry로 결정하도록 했다.
- 오류 안내: Agora 연결 실패 후 정리는 정상 퇴장 성공으로 표시하지 않는다. 문구 후보는 `회의실에 연결하지 못했습니다. 다시 입장해 주세요.`이다. 이는 구현된 문구 또는 사용자가 확정한 정확한 문구가 아니다. 정상 퇴장·장치 검사 취소·연결 실패를 구분할 수 있는 controller 결과를 받는다.
- 첫 안내 페이지의 상세 위치/route 이름과 controller 공개 필드명은 미구현이다. 기존 confirm 위치 활용은 후보이며, 새 props가 이미 존재한다고 가정하지 않는다. 코드 작성 전에 Logic과 연결 순서를 맞춘다.
- 완료 기준: 최초/재입장, 로딩/오류, 계속/취소, 연결 실패 정리/정상 직접 퇴장의 표시를 구분하고 이용 안내가 중복되지 않는다.
- 검증: UI 변경 파일의 의미 있는 테스트와 공통 formatter 실행 후 lint/test/build. 사용자 요청 없는 캡처·시각 QA는 수행하지 않는다.

### Logic: 실 API·Query/Mutation·controller

- 작업 공간: virtual-office-shared.
- `src/features/meeting/api/entry/meetingEntry.api.ts`, `meetingEntry.dto.ts`: 임시 action/snapshot 계약을 서버 8개 연산별 DTO·응답 처리로 교체할 범위. 구현 전 미확정 ID/무세션 계약 해소가 필요하다.
- 공용 `shared/api/api-client.ts`, `axios-instance.ts`, 공통 응답 mapper와 오류 처리를 재사용한다. DTO에서 공통 envelope를 중복 정의하지 않는다.
- 도메인 hook에 Query/Mutation과 query key를 두고 signal, enabled, 최소 캐시 무효화·취소를 연결한다. proposal/vote/inquiry의 확인된 패턴을 따른다. 새로운 조회를 useApi로 다시 감싸지 않는다.
- `src/features/meeting/hook/useMeetingEntry.ts`: 기존 controller를 재사용·변경한다. 임시 viewer/heartbeat/snapshot에 대한 의존을 서버 계약에 맞게 교체한다. UID와 서버 시간을 보존하고 채팅·참여자 조회를 분리한다.
- `useAgoraMeeting`과 `useMeetingDeviceCheck`, RTC credential parser는 재사용 후보다. token 갱신은 같은 서버 join을 호출한다.
- 사용자의 입장 의도와 cleanup을 구분한다. Agora join 실패 시 원래 연결 실패를 보존하고 leave(finalExit=false) 결과를 정상 사용자 퇴장으로 보고하지 않는다. cleanup 자체 실패가 최초 원인을 덮지 않도록 처리한다.
- firstEntry 조회 결과를 UI에 제공하고 최초 안내 페이지와 callback 계약을 UI 세션과 맞춘다. 기존 UI가 선행하므로 기본 연결은 controller → UI이며, 이번 사용자 승인으로 두 UI 요소를 통합하는 변경이 추가되었다.
- role/status는 알려진 상수만 선언하고 미확인 문자열을 거절하지 않으며 원문 표시 모델로 전달한다.
- 참가자/채팅/로컬 RTC의 새 UID를 일관되게 사용한다. 사용자가 보류한 ID 관계는 별개의 문제로 남긴다.
- 검증: 실제 Axios 경계 요청 method/path/body, 공통 envelope, Query 취소·캐시, firstEntry 분기, 토큰 갱신, Agora 실패 cleanup과 직접 leave 결과 구분을 기존 Vitest/MSW 도구로 확인한다. 미확정 계약을 fixture로 채우지 않는다.
- 완료 기준: UI와 양방향 계약이 연결되고 임시 endpoint 대신 서버 연산을 사용하며 검증 결과를 남긴다. 현재는 아직 이 기준을 충족하지 않았다.

## 협업 순서와 Git 통합

- 현재는 문서만 인계한다. 실제 API 연결 완료물은 없다.
- 미확정 API 계약 해소 → Logic 공개 controller 계약 확정·구현 → UI가 통합 페이지 연결 → 합동 계약 검증 순서를 기본으로 한다.
- UI 세션이 먼저 화면 구조를 작업할 경우 실제 소스 수정 전에 진행 중인 Logic 편집 유무를 확인하고 props/callback을 맞춘다. 같은 worktree에서 동시 편집하지 않는다.
- 겹치는 지점은 MeetingEntryRoute의 controller 소비와 기존 useMeetingEntry 반환 계약이다. 기존 변경을 삭제하거나 타 세션 산출물을 수정하지 않는다.
- 새 Git 변경·병합은 실행하지 않았다. 같은 branch의 순차 작업에는 역할 전환을 위한 merge가 필요하지 않다.
- 산출물 책임: 현재 세션은 자기 handoff만 갱신한다. 다음 세션도 자기 산출물을 작성한다.

## 관련 스킬 및 검증 기록

- 공통 task-role-routing, git-branch-strategy, documentation, api-authoring/query-mutation/ui-controller를 참조했다.
- API 스킬에 생성·수정·삭제 캐시 지침이 존재하므로 조회 전용 문서라는 이유의 공용 보강 요청은 필요하지 않다.
- UI 세션은 ui-library 및 관련 UI 스킬을 읽고 자기 UI 자산 선정 문서를 작성해야 한다. 이 문서는 UI 디자인·자산 선정의 승인 계획이 아니다.
- 실행: Git 조회, 코드·스킬·기존 API 패턴 읽기. Swagger는 이전 조회에서 연결 시간 초과였으며 사용자가 제공한 발췌를 근거로 사용했다.
- 미실행: 소스 구현, formatter, lint/test/build, 실제 서버 기능 호출. 문서 전달을 구현·검증 완료로 해석하지 않는다.

## 다음 조치

- Logic: ID 관계에 대한 사용자 답변과 current 무세션 응답 확인.
- UI: 새 UI 역할 세션에서 이 문서와 현재 파일을 읽고 통합 페이지 작업 준비. API/화면을 미확정 mock으로 임의 완성하지 않는다.
