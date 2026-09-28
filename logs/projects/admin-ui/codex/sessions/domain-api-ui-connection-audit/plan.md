# 계획

## 목표

현재 구현된 도메인 API 중 실제 라우팅된 UI에서 호출되지 않는 함수를 확인하고 근거를 보고한다.

## 작업 유형

- 초기 API 연결 현황·패턴 비교는 audit-only, 후속 사용자 승인 범위는 소포 API Logic 구현.

## 범위

- 작업 위치: /Users/okand/SynologyDrive/asan-metaverse-admin-ui
- 브랜치: sy-main
- 기준 HEAD: 0e7c671b511f8e6cecebcce8946a13ee24d8c339
- src/entities 아래 API 함수, API singleton, query/mutation hook, 페이지 controller 및 src/app/router/routes.tsx를 추적한다.
- src/features/meeting의 별도 API와 src/entities/vo의 DTO·fixture를 보조 확인한다.
- 함수 정의·export·테스트 참조만으로 UI 연결을 판정하지 않고, 라우팅된 페이지에서 실행할 수 있는 호출 경로를 확인한다.

## 제외 사항

- 초기 조사에서는 API 또는 UI 구현 변경, 삭제, 서비스 계약 결정, Git 변경을 제외했다. 이후 소포 Logic 추가만 별도로 승인되었다.
- 다른 branch/worktree의 미통합 구현
- 서버 호출, 브라우저 캡처, 배포 환경 동작 검증

## 제약 조건

- 시작 시 staged·unstaged·untracked 변경 없음.
- 조회된 API 함수 수는 endpoint 개수가 아니다. 같은 endpoint를 감싼 별도 함수는 각각 센다.
- 코드와 실제 호출 경로의 정적 조사이며 서비스 정책이나 서버 구현의 정확성을 판단하지 않는다.

## 스킬 및 역할

- 역할: inject로 확인된 logic
- 역할 판단 근거: API와 hook의 소비 경로 조사
- 사용자 역할 확인: inject role로 대체
- 사용자 요청: “지금 구현된 도메인 API들에서 ui에 연결되지 않은 것들 확인해봐”
- 승인할 Git 작업: 없음
- 산출물 책임: owner
- 적용 스킬: policy-task-role-routing, policy-git-branch-strategy, policy-documentation

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 현재 worktree의 API 정의와 public export를 rg로 조사 | logic | task-role-routing | 도메인별 API 목록 |
| hook·controller·라우터와 API 호출부 대조 | logic | task-role-routing | UI 연결과 미연결 구분 |
| 자기 세션 경로에 근거 기록 | logic | documentation | 함수별 조사 결과 |

## 검증

- git status --short, git branch --show-current, git rev-parse HEAD, git worktree list --porcelain
- rg --files 및 rg -n으로 API 정의, singleton·factory 참조, hook 사용처, 라우터 조회
- 관련 파일을 cat·sed로 읽어 호출 경로 확인
- 초기 현황 조사에서는 코드 변경이 없으므로 lint·build·test 및 포맷은 실행하지 않는다. 후속 패턴 비교의 기존 테스트 실행은 아래 추가 범위를 따른다.

## 위험 요소 및 결정 사항

- hook 내부에 API 참조가 있어도 hook 또는 반환 함수의 실제 소비자가 없으면 UI 미연결로 분류한다.
- 개발 환경의 MSW 연결 여부와 UI 호출 경로 존재 여부를 구분한다.
- 가상오피스 DTO만으로 HTTP API 구현이 존재한다고 간주하지 않는다.

## 승인

- 읽기 전용 조사는 현재 사용자 요청으로 수행한다.
- 초기 조사 승인에는 애플리케이션 구현과 Git 변경이 포함되지 않았다. 후속 소포 구현 승인은 아래에 기록하며 Git 변경은 수행하지 않는다.

## 후속 비교 조사

- 사용자 추가 요청: 기존 proposal/vote의 UI·Logic 연결성과 미연결 Logic 구현 패턴 비교.
- 동일 worktree와 HEAD에서 조회·변경·parser·Query key·취소·캐시·controller/view 경계를 대조한다.
- data-fetch-layer와 recipe-data-fetch를 추가 적용한다.
- 기존 계약·Query/mutation 테스트 8개 파일을 실행해 상태와 캐시 동작을 확인한다.
- 코드 수정 없이 exploration.md에 패턴의 공통점·차이와 확인이 필요한 계약을 기록한다.

## 후속 구현: 소포 API Logic

- 사용자 요청: 기존 proposal/vote 및 현대화된 도메인 API 패턴에 맞춰 소포 목록 조회·발송·엑셀 다운로드 Logic을 구현한다.
- 역할과 작업 위치: 기존 logic 역할, 같은 sy-main과 worktree에서 순차 구현한다. Git 변경은 요청하지 않는다.
- 확정 계약: 발송 body의 title, content, userId, itemId, amount는 모두 필수이며 amount는 1 이상이다. 성공·실패의 JSON 응답은 공용 code/message/data 구조다.
- 엑셀 계약: GET /admin/parcels/export는 선택적인 recipient 쿼리만 받는다. 값이 있으면 닉네임 부분일치 필터, 없으면 전체 발송 내역이다. 요청 body나 업로드 파일은 없고, 응답으로 받은 xlsx를 사용자의 로컬에 다운로드한다.
- 기존 공용 ApiResponseDto, ApiClient, 인증·오류 처리, TanStack Query와 Zod를 재사용한다. 공용 DTO를 중복 생성하지 않는다.
- 예상 diff: src/entities/parcels 아래 API·DTO·parser, query key/options, 발송 mutation 및 다운로드 hook/보조 함수를 추가한다. tests 아래 기존 Node/Vite/MSW 방식으로 계약과 다운로드 동작을 검증한다.
- 목록은 page=1, size=20, size 최대 100, createdAt/id 정렬 조건을 반영한다. 발송 성공 시 소포 목록 캐시를 취소·무효화한다.
- 파일 응답 경계에서 바이너리와 응답 파일명을 처리하고, JSON 오류는 기존 오류 계약을 유지한다. 버튼에서 호출할 hook을 제공하며 페이지·버튼 UI 구현은 이번 logic 범위에 포함하지 않는다.
- 검증: 선택/미입력 recipient 직렬화, 목록 기본값·정렬·빈 결과, 필수 요청값, 발송 후 캐시 갱신, xlsx 응답·파일명·다운로드, JSON 오류와 취소를 확인한다. 수정 후 공통 포맷 트리거와 관련 테스트·lint·build를 실행한다.
- 승인 이력: 최초 DTO 추가는 PreToolUse의 사용자 구현 승인 미등록으로 차단되었다. 이후 사용자가 “작업 진행”으로 위 구현 범위를 승인했다.
- 현재 상태: 승인된 소포 Logic 구현과 계약 테스트를 추가했다. 공용 JSON 처리기를 수정하지 않고 export 요청에만 response transform을 지정하여 파일 응답을 내부 공용 envelope로 정규화한다. DOM 다운로드는 별도 함수로 분리하고 export mutation에서 호출한다.
- 완료: 공통 포맷 적용, 신규 소포 테스트 13개와 기존 관련 테스트 69개 모두 통과, lint·build 통과. 실제 서버 호출과 UI 버튼 연결은 수행하지 않았다.
