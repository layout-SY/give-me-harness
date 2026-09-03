# 로그인 기능 로직 계획

## 결론

로그인 API 계약을 Zod로 파싱하고, 성공 시 access token 저장과 `/login?access-token=<실제값>` replace 이동을 수행하는 mutation hook을 구현한다. Query string 노출 위험을 보고한 뒤 사용자가 해당 방식을 명시적으로 승인했다. 사용자가 임시 테스트 UI를 별도로 요청했으므로 production UI와 분리된 페이지에서 form·route·hook을 연결한다.

## 작업 구간

1. 기존 API, token, router, query 관례를 탐색한다.
2. 로그인 API와 mutation hook의 실패 테스트를 추가한다.
3. auth 전용 DTO, parser, Axios client, mutation hook을 구현한다.
4. token query 계약을 테스트 우선으로 변경하고 `URLSearchParams`로 실제 token 값을 인코딩한다.
5. 공용 `TextInput`과 `Button`을 사용한 임시 로그인 form을 테스트 우선으로 구현한다.
6. `src/App.tsx`에 `/login` route를 테스트 우선으로 등록한다.
7. 테스트, build, lint로 기능 로직을 검증한다.
8. 실제 서버 응답에서 비보장 profile 필드가 누락되는 경우를 재현하고 parser 계약을 최소 수정한다.
