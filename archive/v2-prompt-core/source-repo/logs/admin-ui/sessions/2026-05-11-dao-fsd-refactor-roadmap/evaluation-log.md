# 평가 로그

## 컨텍스트
- 작업: DAO 전용 영역에 엄격한 FSD를 도입하기 위한 순차 리팩토링 분석
- 기준선: `dao.api.ts`, `dao.dto.ts`를 도메인 단위 파일로 분해 완료
- 현재 이슈: 작은 단위(파일 내부 의존성)부터 큰 단위(레이어/폴더 의존성)까지 안전하게 이행할 순서 정의

## 구조적 리스크
1. `shared` 성격의 공용 컴포넌트가 `pages/dao`를 역참조하여 레이어 경계가 깨져 있음.
2. DAO 페이지 파일이 조회/상태/변환/액션/모달을 동시에 보유해 변경 영향 반경이 과도하게 큼.
3. 전역 pubsub 이벤트 타입이 DAO 상세 payload까지 포함해 기능 분리 시 결합이 쉽게 재증식할 위험이 큼.

## 왜 중요한가
- FSD는 폴더명이 아니라 의존성 방향이 핵심이며, 현재 구조는 `shared -> page` 역의존이 있어 확장 비용이 급증한다.
- DAO 도메인 기능(Proposal/Audit/Discussion/Pass/Logs)의 page 레벨 비대화는 테스트/리팩터/기능 추가 속도를 모두 저해한다.
- API/DTO 분해를 완료한 지금이 의존성 경계 재설계의 비용 대비 효율이 가장 높은 시점이다.

## 개선 옵션
1. 단계적 전환: 파일 내부 분리 -> shared 순수화 -> entities/features/widgets/pages 레이어 이동
2. 빅뱅 전환: DAO 전체를 한 번에 FSD로 재배치
3. 하이브리드: discussion 등 고변경 영역부터 선행 전환 후 나머지 도메인 확장

## 권장 백로그
1. 파일 내부 분리: page 내부의 search/filter/columns/mutation/modal state를 hook/util/section component로 추출
2. shared 순수화: Table/commonCell의 DAO page 참조 제거, shared contract 타입으로 축소
3. entities/dao 구축: author/status/category/discussion 등 model+ui 경계 확립
4. features/dao 구축: open-detail, moderate, delete 등 유스케이스 단위 액션 캡슐화
5. widgets/dao 구축: page의 대형 화면 블록(table + filter + modal)을 composition 단위로 승격
6. pages/dao 슬림화: route shell + widget 조합만 유지
7. import rule 강제: 레이어 역참조 방지 lint 규칙 적용

## 다음 단계 제안
- Discussion 도메인을 1차 파일 내부 분리 대상(phase-1)으로 선정하고, page 관점 분해 기준(컴포넌트/훅/유틸/이벤트 경계)을 evaluator가 상세 설계한다.

---

## Evaluator 결과 (Discussion 범위)

### 검증된 경로 (2026-05-11)
- `AuthorBadge`: `src/components/author/author-badge.tsx`
- `StatusBadge`: `src/components/status/status-badge.tsx`
- Discussion 색상 유틸: `src/pages/dao/utils/selectColor.ts`
- Discussion 상태 라벨 키 매핑: `src/pages/dao/discuss-posts-management/config/discussion-status-label-key.ts`

### 핵심 진단
1. Discussion 페이지 묶음은 SRP 위반이 크며, 목록/상세/댓글 흐름 각각이 fetch + mapping + mutation + render를 동시에 보유한다.
2. 전역 pubsub 이벤트 계약이 과도한 discussion payload(`rows`, `callback`)를 운반해 결합도를 높인다.
3. shared 경계가 엄격하지 않으며, table row/domain 계약이 shared 성격 경로에 혼재되어 있다.
4. FSD 전환은 shared 승격보다 page-local 계약 분리부터 시작해야 한다.

### 1단계 (파일 내부 분리) 권장 단위
1. `index.tsx`
- `model/search-state.ts` 추출
- `model/map-discussion-post-row.ts` 추출
- `ui/discussion-posts-table-columns.tsx` 추출
- `hooks/use-discussion-posts-table.ts` 추출

2. `detail/_id.modal.tsx`
- `hooks/use-discussion-post-detail-modal.ts` 추출
- `hooks/use-discussion-post-moderation.ts` 추출
- summary/action/banner UI 섹션을 `ui/*`로 추출

3. `proposalPostDetailCommentWidget.tsx`
- `model/comment-row.ts` 추출(flatten/find helper)
- `hooks/use-discussion-comments-table.ts` 추출
- `ui/discussion-comment-table-columns.tsx` 추출

4. `detail/commend/detail/_id.modal.tsx`
- `hooks/use-discussion-comment-detail-modal.ts` 추출

### 2~3단계 (FSD 레이어 이동)
- `pages/dao/discuss-posts-management`: route shell만 유지
- `widgets`: 목록 테이블 / 게시글 상세 모달 / 댓글 테이블
- `features`: 상세 열기, 게시글 숨김/복구, 게시글 삭제, 댓글 삭제
- `entities`: dao-discussion model, dao-author badge, dao-status badge
- `shared`: 도메인 비의존 table/modal/date/format만 유지

### 의존성 규칙 (Page 관점)
- 허용: `page -> widgets/features/entities/shared`
- 금지:
  - `shared`가 DAO DTO 또는 `pages/dao/**`를 import
  - `entities`가 `features/widgets/pages`를 import
  - 전역 pubsub 이벤트가 page row 배열 또는 React callback을 운반

### 즉시 실행 백로그 (순서)
1. `AuthorBadge` 색상 유틸 의존 위치/경로를 1차 게이트로 정리
2. discussion row 계약을 shared table interface 경로 밖으로 이동
3. 목록 페이지 내부(state/mapper/columns/hooks) 분리
4. 게시글 상세 모달 query/mutation hook 분리
5. 댓글 위젯 helper/columns/hooks 분리
6. discussion pubsub payload 계약을 최소 id 중심으로 축소

### 회귀 체크리스트
- 검색/정렬/페이지네이션/리셋 동작
- proposal grouping/head 렌더링
- 게시글 숨김/복구/삭제 + refresh 연쇄
- 댓글 flatten tree 및 상세 모달 조회
- 상태 라벨 키 매핑 정확성
- `yarn lint && npx tsc --noEmit`
