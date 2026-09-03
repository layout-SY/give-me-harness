# 코드 선언 순서와 함수 명명 규칙

## 목적

파일을 열었을 때 구현 세부사항보다 주요 기능과 실행 흐름을 먼저 파악할 수 있도록 선언 순서를 통일한다. 함수명만 읽어도 대상과 수행 동작을 예측할 수 있어야 한다.

## 파일 선언 순서

```text
1. import
2. 공개 타입과 props 계약
3. 주요 exported 함수, Hook, 컴포넌트
4. 주요 기능이 사용하는 내부 도메인 함수
5. 하위 전용 컴포넌트
6. 포맷터, 변환기, reader, 상태 map 등의 유틸
```

타입은 주요 기능의 계약이므로 상단에 둔다. 유틸만 모인 파일은 공개 유틸을 먼저 배치하고, 해당 유틸이 공유하는 저수준 helper를 하단에 둔다.

## 주요 기능 판단

다음 중 하나에 해당하면 상단 기능 영역에 둔다.

- 파일 외부에서 직접 사용하는 exported 함수 또는 컴포넌트
- 사용자 동작이나 도메인 시나리오를 직접 수행하는 함수
- 해당 파일의 상태와 자원 수명주기를 조정하는 Hook
- 외부 SDK나 API의 핵심 경계를 구성하는 함수

날짜 포맷, 오류 문자열 변환, UID key 생성, JSON 필드 reader, Track 일괄 해제처럼 주요 기능을 보조하거나 여러 함수가 재사용하는 코드는 하단에 둔다.

## 함수 이름

- 25자를 넘지 않는다.
- 동사로 시작하고 대상 또는 결과를 포함한다.
- `get`, `set`, `handle`, `process`, `data`, `value`만으로 의미를 끝내지 않는다.
- 함수가 대신 수행하는 구체적인 동작을 이름에 담는다.
- 외부 이벤트 handler는 이벤트 대상과 행위를 함께 표현한다.

```ts
// 권장
joinRtcChannel()
bindRemoteVideoContainer()
parseHttpResponse()
formatMeetingExpiry()
removeSpeakingParticipant()

// 지양
startRtcSession()
setContainer()
parseData()
formatDateTime()
handleChange()
```

파일과 타입이 이미 충분한 문맥을 제공하면 중복 단어는 생략할 수 있다. 단, 호출부만 읽었을 때 대상이 모호해지면 도메인 이름을 포함한다.

회사 웹서버 경계의 타입과 변수는 `Request` 또는 `Response`를 붙인다. 파싱 후 애플리케이션 내부 모델로 변환한 값에서는 접미사를 제거한다. Agora UID는 현재 사용자면 `localUid`, 다른 참가자면 `remoteUid`, 양쪽 모두 가능하면 `participantUid`를 사용한다.

## 추출 기준

하단 배치는 별도 파일 추출을 의미하지 않는다. 호출처가 하나뿐이고 도메인 결합이 강한 helper는 현재 파일에 유지한다. 독립적인 책임 경계가 있거나 실제 재사용 호출처가 둘 이상일 때만 별도 모듈로 분리한다.
