# 구현 로그

## 승인된 범위

승인 계약 `15a8ddfc98c0efd04037cc24229f76f9cd33b2817ee24209e48f04bebbd41b0d`의 문의 도메인, 공용 ApiClient, 문의 MSW·등록 파일, 문의 테스트 3개 및 현재 세션 산출물을 변경했다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `src/shared/api/api-client.ts` | PUT 전송과 ApiResult 변환 추가 | 기존 인증·오류 경계 재사용 |
| `src/entities/inquiries/api/` | JSON mutation 5개, 요청 DTO, 문자열 응답 parser, nullable 답변 | 사용자 제공 backend 계약 반영 |
| `src/entities/inquiries/model/inquiry.enum.ts` | 오래된 RESOLVED/CLOSED를 COMPLETED로 정합화 | 조회·변경의 상태 어휘 일치 |
| `src/entities/inquiries/model/inquiry-mutation-options.ts` | mutation 실행·성공 후 취소·무효화·제거 | 조회 캐시 동기화 |
| `src/entities/inquiries/hook/use-inquiry-mutations.ts`, `index.ts` | mutation hook 5개 공개 | UI에서 도메인 hook으로 요청 가능 |
| `src/mocks/inquiries.handlers.ts`, `src/mocks/handlers.ts` | 상태가 반영되는 mutation, 미답변 null, 공통 등록 | 개발용 실제 요청 경로 일치 |
| `tests/inquiries-*.test.mjs` | 계약, Axios/MSW, mutation 캐시 검증 | 문의 테스트 33개 통과 |

## 재사용한 자산과 새로 만든 자산

ApiClient·ApiResult·unwrapApiResult·withAbortSignal·inquiryKeys·공용 QueryClient 오류 처리를 재사용했다. 문의 mutation options는 HTTP 결과 처리와 캐시 작업을 도메인에서 조립하고 hook 및 실제 QueryClient 테스트가 동일한 설정을 사용한다. 공용 CRUD 추상화나 새 의존성은 추가하지 않았다.

## 핵심 로직·요청 처리

전송 전에 정수 ID와 요청 payload를 검증한다. status/content 이외 필드는 Zod 객체 파싱에서 제외한다. 답변 생성·수정의 body는 JSON `{ content }`이고 multipart·파일·이메일 필드는 제거했다. 응답의 문자열 data는 parser로 검증한 뒤 mutation 결과로 반환한다.

상태·답변 변경 성공 후 문의 목록과 해당 상세의 진행 중 조회를 취소하고 무효화한다. 활성 조회는 재조회되며 비활성 조회는 다음 사용 때 갱신된다. 문의 자체 삭제는 해당 상세를 취소·제거하고 목록만 무효화하여 삭제된 상세를 다시 요청하지 않는다. 다른 상세와 다른 도메인 캐시는 유지한다.

## 결정 사항

- 답변 없음은 사용자 확인대로 null을 보존한다. UI가 성공 조회의 null 답변에 NoResults를 표시한다.
- 답변 생성·수정·삭제로 문의 상태를 자동 변경하지 않는다. 상태 변경 API를 별도로 호출한다.
- MSW 데이터는 factory 단위로 격리하며 불변 갱신한다. answered는 answerContent 유무에서 계산한다.
- mock의 중복 답변 409, 답변 없음 404와 오류 코드·문구는 검증용 fixture다. 실제 서버의 미제공 오류 명세를 보장하지 않는다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `node --test tests/inquiries-contract.test.mjs tests/inquiries-msw.test.mjs tests/inquiries-mutation.test.mjs` 최초 실행 | 32 통과, 1 실패. 설치된 TanStack Query가 취소 시 이전 캐시 데이터를 반환하는 동작에 테스트 기대값을 수정 |
| `node --test tests/*.test.mjs` 최종 실행 | 106/106 통과, 문의 테스트 33개 포함 |
| `npm run build` | 통과. Vite 경로 플러그인·청크 크기 안내 존재 |
| `npm run lint` | 기존 파일에서 71 오류·5 경고. 이번 변경 경로에서는 발견 없음 |
| `./node_modules/.bin/eslint src/entities/inquiries src/shared/api/api-client.ts src/mocks/inquiries.handlers.ts src/mocks/handlers.ts` | 통과 |
| `git diff --check` | 통과 |

## 알려진 위험과 제한

실제 backend 및 화면 통합은 검증하지 않았다. 전체 lint 실패 경로는 sy-main 대비 변경이 없음을 확인했다. 현재 세션의 문서는 기존 `.gitignore`의 `.codex/` 규칙에 따라 로컬 산출물로 남는다.

## 다음 담당자 인계

`handoff.md`에 API·hook 매핑, 성공·오류·null 답변·삭제 후 이동 조건과 브랜치 소유권을 기록했다. 다음 역할은 ui이며 실제 JSX/CSS 변경은 수행하지 않았다.

검증된 소스·테스트 14개를 승인된 branch에 commit `98fc4624d4ff3f1257585373147fb137dcc54058`로 저장했다. 현재 세션의 8종 문서와 handoff는 기존 ignore 규칙을 유지하여 로컬에 보존했다.

## 후속 병합 완료

사용자가 Logic 작업의 sy-main 병합을 요청하고 완료 계약 SHA-256 `5dba11e389b14c7034d5f5e6e9e4a380911cd5e0bb511269794be64e4ed8298d`을 승인했다. sy-main으로 전환 후 finish → verify → close를 각각 실행하여 ff-only 병합, npm run build 통과, CLOSED 기록을 완료했다. 최종 sy-main HEAD는 `98fc4624d4ff3f1257585373147fb137dcc54058`이고 clean이다. cleanup false 계약에 따라 task branch는 보존했다.
