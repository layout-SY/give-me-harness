# 최종 요약

## 무엇이 변경되었는가
- Agora Web SDK를 설치하고 회의 생성, 초대 코드 참가, publish/subscribe, 미디어 토글, 퇴장, Token 갱신 흐름을 구현했다.
- 실제 서버의 `/v1/api/admin/agora` endpoint, `data` envelope, `hostUserSeq/userSeq` DTO와 flat RTC credential 응답을 반영했다.
- API 응답 JSON을 직접 입력할 수 있는 개발 경로와 legacy normalized 응답 호환을 유지했다.
- join/leave 비동기 경쟁을 attempt id로 차단하고 모든 RTC 자원을 정리한다.
- Agora 연결 종료/재연결 상태와 원격 참가자 presence를 SDK 이벤트로 동기화한다.

## 왜 변경했는가
- 회의 메타데이터는 회사 서버가 관리하고 브라우저는 서버가 발급한 채널별 UID/RTC Token으로 Agora에 입장해야 한다.
- 실제 서버 문서와 초기 예상 계약이 달라 실제 endpoint와 응답 parser를 기준으로 교정했다.

## 재사용한 자산
- 기존 `VITE_API_BASE_URL` 환경변수 계약을 유지했다.
- 기존 `/docs` Swagger URL을 API origin으로 정규화한다.

## 영향받는 영역
- `src/features/meeting/**`
- `src/App.tsx`, `src/App.css`, `src/index.css`
- `package.json`, `package-lock.json`, `README.md`

## 검증
- `npm test`: pass (생성/초대 응답 파서 2건)
- `npm run lint`: pass
- `npm run build`: pass
- Watcher: pass
- Chrome 데스크톱에서 초기 화면, 반응형 제약, 필수 사용자 Seq 검증을 확인했다.
- Chrome 두 탭에서 서로 다른 UID로 같은 채널에 접속해 양쪽 원격 1명과 상대 영상 수신을 확인했다.
- 로컬 앱: `http://127.0.0.1:5173/`

## 남은 리스크
- 회사 서버의 초대 참가 API 성공 응답을 확인했지만, 유효한 다른 사용자 Seq가 없어 두 번째 RTC 클라이언트의 실제 입장까지 완료하지 못했다.
- 테스트에 사용한 `userSeq: 1`, `userSeq: 3`은 서버에서 `USER_NOT_FOUND`를 반환했다.
- 개발용 JSON의 화면 입력 userSeq는 credential을 변경하지 않는다. JSON에 포함된 host UID와 동일한 userSeq로 초대 참가하면 두 창이 동일 Agora UID를 사용한다.
- 제공된 RTC Token은 민감 정보이므로 테스트에 재사용하지 않았다.
- 실제 송수신과 Token 갱신은 유효한 새 credential과 2개 이상의 클라이언트에서 검증해야 한다.
- Agora SDK가 단일 청크에 포함돼 약 1.74MB 빌드 경고가 남는다.

## 후속 제안
- RTC 화면 route 단위 lazy loading으로 Agora SDK를 분리한다.
- 전용 RTC Token 재발급 endpoint를 서버에 추가한다.
- 로그인 연동 후 `hostUserSeq/userSeq` body 필드를 Access Token 기반 서버 식별로 전환한다.
- 두 브라우저 기반 실제 join/publish/subscribe/renew/leave E2E 시나리오를 추가한다.

## 발언자 강조 추가
- Agora `volume-indicator`로 음량 60 초과인 로컬·원격 UID를 발언자로 판정한다.
- 발언자 영상 타일에 녹색 발광 테두리를 표시하고 모션 감소 설정을 지원한다.
- 음소거·오디오 중단·퇴장·세션 종료 시 강조 상태를 정리한다.
- 발언 상태가 바뀐 타일만 다시 렌더되도록 UID 목록 동등성 검사와 원격 타일 memo 경계를 적용했다.
- 검증: `npm test` 4건, `npm run lint`, `npm run build` 통과. Agora SDK 청크 크기 경고는 기존과 동일하다.
- 개발 서버: `http://127.0.0.1:5176/`

## 구조 리팩터링 추가
- Agora 세션 orchestration, 로컬 미디어, 원격 참가자, SDK 이벤트 경계를 독립 모듈로 분리했다.
- 준비 UI 5개 섹션과 회의 UI 3개 섹션을 도메인 컴포넌트로 분리했다.
- README에서 상세 아키텍처 문서로 연결하고 RTC lifecycle 불변식을 문서화했다.

## 기능 우선 코드 구성 추가
- 주요 기능을 파일 상단에 배치하고 formatter, reader, key 변환, 오류 변환 유틸은 하단으로 이동했다.
- Hook과 UI callback 이름에 RTC 세션, 로컬 미디어, 원격 참가자 등 동작 대상을 명시했다.
- 함수명은 25자 이내로 제한하고 TypeScript AST 기반 검사로 초과 항목이 없음을 확인했다.
- 회의 API와 응답 parser를 분리하고 변경된 parser 이름을 테스트에 함께 반영했다.
- `docs/code-ordering.md`에 프로젝트 공통 선언 순서와 함수 명명 규칙을 추가했다.

## 통신 계약 문서 추가
- `docs/agora-rtc-contract.md`: Agora 호출, 반환 타입, 이벤트 payload, Track과 Token 수명주기.
- `docs/meeting-api-contract.md`: 회사 API endpoint, request/response, 정규화·호환·오류 규칙.
- README와 회의 아키텍처 문서에서 두 계약 문서로 연결했다.
- SDK 선언과 대조해 퇴장 사유, data channel config, 미사용 필드와 보안 경계를 구분했다.
- 검증 중 잔존한 과거 결합 타입 참조를 현재 회의 접근 정보 계약으로 통일했다.

## 회의 접근 정보 명명 추가
- 결합 타입은 `MeetingWithRtcCredential`, 내부 값은 `meetingAccess`로 통일했다.
- 회사 API 타입과 경계 값에 `Request`/`Response`를 적용하고 parser 이후에는 접미사를 제거했다.
- Agora UID는 현재 사용자 `localUid`, 원격 참가자 `remoteUid`, 양쪽 모두 가능한 값 `participantUid`로 구분했다.
- `Meeting`, Agora `Channel`, 브라우저별 RTC session의 개념 차이를 아키텍처와 계약 문서에 반영했다.
- 검증: `npm test` 6건, `npm run lint`, `npm run build` 통과. Agora SDK 청크 크기 경고는 기존과 동일하다.
