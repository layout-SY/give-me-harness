# 평가 로그

## 컨텍스트
- 대상: Agora 화상회의 feature watcher pass 이후의 장기 구조 평가
- 읽은 문서: `plan.md`, `exploration.md`, `implementation-log.md`, `review-log.md`, `README.md`
- 읽은 코드: `src/features/meeting/**`
- 적용 기준: `policy-documentation`, `policy-abstraction-strategy`, `policy-review-checklist`, evaluator contract
- 전제: watcher pass는 현재 구현 범위의 품질 게이트 통과로 존중한다. 이 문서는 pass/fail 재판정이 아니라 현재 범위를 넘어서는 구조 리스크와 후속 백로그만 기록한다.

## 결론
- 현재 구현은 단일 Agora 회의 데모/검증 화면으로는 응집도가 높고, API 파싱 경계와 RTC 수명주기 훅의 책임 분리가 명확하다.
- 다만 운영 기능으로 확장할 때의 핵심 리스크는 `Agora SDK 번들 크기`, `join API를 재사용하는 token refresh 의미`, `userSeq 임시 인증의 제거 비용`, `실제 서버/다중 클라이언트 검증 부재`, `endpoint/API DTO 변경 가능성`이다.
- 현재 단계에서 공용 컴포넌트나 공용 RTC 추상화를 선제 도입할 필요는 낮다. 다음 단계는 추상화보다 먼저 서버 계약 확정, 인증 전환 경계 정의, 라이브 검증 체계 확보가 우선이다.

## 진단 요약

### 의존 관계
- `App.tsx`는 `MeetingPage`를 정적으로 import하고, `MeetingPage`는 UI 컴포넌트, form validator, API service, `useAgoraMeeting`을 조립한다.
- Agora SDK 직접 의존은 `src/features/meeting/hooks/useAgoraMeeting.ts`에 갇혀 있어 UI 컴포넌트가 SDK 타입에 직접 결합하지 않는다.
- API 의존은 `src/features/meeting/services/meetingApi.ts`에 모여 있고, `MeetingPage`는 `createMeeting`, `joinMeeting`, `refreshMeetingRtcToken`만 호출한다.
- 장기 리스크: `App.tsx -> MeetingPage -> useAgoraMeeting -> agora-rtc-sdk-ng` 정적 import 흐름 때문에 회의 화면이 앱 첫 화면 번들에 포함된다.

### 추상화 수준
- 현재는 단일 feature 내부 계약 중심 설계다. `MeetingWithRtcCredential`, `RtcCredential`, form request, API parser는 계약 역할을 하고, 강한 추상화까지는 아니다.
- 추상화 4조건 기준으로 공용 RTC adapter는 아직 소비자 수가 1개이므로 YAGNI에 가깝다.
- 단, 불안정 영역은 명확하다. Agora SDK 로딩/RTC client 생성, 서버 RTC credential 계약, 인증 전환은 변동 가능성이 높아 다음 단계에서 안정 경계 후보가 된다.

### SOLID
- SRP: form 검증, API 파싱, RTC 수명주기, UI 렌더링이 분리되어 현재 범위에서는 양호하다.
- OCP: 서버 응답 shape 변화에는 `parseMeetingApiResponse` 계층을 수정해야 하므로 확장 지점은 있으나 schema 기반은 아니다.
- LSP/ISP: 외부에 노출된 인터페이스가 작고 도메인 전용이라 대체 가능성 문제는 낮다.
- DIP: UI는 SDK에 직접 의존하지 않지만 `useAgoraMeeting`은 Agora SDK concrete에 직접 의존한다. 운영에서 SDK 교체/모킹/테스트가 필요해지면 adapter 경계가 필요하다.

### KISS
- 현재 직접 구현은 단일 화면 목적에 맞다. 공용 레이어가 부족해서 생기는 문제보다, premature abstraction이 생길 경우의 비용이 더 크다.
- 개발용 JSON 입장과 legacy normalized shape 지원은 검증 편의성 측면에서는 단순하지만, 장기적으로는 운영 코드와 테스트 우회 경로가 섞일 수 있다.

### YAGNI
- 지금 당장 공용 화상회의 프레임워크, 다중 provider RTC abstraction, 전역 상태 도입은 불필요하다.
- 반대로 chunk split, 인증 경계, API 계약 테스트, 다중 클라이언트 검증은 "미래 가능성"이 아니라 운영 전환 조건이므로 백로그로 올릴 가치가 있다.

### 객체 지향 관점
- RTC 수명주기는 hook 내부 ref와 상태로 캡슐화되어 있고, attempt id로 join/leave 불변식을 관리한다.
- 불변식은 코드 내부 절차로 표현되어 있어 현재는 충분하지만, 화면 공유/녹화/권한 단계가 추가되면 명시적 state machine 또는 RTC session adapter로 책임 재할당을 검토해야 한다.

### 코드베이스 수준
- 현재 feature 완성도: B+.
- 운영 준비도: B-.
- 감점 이유는 구현 결함보다 외부 계약/검증/번들 전략의 미확정이다. 근거는 `review-log.md`의 1,738.33 kB chunk 경고, `README.md`의 인증 미연동/refresh endpoint 부재 명시, `implementation-log.md`의 실제 송수신 검증 한계 기록이다.

## 구조적 리스크

1. Agora SDK 1.7MB 단일 chunk
- 근거: `review-log.md`는 `npm run build` pass와 함께 `dist/assets/index-*.js` 1,738.33 kB 단일 chunk 경고가 유지된다고 기록한다.
- 코드 흐름: `src/App.tsx:1`이 `MeetingPage`를 정적 import하고, `src/features/meeting/hooks/useAgoraMeeting.ts:2`가 `agora-rtc-sdk-ng`를 정적 import한다.
- 리스크: 회의 기능이 아닌 초기 진입에서도 Agora SDK가 로드될 수 있다. 현재 단일 demo 앱에서는 허용 가능하지만, 관리자 UI의 여러 화면 중 하나가 되면 초기 로딩 성능과 캐시 무효화 비용이 커진다.
- 방향: route-level lazy loading 또는 `joinSession` 시점의 dynamic import로 SDK chunk를 분리한다. 단, SDK 타입/adapter 경계는 실제 라우팅 구조가 생긴 뒤 적용한다.

2. token refresh가 join API 재사용에 묶임
- 근거: `README.md:64`-`README.md:68`은 별도 refresh endpoint 없이 기존 회의 join API를 다시 사용한다고 명시한다. 구현도 `src/features/meeting/services/meetingApi.ts:287`에서 `/meetings/:id/join`을 refresh 함수로 호출한다.
- 리스크: join이 서버에서 참가 이력 생성, presence 갱신, role 재계산, 중복 참가 처리 같은 side effect를 가진다면 token renew 이벤트마다 join 의미가 반복된다.
- 현재 구현상 refresh callback은 갱신 응답의 `rtcCredential`을 받아 `renewToken`에 사용하고 `session`도 갱신한다. 서버가 join과 renew를 분리하면 DTO와 endpoint가 동시에 바뀐다.
- 방향: 백엔드 계약에서 `/join` 재사용이 idempotent token renew인지 명시하거나, 별도 `/rtc-token/refresh` 계열 endpoint를 요구한다.

3. userSeq 임시 인증에서 Access Token 기반 인증으로 전환할 때의 제거 비용
- 근거: `README.md:22`는 Access token 선택 입력을 명시한다. `src/features/meeting/model/meetingForms.ts:30`과 `src/features/meeting/model/meetingForms.ts:90`은 `userSeq`를 필수 검증하고, `src/features/meeting/types.ts:33`, `src/features/meeting/types.ts:38`, `src/features/meeting/types.ts:42`가 payload에 `hostUserSeq/userSeq`를 포함한다.
- 리스크: 인증이 JWT/Access Token 기반으로 전환되면 사용자 식별자는 UI 입력값이 아니라 인증 컨텍스트 또는 서버 추론 값이 된다. 현재는 UI, validator, DTO, refresh callback에 `userSeq`가 퍼져 있어 제거 시 여러 경계를 동시에 수정해야 한다.
- 방향: 다음 단계에서 `AuthenticatedMeetingActor` 같은 내부 계약을 두고, 전환기에는 `userSeq` 입력과 Access Token claim을 adapter에서만 매핑한다. 운영 전환 후에는 body의 `userSeq` 제거 여부를 서버 DTO와 함께 확정한다.

4. 실제 서버/다중 클라이언트 검증 부재
- 근거: `exploration.md`와 `implementation-log.md`는 실제 Agora 자격 증명, 브라우저 미디어 권한, 2개 이상 클라이언트 없이는 완전 검증이 불가능하다고 기록한다. `review-log.md`도 라이브 미디어와 token refresh가 code-inspection verified 상태라고 남긴다.
- 리스크: `user-published`, `user-unpublished`, token will/did expire, 권한 거부, 장치 점유, 다중 참가자 join/leave 순서 같은 문제는 정적 검토와 build pass로 충분히 검증되지 않는다.
- 방향: staging credential 기반 2-client 수동 검증표와 fake media 기반 자동 smoke test를 분리한다. 특히 token 만료 시간을 짧게 설정한 refresh 검증 세션이 필요하다.

5. endpoint/API DTO 변경 가능성
- 근거: `src/features/meeting/services/meetingApi.ts:125` 이후 parser는 실제 envelope + flat credential shape와 legacy normalized shape를 동시에 지원한다. `README.md:76` 이후 성공 data shape도 서버 계약에 강하게 의존한다.
- 리스크: `meeting.seq`, `rtcToken`, `expiresAt`, `scheduledEnd`, `uid` 타입 중 하나가 바뀌면 runtime parser가 null을 반환하고 일반 오류 메시지로 떨어진다. 현재는 방어적 파싱이 장점이지만, 계약 변경 감지는 런타임 사용자 경로에 늦게 나타난다.
- 방향: OpenAPI/fixture 기반 contract test를 도입하고, parser fixture를 `create`, `invite join`, `meeting id join(refresh)` 3개 케이스로 고정한다. DTO 변경은 feature 코드 수정 전에 contract diff로 먼저 잡아야 한다.

6. 개발용 JSON 입장 경로의 운영 잔존
- 근거: `README.md:109`-`README.md:111`과 `src/features/meeting/MeetingPage.tsx:142` 이후가 개발용 JSON 입장을 유지한다.
- 리스크: QA와 개발에는 유용하지만 운영 관리자 화면에 남으면 실제 인증/API 경로를 우회하는 디버그 표면이 된다.
- 방향: 환경 플래그로 개발용 진입을 제한하거나, 운영 전 배포 정책에서 제거 조건을 명시한다.

## 개선 옵션

1. 최소 운영 전환 옵션
- Agora SDK chunk split을 적용한다.
- Access Token 필수화 시점에 `userSeq` 입력을 제거한다.
- `/join` 기반 refresh가 idempotent인지 서버 문서에 고정한다.
- staging 실서버 2-client 검증표를 작성한다.

2. 계약 안정화 옵션
- API fixture contract test를 먼저 만든다.
- `CreateMeetingRequest`, `JoinMeetingRequest`, `RefreshRtcTokenRequest`를 서버 DTO 변경 단위에 맞춰 versioned adapter로 감싼다.

## 회의 접근 정보 명명 평가
- `MeetingWithRtcCredential`은 지속되는 Meeting, Agora Channel, 클라이언트 RTC session을 혼동하지 않고 데이터 구성을 직접 표현한다.
- 서버 경계의 Request/Response 접미사는 wire contract와 내부 도메인 모델의 변환 위치를 드러낸다.
- `localUid`, `remoteUid`, `participantUid` 구분으로 이벤트 처리와 UI 표시에서 UID 소유자를 호출부만 보고 판단할 수 있다.
- legacy normalized JSON 지원은 개발 전용 adapter로 격리한다.

3. 확장 대비 옵션
- 회의 기능이 관리자 앱의 여러 route 중 하나가 되는 시점에 `MeetingPage` route lazy loading을 적용한다.
- 화면 공유, 녹화, 권한 역할 분기가 추가될 때 `useAgoraMeeting` 내부 절차를 `RtcSessionAdapter` 또는 명시적 state machine으로 분리한다.
- 다만 현재 소비자가 1개인 동안 전역 공용 RTC abstraction은 만들지 않는다.

## 권장 백로그

1. P0 - 라이브 검증 매트릭스 작성
- 실제 서버 + 실제 Agora credential + 2개 브라우저/장치 기준으로 create, invite join, leave, reconnect, remote publish/unpublish, permission deny, token renew를 검증한다.

2. P0 - token refresh 서버 계약 확정
- `/v1/api/admin/agora/meetings/:id/join` 재사용이 idempotent renew인지 확인한다.
- side effect가 있다면 별도 refresh endpoint를 백엔드 backlog로 등록한다.

3. P1 - Access Token 전환 설계
- `userSeq` 입력 제거 시나리오를 정리한다.
- 서버가 사용자 식별을 Access Token에서 추론하는지, 전환기 동안 body field가 유지되는지 DTO 정책을 확정한다.

4. P1 - Agora SDK lazy loading
- `App.tsx` 정적 import 구조에서 route-level 또는 interaction-level chunk split으로 전환한다.
- build budget 기준을 문서화하고 1.7MB chunk 경고를 추적한다.

5. P1 - API contract fixture test
- 생성, 초대 참가, meeting id join(refresh), legacy JSON fixture를 분리한다.
- endpoint path, required body, response parser가 서버 계약 변경에 즉시 실패하도록 만든다.

6. P2 - 개발용 JSON 입장 운영 제한
- production build에서 숨김 또는 제거하는 정책을 정한다.
- README에 개발 전용 조건과 제거 기준을 추가한다.

7. P2 - RTC adapter/state machine 검토
- 화면 공유, 녹화, moderator role, device selector 중 하나 이상이 추가될 때 진행한다.
- 현재 단계에서는 YAGNI로 보류한다.

## planner 이관 여부
- optional: true
- 이유: 지금 즉시 구현할 항목은 아니지만, 운영 전환 milestone을 만들 때 P0/P1 백로그를 planner가 작업 단위로 쪼갤 수 있다.

## 다음 단계 제안
- 다음 작업은 코드 리팩터링보다 `실서버 2-client 검증`과 `token refresh 계약 확정`을 먼저 잡는 편이 낫다.
- 그 다음에 `Access Token 전환 설계`와 `Agora SDK lazy loading`을 별도 작업으로 분리한다.

## 상태
- status: recommendation_ready

## 발언자 강조 기능 평가
- 기존 RTC 훅과 영상 타일을 재사용해 새로운 전역 상태나 공용 컴포넌트를 만들지 않았다.
- 현재 회의 최대 인원 16명과 SDK 2초 보고 주기에서는 UID 목록 비교와 타일별 memo로 충분하다.
- 임계값 60은 SDK 권장값이며, 실제 회의 환경에서 감도가 낮거나 높으면 도메인 상수만 조정할 수 있다.
- 더 빠른 반응을 위한 Web Audio API 병행은 오디오 분석 비용과 구현 복잡도가 증가하므로 현재 범위에서는 보류한다.

## 관심사 분리 리팩터링 평가
- `useAgoraMeeting`은 orchestration facade로 남고 장치, 참가자, SDK callback 세부 구현을 직접 소유하지 않는다.
- event adapter는 외부 SDK 변경을 흡수하는 안정 경계이므로 추상화 4조건 중 불안정 영역 경계와 인지 부하 감소를 충족한다.
- 준비·스테이지 하위 컴포넌트는 단일 화면 전용이므로 meeting 도메인 밖 공용 계층으로 승격하지 않았다.
- 신규 도메인 Hook은 전역 재사용 자산이 아니므로 `.codex/memory/reusable-assets.md`에는 등록하지 않는다.
- 향후 화면 공유나 장치 선택이 추가되기 전에는 더 작은 범용 Hook으로 분해하지 않는다.

## 코드 읽기 순서 및 명명 평가
- 공개 기능을 먼저 배치해 파일 첫 화면에서 사용자 동작과 도메인 책임을 파악할 수 있다.
- 유틸은 하단에 유지하되 이름에 변환 대상과 결과를 포함해 호출부 문맥 의존도를 낮췄다.
- API parser 분리는 외부 응답 계약이라는 독립 책임이 있어 과잉 추상화에 해당하지 않는다.
- 함수명 25자 제한은 자동 감사 가능하지만 축약으로 의미가 손실되지 않는지를 코드 리뷰에서도 함께 확인해야 한다.

## 데이터 계약 문서 평가
- Agora 계약과 회사 API 계약을 분리해 외부 시스템별 변경 영향을 추적할 수 있다.
- 서버가 반환하지만 프론트가 사용하지 않는 필드를 구분해 문서가 서버 전체 DTO를 과장하지 않는다.
- 현재 문서는 수동으로 코드와 동기화해야 하므로 후속 단계에서는 fixture 또는 타입에서 표를 검증하는 contract test 확대가 유효하다.
- OpenAPI가 안정화되면 회사 API 문서의 request/response schema를 자동 생성 문서와 대조해야 한다.
