# 검토 로그

## 상태

- Proposal 섹션 정적 검증과 수동 브라우저 검증 PASS.
- 대체 Watcher 최종 PASS. 지정 Watcher는 Anthropic 크레딧 부족으로 실행 불가.
- 마지막 수정 이후 독립 Visual QA Oracle Pass A·B 모두 PASS.

## 필수 검증

- 대상 ESLint·Vite build
- 실제 브라우저 필터·pagination·상세 ID·mutation
- 잘못된 query/body 및 없는 ID 오류
- fixture 직접 import 제거
- Fresh Visual QA
- Watcher PASS

## 정적 검증

- `npx tsc -b --pretty false`: PASS
- 변경 대상 ESLint: PASS
- `npx vite build`: PASS
- build warning: 기존 단일 chunk 500kB 초과 경고 유지
- LSP: TypeScript/Biome 서버 미설치이며 사용자가 설치를 거절해 CLI 검증으로 대체

## 브라우저 기능 검증

- 최초 목록: `page=1&size=10`, 120건, 상태별 30건
- pagination: 2페이지에서 CP-011부터 노출
- 작성자 검색: `author=홍길동`, 30건·10행 확인
- 상태+제목 검색: `status=RECEIVED&title=시민 제안 샘플`, 접수 30건 확인
- 목록 처리 저장: CP-001 `검토중 → 채택`, POST 후 목록 재조회 반영
- 상세 route: `/cp/proposals/CP-005` ID 응답 확인
- 상세 처리 의견 저장: textarea·처리 이력 즉시 반영
- 오류 계약: 잘못된 query 400, 없는 ID 404, 빈 처리 body 400
- fresh console: errors 0, warnings 0

## Fresh Visual QA

- 목록·상세 각각 375·768·1280px, 총 6개 캡처 생성
- 최초 점검에서 좁은 화면 navigation/layout 붕괴 발견 후 root fix
- 최종 6개 캡처 자체 점검 PASS: 문서 수평 overflow 없음, pagination 내부 스크롤, CJK 클리핑 없음

## 독립 검토 피드백 반영

- 키보드로 Table 행을 선택할 수 없던 문제 수정
- Navigation 아이콘 버튼의 접근 가능한 이름·확장 상태 추가
- 상태 Select와 처리 의견 TextArea의 프로그램적 라벨 연결
- 실제 변경이 없는 process mutation 차단
- 선택 행의 persisted department와 UI 기본값을 동기화하고 사용자 override만 dirty 처리
- `개선을`, `관련 시민`, `위해 제안했습니다`, `검토해 주세요` 의미 단위 줄바꿈 보정
- 대체 Watcher 최신 소스 기준 PASS
- 상세 처리 의견 unchanged·revert 저장 차단
- 모바일 닫힌 Navigation content의 `inert`·`aria-hidden` 및 실제 Tab 격리 확인

## 최종 판정

- Visual QA Pass A: PASS, blockers 없음
- Visual QA Pass B: PASS, blockers 없음
- 대체 Watcher: PASS, blockers 없음
- Proposal 섹션 품질 게이트 통과
