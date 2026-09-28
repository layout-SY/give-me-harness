# 출석·룰렛 API 구현 계획

## 활성 기본값 후속 수정 (2026-09-18)

사용자가 sortOrder 구현 확인과 isActive 기본값 false를 요청했다. 같은 Logic 역할·worktree에서 기존 공통 기본 필드·저장·목록 controller를 수정했다. sortOrder는 등록·수정 모두 전체 보상 배열의 index+1이며 날짜·DAILY/ACC별로 재시작하지 않는 구현을 확인하고 유지했다.

- 화면의 isActive는 boolean, 기본값 false다. 응답 null도 false로 표시하며 활성 토글을 항상 제공한다. 기본 정보의 null 활성 저장 차단을 제거했다.
- 서버 isActive가 null이면 다른 입력을 수정하지 않아도 기본값 false를 저장할 수 있다. 원본 API 응답 nullable 계약은 유지한다.
- 목록·상세 요약도 false로 기본 처리한다. 다른 필수값 검증은 유지한다.
- 수정 소스 4개와 tests/events-controller.test.mjs를 포맷했다. 관련 6개 테스트 파일 51 pass, lint·build·diff 검사 통과. 후속 수정 5개 파일은 미커밋 상태다.
- 같은 세션의 handoff·final-summary를 갱신한다. Git 변경은 이번 요청 범위가 아니다.

## UI 연결 후속 작업 (2026-09-17)

2026-09-18 완료: UI commit dad057f 위에 Logic 연결을 구현했다. 전체 39개 테스트 파일 271 pass, lint·타입 검사·build·diff 검사 통과. 사용자 승인 후 commit 1b8e733으로 39개 파일을 커밋했고 작업 트리가 깨끗함을 확인했다. 상세 변경과 사용법은 같은 폴더의 final-summary.md·handoff.md에 기록했다.

사용자가 UI commit `dad057f` 이후 Logic 연결을 승인했다. 같은 worktree·branch에서 controller·검증·payload·page·routes를 구현한다. 기존 UI 표현은 재사용한다.

- `src/entities/event`: 보상 DAILY/ACC, 설정 IMAGE/TEXT 타입 제한. configKey/configValue는 string 유지.
- `src/widgets/event-admin/{lib,hook}`: 기본 정보·설정·검색·요청 생명주기 공통 로직. 기존 날짜 유틸과 ImageModal 재사용.
- `src/pages/event-attendance`, `src/pages/event-roulette`: 보상 편집, 목록·등록·상세 controller와 페이지 진입.
- `src/app/router`: /events 라우트 및 이미지 모달 마운트.
- 재조회로 미저장 탭 초안을 덮어쓰지 않고 저장 성공한 탭만 초기화한다. IMAGE 저장은 TEXT 초안을 보존한다.
- 편집 가능 null 값은 빈 입력, 보완 불가능한 null 필드는 해당 탭 저장 차단과 사유 표시. 상세/items 응답은 같은 모델을 사용한다.
- 아이템 이름 검색은 page 1, size 5이며 최대 5건 표시한다(사용자 최종 답변).
- 날짜·ID 자동 입력, 보상 가져오기, config 전체 PATCH·업로드 순서, 오류·취소·캐시 동작을 기존 node:test/MSW/Vite 도구로 검증한다. 포맷 후 lint·build 및 관련 테스트를 실행한다.
- UI 인계 정본은 `.claude/logs/sessions/event-attendance-roulette-ui/handoff.md`이며 다른 세션 문서를 수정하지 않는다. 아래 최초 API 계약 중 type string 및 UI 범위 밖 기록은 이 후속 승인으로 갱신되었다.

## 목표와 승인

사용자 제공 명세의 출석 8개·룰렛 8개 API를 기존 ApiClient, Zod parser, TanStack Query 패턴으로 연결하고 UI 사용법을 인계한다. 역할은 inject로 확인된 Logic이며 산출물 책임은 owner다. 사용자가 `브랜치 분기해서 작업 진행`으로 구현을 승인했다.

## 작업 위치와 범위

- 저장소: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`
- 실행 worktree: `/private/tmp/asan-metaverse-admin-ui-event-api`
- branch: `feature/event-attendance-roulette-api`, 직접 부모: `sy-main`
- 분기 HEAD: `f3627abcd440709ccec1b98a6b37238fcf6936e2`
- Git 생성 작업 `2e739d191d444323915ac08560b9128e` 실행 완료. commit·merge는 요청되지 않았다.
- `src/shared/api/common/response.dto.ts`: 기존 페이지 DTO와 별도로 `{items,totalElements,totalPages}` 공용 타입·스키마 추가.
- `src/entities/event/`: DTO·parser·API, query key/options, mutation options, hook, 공개 export 구현. 개발 mock fallback 제거.
- `tests/`: 기존 node:test·tsx·MSW·Vite 테스트 구조에서 계약·오류·취소·캐시 검증. 이전 이벤트 계약 테스트를 새 명세로 갱신.
- 이 세션 폴더에 최종 요약과 사용법 handoff 작성.

## 확정 계약

- 요청은 PATCH를 포함해 명세 필드와 값 필수, null 불허. 목록 page·size 필수, page는 1부터.
- 응답 data와 내부 필드·배열은 nullable, 객체 필드는 반드시 존재. null을 빈 데이터로 대체하지 않는다.
- 기존 공용 envelope와 ApiClient는 재사용. 새 공용 페이지 DTO의 세 필드도 nullable로 정의한다.
- 명세에 전체 enum이 없으므로 type과 configKey는 string. configs의 key/value/type은 임의 문자열 허용.
- 등록 id는 출석 900·룰렛 901과 YYYYMM 조합. 코드 예시는 `2026_07_ATTENDANCE`. transport는 호출자 입력을 변환·생성하지 않는다.
- 보상 objectId는 이벤트 id와 별개이며 별도 조회·자동 매핑을 추가하지 않는다.
- 출석 설정 PATCH에는 configKey/configValue, 룰렛 설정 PATCH에는 type까지 필수.
- 업로드는 eventId와 multipart file, 반환 data는 `{url}`. 임의 파일 제한이나 보상 확률 검증을 추가하지 않는다.

## 재사용 근거와 스킬

`shared/api/api-client.ts`, `common/api-result`, `with-abort-signal.ts`, `axios.interface.ts`, `entities/items/api`·`model`·`hook`, `entities/news/api`·`model`, 기존 이벤트 API 및 참조 테스트를 조사했다. 이벤트 UI 호출부는 발견되지 않았고 기존 타입 테스트에만 직접 호출이 있다.

적용: task-role-routing, git-branch-strategy, coding-convention, data-fetch-layer, type-definition, abstraction-strategy, implementation-quality, documentation, api-authoring, reference/custom-hooks, skill-index. 정책 원본은 현재 세션에 바인딩된 중앙 snapshot이다.

## 실행 순서와 검증

1. 이 worktree에서 DTO·parser·API를 수정하여 명세와 null/필수 계약을 검증한다.
2. 기존 query/mutation 패턴으로 UI용 hook을 구현하고 이벤트별 캐시·취소를 검증한다.
3. 실제 Axios 경로를 통한 테스트용 MSW 응답으로 16개 요청, 인증, 업로드, 오류와 cache invalidation을 검증한다. 런타임 mock은 추가하지 않는다.
4. 공통 `formatting.py apply`로 수정 파일을 포맷하고 `node --test tests/*.test.mjs`, `npm run lint`, `npm run build`를 실행한다. package.json에는 test script가 없다.
5. 같은 branch/worktree에서 다음 UI 역할이 순차 연결할 수 있도록 API·hook 예시와 미확정 UI 사항을 handoff에 기록한다.

## 제한

UI·라우트·운영 서버 변경 및 실서버 데이터 수정은 범위 밖이다. 향후 UI의 objectId 선택 출처, 화면 입력·표시 정책은 이번 transport 구현에서 결정하지 않는다.
