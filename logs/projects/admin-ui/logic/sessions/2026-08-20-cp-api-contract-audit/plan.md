# 계획

## 요청 요약
- `asan-metaverse-user-ui`의 API 요청·응답, TanStack Query 캐시, mutation 성공 후 캐시 조정, MSW, 로깅 흐름을 기준으로 관리자 시민참여 전체 도메인을 감사한다.
- PDF 관리자 화면 정의와 현재 DTO·parser·mock 계약을 대조해 실서버 연동 수준과 보완 범위를 판정한다.

## 작업 유형
- audit-only

## 범위
- user-ui 시민참여 API 계층과 공용 API 인프라
- admin-ui 시민참여 13개 화면 도메인과 공용 API·MSW 인프라
- `시민참여v_4.8.pdf` p15~p43 관리자 화면 요구사항
- 요청·응답 로깅과 민감 데이터 노출 위험

## 제외 범위
- 페이지 UI의 시각적 품질 재검토
- 승인 전 source code 수정
- PDF에서 확인할 수 없는 실제 backend 명세의 임의 확정

## 섹션
1. user-ui 기준 흐름 정의
2. admin-ui 도메인별 적용 범위 대조
3. PDF 요구사항과 DTO·mock 계약 추적
4. 차단 결함·우선순위·수정 계획 작성

## 필요 에이전트
- Planner: 감사 범위와 기준 정의
- Explore: 두 프로젝트와 PDF 근거 수집
- Watcher: 최종 감사 판정 검토
- Evaluator: 장기 구조 리스크 평가

## 필요 스킬
- `policy-data-fetch-layer`
- `policy-review-checklist`
- `policy-documentation`
- `recipe-data-fetch`
- `recipe-data-dto`
- `reference-components`
- `reference-custom-hooks`

## 리스크 / 가정
- PDF는 UI 화면 정의서이며 backend API 명세가 아니다.
- 원본 PDF가 현재 저장소에 없어 PDF 직접 검증은 차단됐고, `CP_ADMIN_UI_HANDOFF.md`와 화면 모델을 2차 근거로만 사용한다.
- 실제 backend 명세가 없어 현재 endpoint·payload 일부는 임시 계약일 수 있다.
- HTTP 요청·응답 로그와 시민참여 활동 로그 도메인은 별개로 판정한다.
- 감사 기준선은 커밋된 HEAD가 아니라 2026-08-20 현재 작업 트리의 on-disk source다.

## 승인 기록
- 사용자가 전체 구현 흐름 확인을 직접 요청해 audit-only 탐색과 문서화를 진행한다.
- source code 수정은 별도 계획 승인 전 수행하지 않는다.
