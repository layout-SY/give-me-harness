# 구현 로그

## 현재 섹션

- Proposal 목록·상세·처리 수직 슬라이스 구현 완료.
- 공통 mock response·pagination·query·fixture 확장 helper를 추가하고 Proposal에서 실제 동작을 검증했다.

## 진행 원칙

- 한 번에 한 도메인만 구현한다.
- 페이지의 fixture import 제거 여부를 각 섹션에서 구조 검증한다.
- mutation 후 동일 session의 재조회 결과가 변경된 state를 반환해야 한다.

## 구현 결과

- `src/mocks/utils/`: API envelope, table pagination, query 변환, fixture 확장 helper 추가
- `src/entities/cp-proposal/api/`: 목록·상세·처리 DTO, Zod schema/parser, typed `ApiClient` 추가
- `src/entities/cp-proposal/model/`: query key, 목록·상세 query, 처리 mutation 추가
- `src/mocks/cp-proposal.handlers.ts`: 결정적 120건 seed, query 필터, pagination, 상세 404, 처리 session state 구현
- `src/pages/cp-proposal/ui/`: fixture 직접 import 제거, 검색 submit·pagination·route ID·처리 저장 연결
- `src/shared/ui/dropdown/`: generic callback 계약 및 HeroUI `textValue` 접근성 보완
- `src/shared/ui/pagination/`: 좁은 화면에서 문서 폭을 확장하지 않는 내부 수평 스크롤 추가
- 공용 shell/navigation/admin layout: 1079px 이하 navigation 자동 접기, 767px 이하 filter·master-detail·grid 단일 열 전환
- 공용 Table: Enter/Space 행 선택, `aria-selected`, focus-visible 지원
- Proposal 목록 처리: 선택 entity의 저장된 부서를 기본값으로 파생하고 사용자 override를 `proposalId`별 dirty state로 관리
- CJK 문구: 조사·보조용언 고립을 막는 `keep-all` 및 mock 문구 non-breaking phrase 적용
- 상세 의견: 정규화 dirty 비교로 unchanged·revert 저장 차단
- 모바일 Navigation: 닫힌 content에 `inert`·`aria-hidden`을 적용해 탭 순서·접근성 트리에서 격리
