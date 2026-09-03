# 계획

## 요청 요약
- T03 Discussion의 완료된 non-UI API/DTO/Zod/query/mutation/stateful MSW 증거를 닫고, 현재 UI diff와 남은 visual 범위를 Claude 소유로 인계한다.

## 작업 유형
- `documentation-only closure`

## 범위
- 기존 Generator/Watcher 증거를 source-confirmed와 runtime-measured로 구분해 인덱싱한다.
- 사용자 소유권 결정 직후의 frozen/dirty baseline을 읽기 전용 Git 상태와 SHA-256으로 고정한다.
- 세션 문서 6개, 동일 slug portfolio, closure 증거 5개를 작성한다.

## 제외 범위
- 제품 코드, 기존 계획/Boulder/ledger, package/lock, 기존 Generator/Watcher 증거의 수정.
- UI 동작·시각 품질·backend compatibility 완료 주장.
- T03 재실행과 UI 상호작용.

## 섹션
1. 측정 증거와 정책/템플릿 확인
2. non-UI 종료 및 Claude 소유권 경계 기록
3. 링크·JSON·frozen baseline·무제품쓰기 검증

## 필요 에이전트
- Documentation worker: 현재 문서 작성.
- Watcher: 기존 independent `confirmed` 결과를 인용하며 역할을 분리.
- Evaluator: 이번 closure에서는 document-only/deferred.

## 필요 스킬
- `policy-documentation`
- `policy-portfolio`
- `git-master`(읽기 전용 status/hash에 한정)

## 리스크 / 가정
- HTTP 계약은 local provisional MSW 계약이며 실제 backend 호환성을 뜻하지 않는다.
- ownership 결정 이전부터 존재한 UI/shared/package dirty diff는 보존 대상이지 이 closure의 변경이 아니다.
- attempt 4는 더 늦은 UI 작업을 포함할 수 있으므로 non-UI 완료 근거로 사용하지 않고 Claude 참고 자료로만 연결한다.

## 승인 근거
- 사용자가 T03 UI diff 보존과 Claude 소유를 명시하고 이 documentation-only closure를 직접 요청했다.
