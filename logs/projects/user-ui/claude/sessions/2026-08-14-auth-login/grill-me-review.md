# 로그인 기능 자체 검토

## 판정

기능 로직 PASS, production UI 통합 대기.

## 확인 사항

- 요청 body는 `email`, `password`, `language: "KO"`, `platform: "WEB"`로 고정된다.
- 응답 envelope와 사용자·token 필드를 런타임에 검증한다.
- 기존 공용 API 성공 판정 로직을 우회해 로그인 응답을 실패로 오판하지 않는다.
- access token 저장, query 인코딩, `/login` pathname, replace history를 사용자 동작 표면의 hook 테스트로 확인했다.
- 공용 input의 입력값이 submit handler를 통해 mutation으로 전달되는지 확인했다.
- App route가 `/login`에서 임시 페이지를 선택하는지 구조 테스트로 확인했다.
- 실제 서버 응답에 없는 profile 필드만 optional로 완화하고 사용자·token 필드는 필수 검증을 유지했다.
- 응답 값을 기본값으로 조작하지 않고 누락 상태를 타입에 그대로 보존했다.
- Query string 노출 위험을 사용자에게 알렸고 명시적으로 선택받았다.
- 관리자 프로젝트를 조회하거나 계약 근거로 사용하지 않았다.
- 임시 페이지는 `src/features/auth/testing/`에 두고 production `ui` 경로와 공용 UI는 수정하지 않았다.
