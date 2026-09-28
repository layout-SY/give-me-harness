# 문의 API·controller 최종 결과

## 제공 사항

`src/features/inquiry/`에 명세의 목록·상세·작성 API, DTO/Zod parser, query·mutation과 목록·상세·작성 controller를 구현했다. 최종 소스는 실제 Prettier 적용 후 lint·build와 문의 테스트 26개를 통과했다. 전체 테스트에서는 문의 외 시민참여 테스트 13개 실패가 남았다.

- `INQUIRY_TYPE_CODE`는 사용자 지시대로 `USER_SIGNUP` 한 항목만 `as const`로 둔다. `INQUIRY_STATUS`는 `OPEN`, `COMPLETED`다.
- 목록은 1-based `page=1`, `size=20`, `sort=createdAt,desc`를 기본값으로 사용하고 다중 정렬을 반복 `sort` 인자로 전달한다. 서버 응답 순서를 유지한다.
- 상세의 이전 문의와 관리자 답변은 각각 객체 또는 `null`로 보존한다.
- 작성은 허용된 네 필드만 명시적으로 매핑한다. 작성자 필드는 전송하지 않는다. 201/SUCCESS/data:null을 `void` 성공으로 처리한다.
- 인증, 요청 취소, 공통 envelope·pagination, 오류 변환을 기존 자산으로 연결했다. 작성 성공은 문의 목록만 무효화한다.
- 공개 진입점: `src/features/inquiry/index.ts`. `useInquiryListController`, `useInquiryDetailController`, `useInquiryWriteController`를 제공한다.
- 작성 controller는 RHF/Zod 필수 검증, 중복 제출 방지, 실패 시 입력 보존, 명시적 초기화와 mutation 성공 상태를 제공한다. 문의 유형을 자동 선택하지 않는다.

## 재사용과 범위

중앙 API 연결 스킬의 `ApiClient → DTO/parser → query·mutation → controller` 경계를 적용했다. `shared/api`의 client·인증·pagination·signal을 재사용하고, 기존 공지사항 전송 및 제안 폼의 RHF 패턴을 따랐다.

이번 세션의 소스 변경은 `src/features/inquiry/`의 15개 신규 파일이다. UI·라우트·공통 API·다른 기능 소스와 Git refs/index는 변경하지 않았다. 작업 중 `src/features/citizen-participation/`의 별도 미커밋 변경 14개가 관찰되었으며 그대로 보존했다.

## 검증

| 실행 | 결과 |
| --- | --- |
| 중앙 `formatting.py apply` 최초 실행 | 문의 소스 15개 파일 실제 Prettier 적용 성공 |
| `npm run test -- src/features/inquiry` | 2개 파일, 26개 테스트 통과 |
| `npm run build` 최종 실행 | 통과. 대용량 chunk 및 plugin 실행 시간 안내 출력 |
| `npm run test` 최초 sandbox 실행 | 96개 파일 중 90개 통과·6개 실패. 테스트 788개 통과·22개 실패·10개 건너뜀. 로컬 listen EPERM 오류 1건 |
| `npm run lint` 최초 실행 | 작성 controller의 `react-hooks/refs` 오류 1건. `form.handleSubmit` 생성·실행을 submit 이벤트 내부로 옮겨 수정함 |
| 수정 후 중앙 `formatting.py apply` | 변경한 작성 controller 포맷 성공 |
| `npm run lint` 최종 실행 | 통과 |
| `npm run test -- --maxWorkers=2` sandbox 밖 최종 실행 | 문의 테스트 26개 포함 807개 통과·13개 실패. 96개 파일 중 92개 통과·4개 실패. listen EPERM 해소 |
| `git diff --check` | 당시 추적 파일에 대해 통과. 신규 파일 검사는 lint/build로 수행해야 함 |

문의 테스트는 실제 Axios/MSW 표면에서 인증 config·URL·정렬·명시적 body·nullable·void·HTTP/업무 오류·네트워크·취소를 확인한다. Controller 테스트는 캐시 key, 목록 갱신 범위, ID 미선택, not-found, 필수 입력, 동시 제출, 실패 후 재제출을 확인한다.

최종 실패 경로와 근거:

- `src/features/citizen-participation/api/http/citizenParticipation.api.test.ts`: 1개 실패. `/citizen/votes/2/ballots`의 MSW handler 불일치.
- `src/features/citizen-participation/mocks/handlers.test.ts`: 3개 실패. 투표 응답 `choice` 검증 실패.
- `src/features/citizen-participation/mocks/browserHandlers.test.ts`: 8개 실패. 토론 요청을 upstream으로 보내야 한다는 테스트 기대와 wildcard mock 처리의 불일치.
- `src/pages/citizen-participation/ui/CitizenResultRoutes.test.tsx`: 1개 실패. 투표 완료 표시 기대와 실제 화면 불일치.

최초 실행에서 실패했던 제안 작성·예약 라우트 테스트는 최종 실행에서 통과했다. 변경 전 상태에서의 재현은 수행하지 않았으므로 남은 실패를 모두 기존 결함이라고 단정하지 않는다. 현재 `src/app`, `src/pages`에서는 문의 모듈 import·사용처가 검색되지 않았으며, 이번 소스 변경은 문의 신규 폴더에 한정된다.

## 동시 작업과 제한

- 다른 Codex 세션의 미확인 쓰기 4건으로 마지막 포맷이 잠시 차단되었다. 사용자도 다른 세션이 작업 중임을 확인했다. 기록이 해소된 실제 상태를 확인한 후 포맷·검증을 재개했으며 runtime 파일을 직접 수정하거나 guard를 우회하지 않았다.
- 실제 backend 호출과 화면 시각 검증은 수행하지 않았다. 문의 UI를 연결할 때 공개 controller를 소비하면 된다.
- UI·라우트 작성은 구현 범위에 포함되지 않는다. 남은 시민참여 테스트 실패는 해당 기능 작업에서 별도로 확인해야 한다.

## 후속 커밋

- 사용자 요청과 명령 실행 승인에 따라 `sy-main`에서 문의 신규 파일 15개만 커밋했다.
- 커밋: `d676dec` — `feat: 문의 API와 목록·상세·작성 controller 구현`.
- 다른 세션의 댓글 변경은 앞선 별도 커밋 `8ba021a`에 포함되었으며 이번 커밋에 섞이지 않았다.
- 중앙 보호 실행기 작업 `a03968d3e06f3357f9979e266706f4b2`가 `done`으로 완료됐다. Git 조회로 커밋 대상과 작업 트리 상태를 확인했다.
- HEAD 변경과 승인 대기 등록 순서, 중앙 잠금 파일의 sandbox 쓰기 제한으로 실행이 지연됐다. 최종 승인 후 같은 보호 실행기를 sandbox 밖에서 실행하여 완료했다. push·merge는 수행하지 않았다.
