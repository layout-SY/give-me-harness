# 계획

## 목표와 승인

기존 승인된 `/admin/news` 목록·등록·상세·삭제·부분 수정 5개 API를 구현하고 기존 공지 수정 폼의 제목·본문·게시 상태를 연결한다. 이전 handoff와 사용자 원문 명세를 읽었으며 현재 사용자가 작업 재개를 지시했다. 구현·스킬·탐색 gate 등록을 확인했다. 요청 명확성은 clear, can_proceed: true다.

- 역할: logic, Git 통합 담당자: codex, 책임: owner
- assignment: adc9f97a68614efa9180b7a90cbf7681
- branch: task/connect-news-api, 상태: ACTIVE, parent/merge target: sy-main
- 시작 HEAD: 98fc4624d4ff3f1257585373147fb137dcc54058
- V3 계약 SHA-256: c4140e0c302e4bc5997976534b43464e897661097924db03c1b8343000ef7ccd
- 산출물: 현재 디렉터리만 작성한다.

## 구현 순서와 완료 기준

1. `src/entities/news`에서 ApiClient·Zod·TanStack Query 인접 패턴으로 DTO, parser, 5개 전송 함수, query/mutation을 작성한다. 목록 순서·서버 집계, 검색 쌍, 반복 sort, 부분 수정의 false/미입력, AbortSignal과 최소 캐시 무효화를 보존한다.
2. 승인된 공지 폼 hook/lib/model/config와 `cp-notice/model/types.ts`에서 숫자 ID 조회와 제목·본문·상태 저장을 연결한다. 명세에 없는 작성자·노출 기간·메인 노출은 미지원으로 표시한다. mainExposure를 isPinned로 해석하지 않는다.
3. `src/mocks/news.handlers.ts`와 지정된 `tests/news-*.test.mjs`에서 Axios·MSW 계약, 폼 매핑과 캐시 race를 검증한다. 전체 Node test, lint, build를 수행한다.
4. Watcher 판정·평가와 owner 8종 문서 및 UI 후속 handoff를 기록한다. 검증 후 commit과 완료 proposal을 준비하고 별도 병합 승인을 받는다.

## 대안과 경계

기존 mock API URL만 교체하면 translations와 폼 필드 계약이 달라 오동작한다. DTO부터 기존 실 API 패턴으로 교체하는 승인안을 유지한다. 공용 API/훅 추상화와 패키지는 추가하지 않는다.

혼합 게시글 목록·신규 등록·유형·상단고정 UI와 공통 MSW registry는 후속 scope다. 현재 handler는 테스트에서 명시적으로 사용한다. 기존 수정 라우트는 `/cp/boards/notices/:noticeId/edit`이며 실제 숫자 ID로 진입해야 한다.

## 검증

`node --test tests/news-contract.test.mjs tests/news-form.test.mjs tests/news-msw.test.mjs tests/news-mutation.test.mjs`, `node --test tests/*.test.mjs`, `npm run lint`, `npm run build`. test script는 없다. 실서버 요청과 시각 QA는 수행하지 않는다.
