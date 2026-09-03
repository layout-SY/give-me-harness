# 평가 로그

## 컨텍스트
- 비교 감사에서 도출된 첫 correctness 위험을 수정하고 사용자 정정 피드백에 따라 Proposal 목록의 route/page/controller 책임을 data/process 경계까지 분리했다.

## 구조적 리스크
1. Discussion·Vote page는 검색, 선택, mutation, Dialog, navigation, JSX를 계속 함께 소유한다.
2. Proposal의 stale 방어 불변식은 controller로 이동했지만 Discussion·Vote는 page-local 상태다.
3. 기존 반응형 표는 375·768px에서 우측 열이 잘리고 토론 모바일 master 영역에 큰 여백이 있다.
4. Discussion·Vote의 상태 변경 draft는 아직 선택 행 ID에 귀속되지 않아 같은 query key background refetch 경계를 다음 controller 분리에서 점검해야 한다.
5. Proposal은 controller 책임 집중을 해소했지만 Discussion·Vote는 동일한 page-local 집중이 남아 있다.

## 왜 중요한가
- Proposal에서 검증한 search/data/process 경계는 route page와 controller의 변경 이유를 composition으로 제한한다. 동일한 책임 집중은 Discussion·Vote의 다음 우선순위로 남아 있다.

## 개선 옵션
1. Proposal에서 검증한 search/data/process 경계를 Vote의 domain hooks에 적용한다.
2. 기간 검증 규칙을 유지하며 Discussion에 동일 경계를 적용한다.
3. 반응형 표와 기간 입력 줄바꿈은 별도 UI 개선 범위로 분리한다.

## 권장 백로그
1. `useCpVoteListSearchState`와 `useCpVoteListController` 파일럿에서 `useStatusTransition.resetKey`를 선택 ID에 결선한다.
2. Discussion 기간 검증과 상태 draft ID 귀속을 유지한 controller 분리.
3. Proposal 375px 테이블·페이지네이션 클리핑과 사이드바 폭 개선.

## 다음 단계 제안
- Watcher가 현재 변경을 confirmed한 뒤, 별도 사용자 승인으로 Vote 책임 분리를 한 섹션씩 진행한다.
