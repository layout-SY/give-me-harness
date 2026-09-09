# 검토 로그

## Watcher 판정

PASS

## 검토 범위

로그인 요청이 `{ loginId, password }`이고 `POST /auth/login`을 인증 없이 호출하는지, 성공 시 액세스·리프레시 토큰과 `expiresIn`을 저장한 뒤 만료 전에 `POST /auth/refresh`를 치는지, 로그인 UI가 이메일이 아닌 아이디 문자열인지.

## 점검 항목

| 점검 | 결과 | 근거 |
| --- | --- | --- |
| 목표 충족 | PASS | DTO·API·mutation·폼이 `loginId`와 `/auth/login`을 쓰고, 세션이 `expiresIn` 30초 전에 refresh한다. |
| 승인 근거 | PASS | 사용자 지시 `이를 반영해` 이후 구현했다. |
| 불러온 스킬 | PASS | data-fetch-layer, api-authoring, type-definition, publishing, documentation을 적용했다. |
| `src/shared/ui/` 재사용 | PASS | 기존 `TextInput`/`Button`을 유지했다. |
| 타입 안전성 | PASS | `npm run build`의 `tsc -b`가 통과했다. |
| 요청 데이터 완전성 | PASS | 로그인 본문은 `loginId`/`password`만 보낸다. language/platform을 붙이지 않는다. |
| 중복/추상화 | PASS | 토큰 파싱은 login/refresh가 같은 envelope를 쓴다. JWT exp 유틸은 쓰지 않는다. |
| 검증 | PASS | auth 테스트 7건, build, lint 성공. |
| 문서화 | PASS | 세션 산출물 8종을 이 디렉터리에 작성한다. |

## 발견 사항

| 심각도 | 경로 | 발견 사항 | 필수 조치 |
| --- | --- | --- | --- |
| 없음 | - | 로그인에 Bearer가 붙거나 이메일을 검증하는 현재 결함은 확인되지 않았다. | 없음 |

## 결론

현재 작업 범위에서 로그인은 무인증 `loginId` 계약이고, 액세스 토큰은 만료 전에 refresh로 유지된다.
