# 구현 로그

## 작업 요약
- 설문조사 템플릿을 패턴이 이미 맞춰진 CP 7슬라이스에 복제했다. `pages`는 `ui`/`hook`/`model`/`lib`, `entities`는 `api`/`model`/`hook`으로 재배치했다. 화면 동작은 바꾸지 않았다.

## 재사용 자산
- 슬라이스 public API(`~/pages/cp-*`, `~/entities/cp-*`)와 pages 루트 `index.ts`의 `./ui/*-page` 재export를 유지했다.
- 공용 CP 목록 추상화 훅은 만들지 않았다.

## 신규 파일 / 수정 파일
- pages: `cp-proposal`, `cp-vote`, `cp-discussion`, `cp-policy`, `cp-comment`, `cp-activity-log`, `cp-dashboard` — `use-*` → `hook/`, `*.types.ts`/`*.config.ts` → `model/`, `*.model.ts` → `lib/`, page/view/css는 `ui/` 유지
- entities: 동일 7슬라이스 + 이미 이동한 `cp-survey` — query/mutation을 `model/`에서 `hook/`으로 이동, 루트 `index.ts` export를 `./hook/`으로 수정
- import 상대경로를 세그먼트 기준으로 재작성했다. `entities/cp-comment/hook/use-cp-comment-process-mutation.ts`의 `./types`는 `../model/types`로 고쳤다.

## 핵심 로직
- 변경 없음. 파일 위치와 import 경로만 세그먼트 계약에 맞췄다.

## 검증 / 요청 처리
- `yarn tsc --noEmit` 통과
- `yarn eslint` 대상 7 pages + 7 entities 통과
- 브라우저 스모크: 대시보드, 제안 목록, 투표 목록/상세, 토론 목록, 정책반영 목록(`정책반영 관리`), 댓글 목록(`댓글 통합 관리`), 활동 로그 목록(`활동 로그`), 사용자 활동 상세(`/cp/activity-logs/users/U-0091`, `사용자 활동 상세`)

## 리스크
- fixture 화면(게시판/신고/메인 노출/보상/운영 정책)과 widget/feature 배럴, 레거시 entity 배럴, cross-entity enum은 이번 범위 밖이다.

## 핸드오프 메모
- 상태: `paused_after_generator`
- Watcher `confirmed` 전 Closure/portfolio 보류
