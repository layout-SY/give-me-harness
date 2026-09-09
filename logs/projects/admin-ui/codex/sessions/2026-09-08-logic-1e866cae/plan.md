# 계획

## 목표

사용자가 제공한 `/admin/news` 5개 API 명세로 공지사항 요청·응답 DTO와 데이터 흐름을 구현하고 기존 수정 폼을 연결한다.

## 작업 유형

feature

## 범위

- `src/entities/news`: 기존 사용처가 없는 `/v1/news` 구현을 공용 ApiClient 기반 목록·상세·등록·수정·삭제, Zod DTO/parser, query key와 query/mutation hook으로 교체한다.
- 승인된 `src/pages/cp-board` 공지 폼 hook/model/config와 `src/entities/cp-notice/model/types.ts`: 숫자 newsId 상세 조회와 제목·본문·상태 저장을 연결한다. 유형과 상단고정 값은 변경하지 않는다.
- `src/mocks/news.handlers.ts`, `tests/news-*.test.mjs`: 실제 Axios·MSW 표면의 계약, 필터·상단고정·부분 수정·삭제·오류·취소·캐시·폼 매핑을 확인한다.
- 현재 assignment 산출물은 `.codex/logs/sessions/2026-09-08-logic-1e866cae`에 작성한다. 이전 세션 디렉터리에 쓰지 않는다.

## 제외 사항

혼합 게시글 목록의 UI 개편, 신규 등록 화면·라우트, 유형·상단고정 입력 UI, legacy 댓글·일괄 변경 API, 공통 MSW 등록은 현재 branch scope에 없다. 새 news handler는 테스트에서 명시적으로 사용한다.

## 제약 조건

- API 명세의 원문 필드와 상태만 사용한다. 목록의 `totalElements`, `totalPages`, `pinnedItemCount` 및 서버 정렬 순서를 보존한다.
- `by`와 `keyword`는 함께 입력하고, page/size 기본값은 1/20이다. sort는 반복 query parameter로 전송한다.
- PATCH는 입력한 필드만 전송하며 `false`도 유지한다. mutation의 raw data는 null이고 공용 ApiResult가 이를 undefined로 바꾸는 기존 계약을 수용한다.
- 작성자·노출 기간·메인 노출은 서버 미지원으로 표현한다. 메인 노출을 `isPinned`로 임의 해석하지 않는다.
- 한 번에 한 논리 구간씩 구현한다. 원격 호출·시각 QA·자동 merge는 하지 않는다.

## 스킬 및 역할

- 확인된 역할: logic (inject)
- 사용자 확인: 빈 기존 브랜치를 사용해 구현하자는 질문에 2026-09-08 “작업해봐”라고 승인했다.
- Git 통합 담당자: codex
- 산출물 책임: owner
- branch: `task/connect-news-api`, parent/merge target: `sy-main`, 시작 HEAD: `98fc4624d4ff3f1257585373147fb137dcc54058`
- branch 계약 SHA-256: `c4140e0c302e4bc5997976534b43464e897661097924db03c1b8343000ef7ccd`

| 작업 구간 | 역할 | 방법 | 기대 결과 |
| --- | --- | --- | --- |
| news API·DTO | Logic | 기존 inquiries 구조와 공용 ApiClient 재사용 | 실제 5개 API 명세 반영 |
| query/mutation | Logic | TanStack Query·취소·최소 무효화 | 오래된 조회가 저장 결과를 덮어쓰지 않음 |
| 기존 수정 폼 | Logic | 서버 DTO와 표시 모델 분리 | 지원 필드 저장·미지원 필드 안내 |
| 검증·기록 | Logic | Node test·MSW·lint·build | 실행 근거와 UI 후속 계약 |

## 검증

기존 도구로 `node --test tests/news-contract.test.mjs tests/news-form.test.mjs tests/news-msw.test.mjs tests/news-mutation.test.mjs`, 전체 `node --test tests/*.test.mjs`, `npm run lint`, `npm run build`를 수행한다. package.json에는 test script가 없다.

## 위험 요소 및 결정 사항

기존 화면이 NT-형식 mock ID와 별도 cp-board 데이터에 의존한다. 실제 news ID로 수정 경로에 진입해야 하며 목록·등록 UI 연결은 handoff에 기록한다. 상단고정 카운트와 일반 목록의 total 계산 관계는 명세에 명확히 정의되지 않았으므로 실제 응답 숫자를 재계산하지 않는다.

## 승인

- 상태: 사용자 구현 승인 확인. 기존 V3 source scope 안에서 진행한다.
- 요청 명확성: clear, can_proceed: true
- 역할·구현 확인 문구: 이 역할과 계획대로 진행할까요, 아니면 조정할 부분이 있나요?
