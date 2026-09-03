# 평가 로그

## 컨텍스트
- portfolio 경험 기록을 선택 문서에서 강제 가능한 완료 산출물로 전환했다.

## 구조적 리스크
- portfolio의 필수 섹션·비공백은 자동 검사할 수 있지만 내용의 사실성은 Watcher evidence 검토에 의존한다.
- 한 저장소에서 동시에 두 작업이 active-session marker를 갱신하는 병렬 실행은 지원하지 않는다.
- 필수 섹션 목록이 policy·hook·test에 중복되어 향후 변경 시 함께 갱신해야 한다.

## 개선 옵션
- P1: portfolio에 대화·테스트·review-log 근거 참조를 더 구조적으로 연결한다.
- P2: 필수 문서·섹션을 단일 manifest/schema에서 관리한다.
- P2: 동일 저장소 병렬 작업이 필요해지면 task ID별 marker namespace를 도입한다.

## 권장 백로그
1. evidence reference 필드의 기계 검증 가능 범위 조사
2. policy/hook/test 상수의 단일 source 검토
3. 병렬 task marker 필요성 측정

## 다음 단계 제안
- 현재 단일 작업 실행 모델에서는 active-session marker를 사용하고 병렬 요구가 생길 때 task ID namespace를 추가한다.
