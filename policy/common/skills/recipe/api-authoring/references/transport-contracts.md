# 전송 계약과 검증 경계

## 표준 경로

`화면 → 도메인 hook / query·mutation options → 도메인 API factory → ApiClient → Axios`를 기본으로 사용한다. API factory는 React 상태, 모달, 라우팅, QueryClient를 소유하지 않는다. 기존 feature/entities 경계를 유지하고 앱에서 연결된 이웃 구현을 참조한다. 미연결 레거시 파일의 존재만으로 표준을 판단하지 않는다.

| 계층             | 책임                                       | 검토할 계약                                          |
| ---------------- | ------------------------------------------ | ---------------------------------------------------- |
| 요청 DTO·mapper  | 허용 필드 선택, ID·query·payload 검증      | 누락 / undefined / null, 배열 직렬화, 날짜·숫자 표현 |
| API factory      | URL·method·config·signal·body 연결         | 인증, path encoding, multipart 필드명                |
| 응답 parser      | unknown을 검증하고 UI 모델로 변환          | envelope, 목록·상세·mutation별 성공 body             |
| Query / mutation | 실패를 throw로 변환, 캐시·비동기 상태 소유 | key·retry·invalidation·오류 표시                     |

## ApiResult와 parser

- `ApiResult<T>` 타입 선언만으로 서버 응답이 검증되지는 않는다. 외부 값은 `unknown`에서 parser로 좁힌다. user-ui의 `mapApiResult(result, parser)`처럼 API 내부에서 검증하는 기존 경로도 허용한다. **Query 캐시나 UI 모델에 들어가기 전 정확히 한 검증 경계**를 두며 동일 응답을 중복 parse하지 않는다.
- Query 함수는 실패 `ApiResult`를 기존 `unwrapApiResult` / `ApiFailureError`로 throw해야 한다. `success: false`를 정상 캐시 데이터로 저장하지 않는다. 공유 unwrap이 있으면 재사용하고, 없으면 동일 도메인 helper들의 의미가 같은지 먼저 확인한다.
- `ApiResult` 반환 API도 HTTP·네트워크·취소에서 reject할 수 있다. 업무 실패 envelope와 reject 경로를 모두 검증한다. status·code·cause가 필요한데 `new Error(message)`만 남기지 않는다.
- 목록 pagination, empty 배열, nullable 상세, 문자열·boolean·void mutation은 각 endpoint 계약대로 파싱한다. 공통 mapper의 `data ?? undefined` 때문에 null이 사라지는 경로를 확인한다. 단일 범용 schema로 모두 맞추지 않는다.
- 응답이 없는 mutation과 응답을 검증하지 않는 mutation을 구분한다. UI에서 ID·완료 여부를 읽으면 그 필드를 검증한다. 빈 응답을 허용하려면 서버 계약 근거를 남긴다.

## 인증·취소·업로드

- `customConfig` 등 기존 인증 정책을 재사용한다. user-ui의 저장된 token 자동 부착과 admin-ui의 `authRequired` 지정은 서로 다른 계약이다. 하나를 다른 앱에 복사하지 않는다.
- Axios 호출은 `(url, body, config)` 순서를 확인한다. body 없는 POST도 인증 config를 두 번째 인자에 넣지 않는다.
- Query가 전달한 `signal`은 `withAbortSignal`을 거쳐 전송까지 연결한다. signal이 optional인 request에서도 전달받은 값은 버리지 않는다. 반복된 abort 변환 helper는 기존 shared helper로 공통화할 수 있는지 확인한다.
- ID가 자유 문자열이면 path segment encoding을 적용한다. 양의 정수 등 제한된 ID schema를 사용하는 경로는 해당 계약을 유지한다. 조회 filter와 multipart 배열의 직렬화 규칙은 endpoint별로 확인한다.
- FormData의 필드명·파일·JSON 문자열·반복 필드 순서는 서버 계약대로 만든다. 앱의 기존 Axios 변환 설정에서 multipart boundary가 실제로 생성되는지 검증한다. 인증·signal config를 함께 유지한다.

## 예외

- auth의 token 교환·refresh, RTC token 발급, meeting-entry의 timeout/heartbeat처럼 별도 lifecycle이 있는 전송은 근거가 있을 때 유지한다. 무조건 Query 또는 ApiClient로 옮기지 않는다.
- fetch 예외도 status 보존, abort·timeout 구분, 요청/응답 검증과 오류 표시 책임을 명시한다. SDK·same-origin 개발 endpoint와 실제 backend endpoint를 혼동하지 않는다.
- 개발 환경에서 실패를 mock 성공으로 바꾸는 transport fallback을 신규 표준으로 재사용하지 않는다. mock이 필요하면 승인된 계약의 MSW 경계에서 성공·실패를 명시적으로 선택한다.

## 검증 기준

요청 method·URL·인증 config·body·query serialization·signal을 실제 client 경계에서 확인한다. 의미 있는 응답 경계에는 성공·업무 실패·HTTP 실패·잘못된 body·취소를 포함한다. 테스트 때문에 실 API를 호출하거나 미확정 계약을 만들지 않는다.
