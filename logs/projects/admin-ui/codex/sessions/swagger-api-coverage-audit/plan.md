# 계획

## 목표

2026-09-28에 제공된 Swagger의 전체 API path·method와 요청·응답을 현재 admin-ui 소스에 대조하여 누락, 계약 차이, 화면 연결 상태를 검토한다.

## 작업 유형

audit-only

## 범위

- 작업 위치: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`
- 기준: `sy-main`, `4b0b7db45aa9d15bf918a1a084370594e138a124`, 조사 시작 시 미커밋 변경 없음.
- Swagger UI → swagger-initializer.js → swagger-config → /v3/api-docs 순서로 원본 명세를 확인한다.
- `src/entities/**/api`, `src/shared/api/common`, hook·query/mutation options, 실제 pages/features/widgets와 router, mock 적용 조건을 읽는다.
- 전체 operation 목록과 미구현 요청·응답, 재사용 가능한 연결 패턴, 계약 공백을 기록한다.

## 제외 사항

애플리케이션·패키지 수정, 실제 업무 API 호출, 로그인, 데이터 변경, Git 변경, 브라우저/시각 QA.

## 제약 조건

명세에 없는 endpoint의 서버 존재 여부는 단정하지 않는다. API 함수 정의, hook 존재, 화면 연결, 실제 통신 성공을 구분한다. 과거 확정 계약 주석과 현재 Swagger가 충돌하면 변경 승인으로 해석하지 않는다.

## 스킬 및 역할

- 세션 역할: inject로 확인된 logic.
- 근거: API·DTO·parser·hook·데이터 연결 범위의 기술 조사.
- 적용 스킬: task-role-routing, git-branch-strategy, data-fetch-layer, documentation.
- 승인할 Git 작업: 없음.
- 산출물 책임: owner.
- 사용자 요청 자체가 읽기 전용 검토의 근거이며, 구현 승인은 요청하지 않는다.

| 작업 구간 | 역할 | 방법 | 기대 결과 |
| --- | --- | --- | --- |
| Swagger 명세 수집 | logic | 제공된 서버 문서 GET | 전체 path·method·schema 확보 |
| 저장소 대조 | logic | rg 및 소스 읽기 | 일치 호출과 계약 차이 구분 |
| 연결 상태 조사 | logic | hook·controller·router·mock 참조 추적 | 정의만 있는 API 식별 |
| 결과 기록 | logic | 자기 세션 산출물 작성 | 전체 대조표와 후속 검토 근거 |

## 검증

명세 operation 개수와 대조표 개수를 맞추고, 누락 후보를 src 전체에서 재검색한다. 코드는 변경하지 않으므로 포맷·lint·build 및 테스트는 실행하지 않는다.

## 위험 요소 및 결정 사항

정적 검토 결과이며 실제 서버의 응답·업무 동작을 실행 검증하지 않는다. 공개 schema의 optional/null 표현이나 상세 미기재를 임의 계약으로 보완하지 않는다.

## 승인

읽기 전용 조사는 사용자 요청에 따라 수행한다. 소스 구현 및 Git 작업은 승인·실행하지 않았다.

